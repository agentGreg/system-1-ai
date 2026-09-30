#!/bin/bash
# Full 30-item runs for all chat/completions systems, sequential (one call in flight at a time).
set -u
cd "$(dirname "$0")"
run(){ python3 run_cloud.py --model "$1" --reasoning="$2" --label "$3" --out "raw_$4.jsonl" > "log_$4.txt" 2>&1; tail -1 "log_$4.txt"; }
run openai/gpt-6-luna "" "GPT-6 Luna (direct, default reasoning)" gpt-6-luna
run deepseek/deepseek-v4.1-flash "" "DeepSeek V4.1 Flash (direct, default reasoning)" deepseek-v4.1-flash
run anthropic/claude-sonnet-5.5 '{"effort":"medium"}' "Claude Sonnet 5.5, reasoning effort medium" sonnet-5.5_medium
run anthropic/claude-sonnet-5.5 '{"effort":"minimal"}' "Claude Sonnet 5.5, reasoning effort minimal" sonnet-5.5_minimal
run openai/gpt-6.1-sol '{"effort":"medium"}' "GPT-6.1 Sol, reasoning effort medium" gpt-6.1-sol_medium
run openai/gpt-6.1-sol '{"effort":"minimal"}' "GPT-6.1 Sol, reasoning effort minimal" gpt-6.1-sol_minimal
run google/gemini-3.8-flash '{"effort":"medium"}' "Gemini 3.8 Flash, thinking effort medium" gemini-3.8-flash_medium
run openai/gpt-6.1-sol '{"effort":"high"}' "GPT-6.1 Sol, reasoning effort high" gpt-6.1-sol_high   # added after Sonnet showed no reasoning
