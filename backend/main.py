import torch
import json
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import transformer_trainer as tt
from rag_pipeline import  rerank_only,retrieve_only
# --- 核心修改：导入新的、分离的服务实例和函数 ---
from model_server import get_tokenizer,llm_basics_server, sft_model_provider,sft_server
import logging
# --- FastAPI 应用和CORS配置 ---
app = FastAPI(
  title="LLM Explorer Backend",
  description="API server for the LLM Explorer application, providing model inference and other services.",
  version="1.0.0"
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 为了方便开发，允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 数据模型定义 (Request/Response Models) ---
class RagQueryRequest(BaseModel):
    query: str
class TokenizeRequest(BaseModel):
    text: str
class RerankRequest(BaseModel):
    query: str
    documents: List[Dict[str, Any]]

class GenerationRequest(BaseModel):
    query: str
    context: str
class TrainRequest(BaseModel):
    components: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
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
class PromptEngRequest(BaseModel):
    prompt: str
# --- API 路由定义 ---

@app.get("/")
def read_root():
    return {"message": "LLM Explorer Backend is running"}

# --- SFT 页面相关API (从原始 main.py 中恢复) ---
@app.post("/api/sft/visualizer_tokenize")
async def visualizer_tokenize(request: TokenizeRequest):
    """
    专门为SFT可视化器提供的Tokenize端点。
    使用 .tokenize() 方法来正确地将文本转换为Token字符串列表，
    以解决单ID解码不准确的问题。
    """
    try:
        tokenizer = get_tokenizer()
        # .tokenize() 直接返回模型实际处理的Token字符串列表
        tokens = tokenizer.tokenize(request.text)
        # 然后再将这些正确的Token字符串转换为ID
        token_ids = tokenizer.convert_tokens_to_ids(tokens)
        return {"tokens": tokens, "token_ids": token_ids}
    except Exception as e:
        logger.error(f"Visualizer Tokenize 发生错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Tokenization for visualizer failed.")

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
@app.post("/api/transformer/train")
async def train_transformer_model(request: TrainRequest):
    logger.info("Received Transformer training request")
    try:
        # 1. 解析前端发来的模型结构配置
        config = {}
        encoder_blocks = [c for c in request.components if c['type'] == 'encoder_block']
        decoder_blocks = [c for c in request.components if c['type'] == 'decoder_block']

        config['num_encoder_layers'] = len(encoder_blocks)
        config['num_decoder_layers'] = len(decoder_blocks)
        
        if not encoder_blocks or not decoder_blocks:
            return {"status": "error", "logs": ["模型结构不完整，必须同时包含编码器和解码器块。"]}

        # 使用第一个编码器块的参数作为全局参数
        config['heads'] = encoder_blocks[0]['params']['heads']
        config['ff_dim'] = encoder_blocks[0]['params']['ff_dim']

        embedding_layer = next((c for c in request.components if c['type'] == 'embedding'), None)
        config['embed_dim'] = embedding_layer['params']['embed_dim'] if embedding_layer else 512
        
        logger.info(f"Parsed model config: {config}")

        # 2. 设定数据集的准确路径
        # 该路径是相对于项目根目录（即 start_server.bat 所在的位置）
        data_path = os.path.join("backend", "dldemos", "Transformer", "data")
        
        # 增加路径检查，提供更明确的错误信息
        if not os.path.exists(os.path.join(data_path, 'train.cn')):
             return {"status": "error", "logs": [f"错误：在路径 '{data_path}' 下找不到 train.cn 文件。", "请确认已将 cn.txt 和 en.txt 分别重命名为 train.cn 和 train.en。"]}

        # 3. 调用我们最终版的训练流程
        logs = tt.start_training_process(config, data_path)
        
        return {"status": "Training complete", "logs": logs}

    except Exception as e:
        logger.error(f"An error occurred during transformer training: {e}", exc_info=True)
        return {"status": "error", "logs": [f"API层出现严重错误: {e}", "请检查后端控制台以获取详细的追溯信息。"]}

@app.post("/api/rag/retrieve")
async def handle_rag_retrieve(request: RagQueryRequest):
    """
    接收用户问题，只执行向量检索并返回初步结果。
    """
    try:
        retrieval_results = retrieve_only(request.query)
        return retrieval_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/rerank")
async def handle_rag_rerank(request: RerankRequest):
    """
    接收初步检索结果和问题，执行重排序并返回精排结果。
    """
    try:
        rerank_results = rerank_only(request.query, request.documents)
        return rerank_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/generate")
async def handle_rag_generate(request: GenerationRequest):
    """
    接收最终的上下文和问题，调用LLM生成答案。
    """
    try:
        prompt_template = f"""
        请严格根据以下【参考资料】，简洁、准确、专业地回答用户的问题。”。

        【参考资料】:
        {request.context}

        ---
        【用户的问题】:
        {request.query}

        【你的回答】:
        """
        model = sft_model_provider("base")
        tokenizer = get_tokenizer()
        messages = [{"role": "user", "content": prompt_template}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            outputs = model.generate(
                **inputs, max_new_tokens=512, temperature=0.1, top_p=0.9,
                do_sample=True, pad_token_id=tokenizer.eos_token_id
            )
        response_ids = outputs[0][inputs.input_ids.shape[1]:]
        final_answer = tokenizer.decode(response_ids, skip_special_tokens=True)
        return {"final_answer": final_answer.strip(), "final_prompt": prompt_template}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- Prompt Engineering 页面 API (核心修改) ---
@app.post("/api/prompt-eng-judge")
async def judge_prompt(request: PromptEngRequest):
    """
    接收用户的Prompt，调用qwen3-0.6b模型生成邮件，并根据Prompt本身评分。
    """
    user_prompt = request.prompt
    
    # 1. 根据用户Prompt的关键词进行评分 (简易逻辑保持不变)
    score = 30
    feedback = '评分较低。提示词可能不够清晰，导致邮件格式或内容有欠缺。'
    
    prompt_lower = user_prompt.lower()
    if '邮件' in prompt_lower and ('邀请' in prompt_lower or '通知' in prompt_lower): score += 20
    if '专业' in prompt_lower or '正式' in prompt_lower: score += 15
    if '角色' in prompt_lower or '扮演' in prompt_lower: score += 10
    if '简洁' in prompt_lower or '清晰' in prompt_lower: score += 5
    if '格式' in prompt_lower or '标题' in prompt_lower: score += 10
    
    if score >= 80:
        feedback = '非常棒的Prompt！清晰、具体，包含了角色、任务和风格要求，能生成高质量的邮件。'
    elif score >= 50:
        feedback = '不错的尝试！Prompt提供了基本信息，但可以更具体，比如指定语气或格式。'

    # 2. 构建发送给真实模型的完整指令
    # 我们将任务背景和用户的Prompt结合起来
    full_prompt_to_model = f"""
    你是一名专业的行政助理。
    请根据以下要点，撰写一封会议邀请邮件：
    - 会议主题：第二季度产品规划
    - 时间：下周三下午2点
    - 地点：301会议室
    - 参会人：产品部、研发部负责人

    现在，请严格按照用户的以下指示来生成这封邮件：
    ---
    用户指示："{user_prompt}"
    ---
    你的邮件内容：
    """

    # 3. 调用 qwen3-0.6b 模型生成邮件内容
    try:
        model = sft_model_provider("base")
        tokenizer = get_tokenizer()

        messages = [{"role": "user", "content": full_prompt_to_model}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256, # 邮件内容不需要太长
                temperature=0.7,   # 允许一定的创造性
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response_ids = outputs[0][inputs.input_ids.shape[1]:]
        model_output = tokenizer.decode(response_ids, skip_special_tokens=True).strip()

    except Exception as e:
        print(f"调用模型时发生错误: {e}")
        raise HTTPException(status_code=500, detail="模型生成内容时发生错误。")


    return {"score": score, "feedback": feedback, "output": model_output}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)