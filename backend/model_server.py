import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import os
import numpy as np
from sklearn.decomposition import PCA

# --- 路径定义 ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL_PATH = os.path.join(backend_dir, "models", "qwen3-0.6b")
CHECKPOINT_BASE_PATH = os.path.join(backend_dir, "models", "qwen3-catgirl-lora-checkpoints-vanilla")


class ModelServer:
    """
    一个封装了模型、Tokenizer加载和核心功能的单例服务类。
    """
    def __init__(self):
        print("正在初始化 ModelServer...")
        self.base_model_cache = {}
        self.lora_model_cache = {}
        self.tokenizer = self._load_tokenizer()
        self._load_base_model() # 启动时预加载基础模型
        print("ModelServer 初始化完成。")

    def _load_tokenizer(self):
        """私有方法：加载全局唯一的tokenizer实例。"""
        print(f"从本地路径 '{BASE_MODEL_PATH}' 加载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
        print("Tokenizer 加载完成。")
        return tokenizer

    def _load_base_model(self):
        """私有方法：加载纯净的基础模型实例到缓存。"""
        if "base" not in self.base_model_cache:
            print(f"首次加载基础模型: {BASE_MODEL_PATH} ...")
            quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
            model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_PATH,
                quantization_config=quantization_config,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )
            self.base_model_cache["base"] = model
            print("基础模型加载完成。")
        return self.base_model_cache["base"]

    def get_model_for_inference(self, model_id: str = "base"):
        """
        根据模型ID，获取用于推理的最终模型。
        """
        if model_id == "base":
            print("--- 推理模式: 基础模型 ---")
            return self.base_model_cache.get("base")
            
        if model_id in self.lora_model_cache:
            print(f"--- 推理模式: 从缓存加载LoRA模型 '{model_id}' ---")
            return self.lora_model_cache[model_id]

        lora_path = os.path.join(CHECKPOINT_BASE_PATH, model_id)
        if os.path.isdir(lora_path):
            print(f"动态加载 LoRA 权重: {lora_path} ...")
            base_model = self.base_model_cache.get("base")
            # 确保基础模型已加载
            if base_model is None:
                base_model = self._load_base_model()
            
            lora_model = PeftModel.from_pretrained(base_model, lora_path)
            self.lora_model_cache[model_id] = lora_model
            print(f"--- 推理模式: '{model_id}' 已加载并缓存 ---")
            return lora_model
        else:
            print(f"警告：未找到检查点 '{model_id}'，将使用基础模型。")
            return self.base_model_cache.get("base")

    # --- 新增功能：获取词嵌入 ---
    def get_embeddings(self, words: list[str]):
        """
        获取单词的嵌入向量并通过PCA降维到2D。
        """
        base_model = self.base_model_cache.get("base")
        embeddings_layer = base_model.get_input_embeddings()
        
        token_ids = self.tokenizer(words, add_special_tokens=False)['input_ids']
        
        vectors = []
        processed_words = []
        for i, word in enumerate(words):
            if token_ids[i]:
                vec = embeddings_layer(torch.tensor(token_ids[i][0]).to(base_model.device)).detach().cpu().numpy()
                vectors.append(vec)
                processed_words.append(word)

        if len(vectors) < 2:
            return {"error": "Please provide at least 2 words to visualize."}
        
        pca = PCA(n_components=2)
        vectors_2d = pca.fit_transform(np.array(vectors))
        
        return {
            "words": processed_words,
            "vectors": vectors_2d.tolist()
        }

    # --- 新增功能：获取注意力权重 ---
    def get_attention(self, text: str, layer: int, head: int):
        """
        获取输入文本在一个指定层和头的注意力权重。
        """
        model = self.get_model_for_inference("base") # 注意力可视化通常在基础模型上进行
        inputs = self.tokenizer(text, return_tensors="pt").to(model.device)
        token_ids = inputs.input_ids[0].tolist()
        tokens = self.tokenizer.convert_ids_to_tokens(token_ids)
        
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)
        
        attention_tensor = outputs.attentions[layer]
        attention_for_head = attention_tensor[0, head, :, :].cpu().numpy().tolist()
        
        return {
            "tokens": tokens,
            "attention": attention_for_head
        }

# --- 创建全局唯一的服务实例 ---
# 在FastAPI应用中，我们只会导入这个 model_server_instance 实例
model_server_instance = ModelServer()