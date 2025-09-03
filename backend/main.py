import torch
import json
import os
import re
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

# --- 核心修改：直接导入 model_server 的单例 ---
from model_server import model_server_instance

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

# 用于 /api/tokenize 的模型
class TokenizeRequest(BaseModel):
    text: str

# 用于 /api/predict_next 的模型
class PredictRequest(BaseModel):
    text: str
    top_k: int = 5

# 用于 /api/chat 的模型
class ChatRequest(BaseModel):
    prompt: str
    model_id: str = Field(..., description="模型ID, e.g., 'base', 'checkpoint-50'")

# --- 新增：用于 /api/get_embeddings 的模型 ---
class EmbeddingRequest(BaseModel):
    words: List[str]

# --- 新增：用于 /api/get_attention 的模型 ---
class AttentionRequest(BaseModel):
    text: str
    layer: int = 0
    head: int = 0


# --- API 路由定义 ---

@app.get("/")
def read_root():
    return {"message": "后端服务连接成功! Hello from FastAPI!"}

# --- SFT 页面相关API (保持不变) ---
@app.get("/api/sft/golden_predictions")
def get_golden_predictions():
    file_path = os.path.join(os.path.dirname(__file__), "sft", "cat_sft", "golden_predictions_vanilla.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="golden_predictions_vanilla.json 文件未找到")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/sft/training_logs")
def get_training_logs():
    try:
        script_dir = os.path.dirname(__file__)
        csv_path = os.path.join(script_dir, "sft", "cat_sft", "wandb", "run-20250828_175844-bicdaw19", "files", "wandb_history_data.csv")
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail=f"CSV日志文件未找到: {csv_path}")
        df = pd.read_csv(csv_path)
        logs_df = df[['train/global_step', 'train/loss', 'train/learning_rate']].copy()
        logs_df.rename(columns={
            'train/global_step': 'step',
            'train/loss': 'loss',
            'train/learning_rate': 'learning_rate'
        }, inplace=True)
        logs_df.dropna(inplace=True)
        logs_df['step'] = logs_df['step'].astype(int)
        return logs_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取训练日志失败: {str(e)}")

# --- Chat 页面API ---
@app.post("/api/chat")
def chat_with_model(request: ChatRequest):
    try:
        # --- 核心修改：使用 model_server_instance ---
        tokenizer = model_server_instance.tokenizer
        model = model_server_instance.get_model_for_inference(request.model_id)
        
        messages = [{"role": "user", "content": request.prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        
        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=256, use_cache=True)
        
        response_text = tokenizer.batch_decode(outputs)[0]
        
        try:
            assistant_response_raw = response_text.split("<|im_start|>assistant\n")[1].split("<|im_end|>")[0].strip()
            assistant_response_clean = re.sub(r"<think>.*?</think>", "", assistant_response_raw, flags=re.DOTALL).strip()
        except IndexError:
            assistant_response_clean = "[模型未能生成有效回复]"
            
        return {"reply": assistant_response_clean}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- LLM Basics 页面API ---

@app.post("/api/tokenize")
def tokenize_text(request: TokenizeRequest):
    # --- 核心修改：使用 model_server_instance ---
    tokenizer = model_server_instance.tokenizer
    token_ids = tokenizer.encode(request.text)
    # 修正：返回 tokens 和 ids 以便前端使用
    tokens = [tokenizer.decode([token_id]) for token_id in token_ids]
    return {"tokens": tokens, "token_ids": token_ids}

@app.post("/api/predict_next")
def predict_next_token(request: PredictRequest):
    # --- 核心修改：使用 model_server_instance ---
    tokenizer = model_server_instance.tokenizer
    model = model_server_instance.get_model_for_inference("base") # 基础功能固定使用base model
    
    inputs = tokenizer(request.text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs)
    
    next_token_logits = outputs.logits[:, -1, :]
    probabilities = torch.softmax(next_token_logits, dim=-1)
    top_k_probs, top_k_indices = torch.topk(probabilities, request.top_k)
    
    top_k_probs = top_k_probs.cpu().flatten().tolist()
    top_k_indices = top_k_indices.cpu().flatten().tolist()
    top_k_tokens = [tokenizer.decode([idx]) for idx in top_k_indices] # decode出来可能带空格，前端处理
    
    predictions = [{"token": token, "probability": round(prob * 100, 2)} for token, prob in zip(top_k_tokens, top_k_probs)]
    return {"predictions": predictions}

# --- 新增：LLM Basics 页面API ---

@app.post("/api/get_embeddings")
async def get_embeddings(request: EmbeddingRequest):
    try:
        # --- 核心修改：使用 model_server_instance ---
        result = model_server_instance.get_embeddings(request.words)
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get_attention")
async def get_attention(request: AttentionRequest):
    try:
        # --- 核心修改：使用 model_server_instance ---
        result = model_server_instance.get_attention(request.text, request.layer, request.head)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))