"""Shared helpers: load the test set, describe the hardware, write results."""
import json
import platform
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATEGORY = {"R": "reklamacja", "D": "routing", "E": "eskalacja", "K": "kompletnosc"}


def load_items(path=HERE / "decisions.jsonl"):
    items = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    for it in items:
        it["category"] = CATEGORY[it["id"][0]]
    return items


def hardware():
    def sysctl(k):
        return subprocess.run(["sysctl", "-n", k], capture_output=True, text=True).stdout.strip()
    return {"chip": sysctl("machdep.cpu.brand_string"),
            "ram_gb": int(sysctl("hw.memsize")) // 2**30,
            "macos": platform.mac_ver()[0], "python": platform.python_version()}


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
