import torch
import pandas as pd
import wandb
import os
import json
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
proxy_url = "http://127.0.0.1:7890" 

# 为所有HTTP和HTTPS请求设置代理
os.environ['HTTP_PROXY'] = proxy_url
os.environ['HTTPS_PROXY'] = proxy_url

print(f"--- 已为本次运行配置代理: {proxy_url} ---")
# --- 1. 配置与初始化 ---
print("--- 步骤 1: 配置与初始化 (通用 Transformers & TRL 版) ---")

# wandb 配置
WB_TOKEN = "8a3d4548476cfc4c37712a0d0081c7ecdb84616b"
wandb.login(key=WB_TOKEN)

# 训练超参数
training_config = {
    "lora_r": 128,
    "lora_alpha": 256,
    "lora_dropout": 0.05,
    "learning_rate": 2e-4,
    "per_device_train_batch_size": 1, 
    "gradient_accumulation_steps": 8, 
    "max_steps": 250,
    "warmup_steps": 10,
    "logging_steps": 5,
    "save_steps": 50,
}

run = wandb.init(
    project="qwen3-0.6B-catgirl-finetune",
    name="run_vanilla_trl_with_local_model",
    config=training_config
)

# --- 路径定义 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))

BASE_MODEL_PATH = os.path.join(backend_dir, "models", "qwen3-0.6b")
DATA_FILE_PATH = os.path.join(script_dir, "cat.json")
OUTPUT_DIR_PATH = os.path.join(backend_dir, "models", "qwen3-catgirl-lora-checkpoints-vanilla")

# --- 2. 加载模型与Tokenizer ---
print(f"\n--- 步骤 2: 加载本地模型: {BASE_MODEL_PATH} ---")
if not os.path.isdir(BASE_MODEL_PATH):
    raise FileNotFoundError(f"基础模型文件夹未找到! 位于: {BASE_MODEL_PATH}")

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    quantization_config=quantization_config,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# --- PEFT / LoRA 配置 ---
model = prepare_model_for_kbit_training(model)
peft_config = LoraConfig(
    r=run.config.lora_r,
    lora_alpha=run.config.lora_alpha,
    lora_dropout=run.config.lora_dropout,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, peft_config)
print("模型和LoRA适配器加载完成 (通用版)。")

# --- 3. 数据集处理 ---
print(f"\n--- 步骤 3: 加载数据集: {DATA_FILE_PATH} ---")
raw_dataset = load_dataset("json", data_files={"train": DATA_FILE_PATH}, split="train")
def format_cat_data(example):
    return {"conversations": [{"role": "user", "content": example.get("instruction", "")}, {"role": "assistant", "content": example.get("output", "")}]}
formatted_dataset = raw_dataset.map(format_cat_data, remove_columns=raw_dataset.column_names)
def template_dataset(examples):
    return {"text": tokenizer.apply_chat_template(examples["conversations"], tokenize=False)}
train_dataset = formatted_dataset.map(template_dataset, remove_columns=formatted_dataset.column_names).shuffle(seed=42)
print(f"数据集处理完成，共 {len(train_dataset)} 条数据。")

# --- 4. 配置并开始训练 ---
print(f"\n--- 步骤 4: 开始训练，检查点将保存至: {OUTPUT_DIR_PATH} ---")
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=train_dataset,
    dataset_text_field="text", max_seq_length=2048, peft_config=peft_config,
    args=TrainingArguments(
        per_device_train_batch_size=run.config.per_device_train_batch_size,
        gradient_accumulation_steps=run.config.gradient_accumulation_steps,
        max_steps=run.config.max_steps, learning_rate=run.config.learning_rate,
        warmup_steps=run.config.warmup_steps, logging_steps=run.config.logging_steps,
        save_strategy="steps", save_steps=run.config.save_steps,
        optim="paged_adamw_8bit", weight_decay=0.01,
        lr_scheduler_type="linear", seed=42,
        output_dir=OUTPUT_DIR_PATH, report_to="wandb",
    )
)
trainer.train()
print("训练完成！")

# --- 5. 生成测试样本 ---
print("\n--- 步骤 5: 生成并保存测试样本 ---")
golden_prompts = ["你好", "你叫什么名字？", "今天天气怎么样", "讲个笑话", "我有点难过，可以安慰我一下吗？"]
results = {}
checkpoints = sorted([d for d in os.listdir(OUTPUT_DIR_PATH) if d.startswith("checkpoint-")])
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH, quantization_config=quantization_config, device_map="auto"
)

for model_id in ["base"] + checkpoints:
    print(f"正在使用 '{model_id}' 模型生成回答...")
    current_model = base_model
    if model_id != "base":
        current_model = PeftModel.from_pretrained(base_model, os.path.join(OUTPUT_DIR_PATH, model_id))
        current_model = current_model.merge_and_unload()

    results[model_id] = {}
    for prompt in golden_prompts:
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        
        with torch.inference_mode():
            outputs = current_model.generate(**inputs, max_new_tokens=128, use_cache=True)
        
        response = tokenizer.batch_decode(outputs)[0]
        
        try:
            assistant_response = response.split("<|im_start|>assistant\n")[1].split("<|im_end|>")[0].strip()
        except IndexError:
            assistant_response = "[模型未能生成有效回复]"
        results[model_id][prompt] = assistant_response

predictions_path = os.path.join(script_dir, "golden_predictions_vanilla.json")
with open(predictions_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"所有测试样本已生成并保存到: {predictions_path}")
wandb.finish()
print("\n微调流程和数据采集全部完成！")