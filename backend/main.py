import torch
import json
import os
import glob
import re # 导入正则表达式库
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import ast
import model_server

# --- FastAPI 应用和CORS配置 (保持不变) ---
app = FastAPI()
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 模型定义 ---
class TokenizeRequest(BaseModel):
    text: str

class PredictRequest(BaseModel):
    text: str
    top_k: int = 5

class ChatRequest(BaseModel):
    prompt: str # 只接收一个字符串 prompt
    model_id: str = Field(..., description="模型ID, e.g., 'base', 'checkpoint-50'")

# --- API 路由定义 ---

@app.get("/")
def read_root():
    return {"message": "后端服务连接成功! Hello from FastAPI!"}
@app.get("/api/sft/golden_predictions")
def get_golden_predictions():
    """读取并返回 golden_predictions.json 的内容"""
    file_path = os.path.join(os.path.dirname(__file__), "sft", "cat_sft", "golden_predictions_vanilla.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="golden_predictions_vanilla.json 文件未找到")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/sft/training_logs")
def get_training_logs():
    # 【核心修正】读取 output.log 文件并从中解析数据
    try:
        script_dir = os.path.dirname(__file__)
        wandb_base_dir = os.path.join(script_dir, "sft", "cat_sft", "wandb")
        
        run_dirs = [d for d in os.listdir(wandb_base_dir) if d.startswith("run-") and os.path.isdir(os.path.join(wandb_base_dir, d))]
        if not run_dirs:
            raise FileNotFoundError("在wandb目录下未找到任何 run-* 文件夹")
            
        latest_run_dir = max(run_dirs, key=lambda d: os.path.getmtime(os.path.join(wandb_base_dir, d)))
        
        # 将目标文件指向 output.log
        log_file_path = os.path.join(wandb_base_dir, latest_run_dir, "files", "output.log")
        
        if not os.path.exists(log_file_path):
             raise FileNotFoundError(f"在最新的运行目录 {latest_run_dir} 中未找到 output.log 文件")

        print(f"--- 成功定位到日志文件: {log_file_path}")
        
        logs = []
        with open(log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                # 查找包含 loss 和 learning_rate 的日志行
                if "'loss':" in line and "'learning_rate':" in line:
                    try:
                        # 找到行中字典字符串的开始和结束位置
                        start_index = line.find('{')
                        end_index = line.rfind('}') + 1
                        dict_str = line[start_index:end_index]
                        
                        # 使用 ast.literal_eval 安全地将字符串转换为字典
                        log_entry = ast.literal_eval(dict_str)
                        
                        if "loss" in log_entry and "step" in log_entry:
                            logs.append({
                                "step": log_entry.get("step"),
                                "loss": log_entry.get("loss"),
                                "learning_rate": log_entry.get("learning_rate"),
                            })
                    except (ValueError, SyntaxError):
                        # 如果某一行解析失败，就跳过
                        continue
        return logs
    except Exception as e:
        print(f"--- 读取wandb日志时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"读取训练日志失败: {str(e)}")
@app.post("/api/chat")
def chat_with_model(request: ChatRequest):
    tokenizer = model_server.get_tokenizer()
    model = model_server.get_model_for_inference(request.model_id)
    
    # 【核心修改】构建单轮对话输入
    messages = [{"role": "user", "content": request.prompt}]
    
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    
    with torch.inference_mode():
        outputs = model.generate(**inputs, max_new_tokens=256, use_cache=True)
    
    response_text = tokenizer.batch_decode(outputs)[0]
    
    try:
        assistant_response_raw = response_text.split("<|im_start|>assistant\n")[1].split("<|im_end|>")[0].strip()
        
        # 【核心修改】使用正则表达式移除 <think> 标签块
        assistant_response_clean = re.sub(r"<think>.*?</think>", "", assistant_response_raw, flags=re.DOTALL).strip()
        
    except IndexError:
        assistant_response_clean = "[模型未能生成有效回复]"
        
    return {"reply": assistant_response_clean}
@app.post("/api/tokenize")
def tokenize_text(request: TokenizeRequest):
    tokenizer = model_server.get_tokenizer()
    token_ids = tokenizer.encode(request.text)
    tokens = [tokenizer.decode([token_id]) for token_id in token_ids]
    return {"tokens": tokens}

@app.post("/api/predict_next")
def predict_next_token(request: PredictRequest):
    tokenizer = model_server.get_tokenizer()
    # 【核心修正】调用正确的函数名，并明确指定使用基础模型
    model = model_server.get_model_for_inference("base")
    inputs = tokenizer(request.text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)
    next_token_logits = outputs.logits[:, -1, :]
    probabilities = torch.softmax(next_token_logits, dim=-1)
    top_k_probs, top_k_indices = torch.topk(probabilities, request.top_k)
    top_k_probs = top_k_probs.cpu().flatten().tolist()
    top_k_indices = top_k_indices.cpu().flatten().tolist()
    top_k_tokens = [tokenizer.decode([idx]).strip() for idx in top_k_indices]
    predictions = [{"token": token, "probability": round(prob * 100, 2)} for token, prob in zip(top_k_tokens, top_k_probs)]
    return {"predictions": predictions}