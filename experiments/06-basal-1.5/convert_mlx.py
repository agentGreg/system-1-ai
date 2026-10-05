"""MLX conversions of a basal-1.5 model in the layout of Remek's own MLX ports (Remek/basal-1.5-*-MLX-8bit).

Decoder layers: MLX affine quantization (a bf16 scale and bias per group). The token embeddings and the output head
stay in bf16, because the decision is read from the output head's logits of the option letters.
Variants:
  bf16           plain MLX copy of the bf16 weights (no quantization)
  <b>bit         affine b-bit, group 64, e.g. 4bit, 6bit
  <b>bit-g<n>    affine b-bit, group n, e.g. 4bit-g32
  mixed-4-6      mlx_lm's mixed_4_6 recipe (llama.cpp Q4_K_M-like: v_proj and down_proj at 6 bits in the first and
                 last eighth of the layers and every third layer between, the rest at 4 bits, group 64), except that
                 the embeddings and the output head stay in bf16 (mlx_lm would put the head at 6 bits)
The basal files the engine needs (CALIBRATION.json, basal.json, chat_template.jinja) are copied next to the weights.

usage: python convert_mlx.py --model Remek/basal-1.5-mini --variants 4bit 6bit bf16 --out ~/models/basal-mlx
"""
import argparse
import json
import re
import shutil
from pathlib import Path

from huggingface_hub import snapshot_download
from mlx_lm import convert

KEEP_BF16 = ("embed_tokens", "lm_head")
BASAL_FILES = ("CALIBRATION.json", "basal.json", "chat_template.jinja", "generation_config.json")


def decoder_only(path, module, config=None):
    return hasattr(module, "to_quantized") and not any(k in path for k in KEEP_BF16)


def mixed_4_6(num_layers, group_size=64):
    def pred(path, module, config=None):
        if not decoder_only(path, module):
            return False
        m = re.search(r"layers\.(\d+)\.", path)
        i = int(m.group(1)) if m else 0
        more = i < num_layers // 8 or i >= 7 * num_layers // 8 or (i - num_layers // 8) % 3 == 2
        bits = 6 if more and ("v_proj" in path or "down_proj" in path) else 4
        return {"group_size": group_size, "bits": bits, "mode": "affine"}
    return pred


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Remek/basal-1.5-mini")
    ap.add_argument("--variants", nargs="+", default=["4bit", "6bit", "bf16"])
    ap.add_argument("--out", default=str(Path.home() / "models/basal-mlx"))
    a = ap.parse_args()

    src = Path(snapshot_download(a.model))
    name = a.model.split("/")[-1]
    n_layers = json.loads((src / "config.json").read_text())["num_hidden_layers"]
    for v in a.variants:
        dst = Path(a.out).expanduser() / f"{name}-MLX-{v}"
        if dst.exists():
            shutil.rmtree(dst)
        if v == "bf16":
            convert(str(src), str(dst), dtype="bfloat16")
        elif v == "mixed-4-6":
            convert(str(src), str(dst), quantize=True, q_bits=4, q_group_size=64, q_mode="affine",
                    dtype="bfloat16", quant_predicate=mixed_4_6(n_layers))
        else:
            m = re.fullmatch(r"(\d)bit(?:-g(\d+))?", v)
            bits, gs = int(m.group(1)), int(m.group(2) or 64)
            convert(str(src), str(dst), quantize=True, q_bits=bits, q_group_size=gs, q_mode="affine",
                    dtype="bfloat16", quant_predicate=decoder_only)
        for f in BASAL_FILES:
            if (src / f).exists():
                shutil.copy2(src / f, dst / f)
        # the base config has the transformers-5 form rope_parameters={"rope_theta": 1e6}; mlx_lm 0.31 reads only a
        # top-level rope_theta and otherwise silently uses 10000 (wrong positions, |dp| up to 0.3 vs PyTorch bf16)
        cfg_path = dst / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["rope_theta"] = cfg.get("rope_parameters", {}).get("rope_theta", cfg.get("rope_theta"))
        cfg_path.write_text(json.dumps(cfg, indent=4))
        print(f"{v}: {dst}  {sum(p.stat().st_size for p in dst.glob('*.safetensors')) / 1e9:.2f} GB", flush=True)


if __name__ == "__main__":
    main()
