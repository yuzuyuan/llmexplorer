import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, AutoConfig
from peft import PeftModel
import os
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import math

# --- 路径定义 ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL_PATH = os.path.join(backend_dir, "models", "qwen3-0.6b")
CHECKPOINT_BASE_PATH = os.path.join(backend_dir, "models", "qwen3-catgirl-lora-checkpoints-vanilla")

# --- 资源缓存 ---
base_model_cache = {}
lora_model_cache = {}
tokenizer_cache = None

# --- 独立的 PyTorch 注意力模块 ---
class StandaloneAttention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.q_layer = nn.Linear(hidden_dim, hidden_dim)
        self.k_layer = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, hidden_states):
        q = self.q_layer(hidden_states)
        k = self.k_layer(hidden_states)
        attention_scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.hidden_dim)
        seq_len = k.size(1)
        mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).to(hidden_states.device)
        attention_scores = attention_scores.masked_fill(mask.bool(), float('-inf'))
        return F.softmax(attention_scores, dim=-1)

def get_tokenizer():
    global tokenizer_cache
    if tokenizer_cache is None:
        tokenizer_cache = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
    return tokenizer_cache

def get_base_model():
    global base_model_cache
    if "base" not in base_model_cache:
        config = AutoConfig.from_pretrained(BASE_MODEL_PATH)
        config.output_hidden_states = True
        quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH, config=config, quantization_config=quantization_config,
            torch_dtype=torch.bfloat16, device_map="auto"
        )
        base_model_cache["base"] = model
    return base_model_cache["base"]

def get_model_for_sft_inference(model_id: str = "base"):
    if model_id == "base": return get_base_model()
    if model_id in lora_model_cache: return lora_model_cache[model_id]
    lora_path = os.path.join(CHECKPOINT_BASE_PATH, model_id)
    if os.path.isdir(lora_path):
        base_model = get_base_model()
        lora_model = PeftModel.from_pretrained(base_model, lora_path)
        lora_model.config.output_hidden_states = True
        lora_model_cache[model_id] = lora_model
        return lora_model
    return get_base_model()

def clean_token_for_display(token):
    return token.replace('Ġ', '').replace(' ', ' ').replace('\_', ' ').encode('ascii', 'ignore').decode('ascii').strip()

class LlmBasicsModelServer:
    # ... 此部分代码保持不变 ...
    def __init__(self):
        self.tokenizer = get_tokenizer()
        self.model = get_base_model()
        self.device = self.model.device
        hidden_dim = self.model.config.hidden_size
        self.attention_module = StandaloneAttention(hidden_dim).to(self.device).eval()

    def tokenize(self, text):
        token_ids = self.tokenizer.encode(text)
        tokens = [clean_token_for_display(self.tokenizer.decode([token_id], skip_special_tokens=True)) for token_id in token_ids]
        return {"tokens": [token for token in tokens if token]}

    def get_embeddings(self, words):
        high_dim_vectors = []
        with torch.no_grad():
            for word in words:
                inputs = self.tokenizer(word, return_tensors="pt").to(self.device)
                outputs = self.model(**inputs)
                vector = outputs.hidden_states[-1].to(torch.float32).mean(dim=1).squeeze().cpu().numpy()
                high_dim_vectors.append(vector)
        
        high_dim_vectors = np.array(high_dim_vectors)
        if high_dim_vectors.ndim == 1: 
            high_dim_vectors = np.expand_dims(high_dim_vectors, axis=0)

        n_samples = high_dim_vectors.shape[0]
        perplexity_value = min(30.0, float(n_samples - 1))

        if n_samples > 1:
            tsne = TSNE(n_components=2, perplexity=perplexity_value, random_state=42)
            vectors_2d = tsne.fit_transform(high_dim_vectors)
        else:
            pca = PCA(n_components=2)
            vectors_2d = pca.fit_transform(high_dim_vectors)

        return {"words": words, "vectors": vectors_2d.tolist()}

    def get_attention(self, text, layer, head):
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            outputs = self.model(**inputs)
            if not getattr(outputs, 'hidden_states', None):
                 raise RuntimeError("模型未能输出 'hidden_states'。")
            hidden_states = outputs.hidden_states[-1].to(torch.float32)
            attention_weights = self.attention_module(hidden_states)
            attention_matrix = attention_weights[0].cpu().numpy().tolist()
            tokens = [clean_token_for_display(self.tokenizer.convert_ids_to_tokens([token_id])[0]) for token_id in inputs['input_ids'][0]]
        return {"tokens": tokens, "attention": attention_matrix}

    def predict_next(self, text):
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            outputs = self.model(**inputs)
            predictions = outputs.logits[:, -1, :]
        top_k = torch.topk(predictions, 5, dim=-1)
        top_k_ids = top_k.indices.squeeze().tolist()
        top_k_tokens = [clean_token_for_display(self.tokenizer.decode([idx], skip_special_tokens=True)) for idx in top_k_ids]
        probabilities = torch.nn.functional.softmax(top_k.values, dim=-1).squeeze().cpu().tolist()
        response = []
        for token, prob in zip(top_k_tokens, probabilities):
            if token:
                response.append({"token": token, "probability": round(prob * 100, 2)})
        return {"predictions": response}

class SftModelServer:
    def __init__(self):
        self.tokenizer = get_tokenizer()
        self.loss_fn = nn.CrossEntropyLoss()

    # --- 新增: Loss 计算方法 ---
    def calculate_loss(self, model_id, context, target_token_id):
        model = get_model_for_sft_inference(model_id)
        
        with torch.no_grad():
            # 准备输入
            inputs = self.tokenizer(context, return_tensors="pt").to(model.device)
            
            # 前向传播
            outputs = model(**inputs)
            
            # 获取最后一个位置的 logits
            logits = outputs.logits[:, -1, :] # shape: (batch_size, vocab_size)
            
            # 准备目标
            # CrossEntropyLoss 需要 target 的 shape 为 (batch_size)
            target = torch.tensor([target_token_id], device=model.device)
            
            # 计算 Loss
            loss = self.loss_fn(logits, target)
            
            return {"loss": round(loss.item(), 4)} # 返回一个保留4位小数的浮点数

# --- 实例化服务 ---
sft_model_provider = get_model_for_sft_inference
llm_basics_server = LlmBasicsModelServer()
sft_server = SftModelServer() # 新增 SFT 服务实例