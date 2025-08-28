import torch
import json
import os
import glob
import re # 导入正则表达式库
import pandas as pd # 导入 pandas 库
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
    """从 wandb_history_data.csv 读取日志用于可视化"""
    try:
        # 【核心修改】直接定位到指定的CSV文件
        script_dir = os.path.dirname(__file__)
        csv_path = os.path.join(script_dir, "sft", "cat_sft", "wandb", "run-20250828_175844-bicdaw19", "files", "wandb_history_data.csv")

        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail=f"CSV日志文件未找到: {csv_path}")

        print(f"--- 成功定位到日志文件: {csv_path}")

        # 使用 pandas 读取 CSV
        df = pd.read_csv(csv_path)

        # 筛选和重命名列以匹配前端期望的格式
        # 前端需要 'step', 'loss', 'learning_rate'
        # CSV 中对应的列是 'train/global_step', 'train/loss', 'train/learning_rate'
        logs_df = df[['train/global_step', 'train/loss', 'train/learning_rate']].copy()
        logs_df.rename(columns={
            'train/global_step': 'step',
            'train/loss': 'loss',
            'train/learning_rate': 'learning_rate'
        }, inplace=True)

        # 去除包含 NaN 值的行，确保数据干净
        logs_df.dropna(inplace=True)

        # 将 step 列转换为整数类型，确保 Echarts 能正确处理
        logs_df['step'] = logs_df['step'].astype(int)

        # 将DataFrame转换为前端期望的字典列表格式
        logs = logs_df.to_dict(orient='records')

        return logs

    except Exception as e:
        print(f"--- 读取wandb CSV日志时发生错误: {e}")
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