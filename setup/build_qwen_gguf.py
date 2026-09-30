"""
build_qwen_gguf.py — Merge the AgriVision LoRA into Qwen2.5-1.5B-Instruct and
export a single GGUF file usable by Ollama (local) and llama.cpp server (deploy).

Steps:
  1. base (Qwen/Qwen2.5-1.5B-Instruct, downloaded once) + LoRA -> merged HF model
  2. merged HF model -> GGUF (Q8_0 by default: ~1.6GB, near-lossless for 1.5B)

Usage:
  .venv/bin/python setup/build_qwen_gguf.py [--outtype q8_0|f16|bf16]

Outputs (git-ignored, under models_cache/llm/):
  agrivision-qwen-merged/            merged HF weights
  agrivision-qwen-1.5b-<outtype>.gguf
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LLM_DIR = ROOT / "models_cache" / "llm"
ADAPTER_DIR = LLM_DIR / "agrivision-qwen-lora"
MERGED_DIR = LLM_DIR / "agrivision-qwen-merged"
LLAMA_CPP_DIR = LLM_DIR / "_llama.cpp"
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def merge() -> None:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[1/2] Loading base {BASE_MODEL} + adapter {ADAPTER_DIR.name}")
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR)
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, dtype=torch.bfloat16)
    if base.get_input_embeddings().weight.shape[0] < len(tokenizer):
        base.resize_token_embeddings(len(tokenizer))
    merged = PeftModel.from_pretrained(base, ADAPTER_DIR).merge_and_unload()

    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(MERGED_DIR, safe_serialization=True)
    tokenizer.save_pretrained(MERGED_DIR)
    print(f"      merged model saved -> {MERGED_DIR}")


def convert(outtype: str) -> Path:
    out = LLM_DIR / f"agrivision-qwen-1.5b-{outtype}.gguf"
    print(f"[2/2] Converting to GGUF ({outtype}) -> {out.name}")
    subprocess.run(
        [sys.executable, str(LLAMA_CPP_DIR / "convert_hf_to_gguf.py"), str(MERGED_DIR),
         "--outfile", str(out), "--outtype", outtype],
        check=True,
        env={**__import__("os").environ, "PYTHONPATH": str(LLAMA_CPP_DIR / "gguf-py")},
    )
    print(f"      done: {out} ({out.stat().st_size / 1e9:.2f} GB)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outtype", default="q8_0", choices=["q8_0", "f16", "bf16"])
    ap.add_argument("--skip-merge", action="store_true", help="reuse an existing merged dir")
    args = ap.parse_args()

    if not args.skip_merge:
        merge()
    convert(args.outtype)


if __name__ == "__main__":
    main()
