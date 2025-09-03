import torch
import json
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# --- 核心修改：导入新的、分离的服务实例和函数 ---
from model_server import llm_basics_server, sft_model_provider,sft_server

# --- FastAPI 应用和CORS配置 ---
app = FastAPI(
  title="LLM Explorer Backend",
  description="API server for the LLM Explorer application, providing model inference and other services.",
  version="1.0.0"
)

# 为了方便开发，允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 数据模型定义 (Request/Response Models) ---

class TokenizeRequest(BaseModel):
    text: str

class EmbeddingsRequest(BaseModel):
    words: List[str]

class AttentionRequest(BaseModel):
    text: str
    layer: int
    head: int

class PredictRequest(BaseModel):
    text: str

class SftRequest(BaseModel):
    model_id: str
    prompt: str
    max_new_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.9
class LossCalculationRequest(BaseModel):
    model_id: str
    context: str
    target_token_id: int
# --- API 路由定义 ---

@app.get("/")
def read_root():
    return {"message": "LLM Explorer Backend is running"}

# --- SFT 页面相关API (从原始 main.py 中恢复) ---

@app.get("/api/sft/golden_predictions")
def get_golden_predictions():
    """从文件加载并返回 SFT 的黄金标准预测。"""
    file_path = os.path.join(os.path.dirname(__file__), "sft", "cat_sft", "golden_predictions_vanilla.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="golden_predictions_vanilla.json 文件未找到")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/sft/training_logs")
def get_training_logs():
    """从文件加载并返回 SFT 的训练日志。"""
    try:
        script_dir = os.path.dirname(__file__)
        csv_path = os.path.join(script_dir, "sft", "cat_sft", "wandb", "run-20250828_175844-bicdaw19", "files", "wandb_history_data.csv")
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail=f"CSV日志文件未找到: {csv_path}")
        df = pd.read_csv(csv_path)
        # 选择并重命名需要的列
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

# --- LLM Basics 页面API ---

@app.post("/api/tokenize")
async def tokenize(request: TokenizeRequest):
    try:
        return llm_basics_server.tokenize(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get_embeddings")
async def get_embeddings(request: EmbeddingsRequest):
    try:
        return llm_basics_server.get_embeddings(request.words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get_attention")
async def get_attention(request: AttentionRequest):
    try:
        return llm_basics_server.get_attention(request.text, request.layer, request.head)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict_next")
async def predict_next(request: PredictRequest):
    try:
        return llm_basics_server.predict_next(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SFT/Chat 页面生成 API ---

@app.post("/api/sft_generate") # URL 保持统一，对应前端的 SftSimulator.vue
async def sft_generate(request: SftRequest) -> Dict[str, Any]:
    try:
        # 使用新的 sft_model_provider 函数来获取模型
        model = sft_model_provider(request.model_id)
        tokenizer = llm_basics_server.tokenizer # 复用 tokenizer

        messages = [{"role": "user", "content": request.prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.inference_mode(): # 使用 inference_mode 替代 no_grad，更适合推理
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # 精确地解码模型生成的新内容
        response_ids = outputs[0][inputs.input_ids.shape[1]:]
        generated_text = tokenizer.decode(response_ids, skip_special_tokens=True)

        return {"reply": generated_text.strip()}
    except Exception as e:
        print(f"Error during SFT generation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during generation: {e}")
@app.post("/api/calculate_loss")
async def calculate_loss(request: LossCalculationRequest):
    """根据上下文和目标 Token，计算指定模型的 Loss。"""
    try:
        return sft_server.calculate_loss(request.model_id, request.context, request.target_token_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)