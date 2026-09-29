"""
finetune_qlora.py — QLoRA fine-tune of the advisory LLM (user-run on a GPU, e.g. Colab T4 16GB).

Base model (recommendation): Qwen/Qwen2.5-1.5B-Instruct — Apache-2.0, fits QLoRA
on a single T4, well-documented chat template in tokenizer_config.json, and small
enough to serve as a quantized GGUF on a cheap CPU VM. Re-confirm license and
availability on the model card before training.

Chat template: NEVER hand-written. Prompts are rendered with
tokenizer.apply_chat_template(), i.e. the template shipped with the base model;
loss is masked to the assistant turn only.

QLoRA: 4-bit NF4 base + double quantization, LoRA r=16/alpha=32/dropout=0.05 on
all attention + MLP projections. Use --no-4bit only if you have >=24GB VRAM.

    pip install -r training/requirements-train.txt
    python -m training.llm.finetune_qlora --base Qwen/Qwen2.5-1.5B-Instruct --out models_cache/llm/agrivision-qwen-lora
Serve (example, vLLM with LoRA):
    vllm serve Qwen/Qwen2.5-1.5B-Instruct --enable-lora --lora-modules agrivision-advisor=models_cache/llm/agrivision-qwen-lora
    -> ADVISORY_BACKEND=local_llm LOCAL_LLM_URL=http://<host>:8000/v1 LOCAL_LLM_MODEL=agrivision-advisor
"""

from __future__ import annotations

from training.paths import MODELS, RESULTS  # noqa: F401

import argparse
import json
from pathlib import Path

DATA = RESULTS / "zone2" / "llm_data"


def load_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def tokenize_example(tok, messages, max_len):
    prompt_ids = tok.apply_chat_template(messages[:-1], add_generation_prompt=True, tokenize=True)
    full_ids = tok.apply_chat_template(messages, tokenize=True)
    full_ids = full_ids[:max_len]
    labels = [-100] * min(len(prompt_ids), len(full_ids)) + full_ids[len(prompt_ids):]
    return {"input_ids": full_ids, "attention_mask": [1] * len(full_ids), "labels": labels[: len(full_ids)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--out", default=str(MODELS / "llm" / "agrivision-qwen-lora"))
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--no-4bit", action="store_true")
    a = ap.parse_args()

    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                              DataCollatorForSeq2Seq, Trainer, TrainingArguments)

    tok = AutoTokenizer.from_pretrained(a.base)
    if tok.chat_template is None:
        raise SystemExit("Base model ships no chat template — pick an instruct model.")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    dtype = torch.bfloat16 if bf16 else torch.float16
    quant = None if a.no_4bit else BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=dtype)
    model = AutoModelForCausalLM.from_pretrained(a.base, quantization_config=quant, torch_dtype=dtype, device_map={"": 0})
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    if quant:
        model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()

    def ds(split):
        return Dataset.from_list([tokenize_example(tok, r["messages"], a.max_len) for r in load_jsonl(DATA / f"sft_{split}.jsonl")])

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=a.out, num_train_epochs=a.epochs, learning_rate=a.lr, per_device_train_batch_size=a.batch,
            per_device_eval_batch_size=a.batch, gradient_accumulation_steps=a.grad_accum, lr_scheduler_type="cosine",
            warmup_ratio=0.05, logging_steps=10, eval_strategy="epoch", save_strategy="epoch",
            load_best_model_at_end=True, metric_for_best_model="eval_loss", save_total_limit=2,
            bf16=bf16, fp16=not bf16 and torch.cuda.is_available(), gradient_checkpointing=True, report_to=[]),
        train_dataset=ds("train"), eval_dataset=ds("val"),
        data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100),
    )
    trainer.train()
    model.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    print(f"Saved LoRA adapter to {a.out}")


if __name__ == "__main__":
    main()
