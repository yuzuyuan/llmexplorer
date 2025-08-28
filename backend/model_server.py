import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import os

# --- 路径定义 ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL_PATH = os.path.join(backend_dir, "models", "qwen3-0.6b")
CHECKPOINT_BASE_PATH = os.path.join(backend_dir, "models", "qwen3-catgirl-lora-checkpoints-vanilla")

# --- 资源缓存 ---
# 分开缓存基础模型和已加载的LoRA模型
base_model_cache = {}
lora_model_cache = {}
tokenizer = None

def get_tokenizer():
    """获取全局唯一的tokenizer实例。"""
    global tokenizer
    if tokenizer is None:
        print(f"从本地路径 '{BASE_MODEL_PATH}' 加载 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
        print("Tokenizer 加载完成。")
    return tokenizer

def get_base_model():
    """获取纯净的基础模型实例。"""
    if "base" not in base_model_cache:
        print(f"首次加载基础模型: {BASE_MODEL_PATH} ...")
        quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH,
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        base_model_cache["base"] = model
        print("基础模型加载完成。")
    return base_model_cache["base"]

def get_model_for_inference(model_id: str = "base"):
    """
    根据模型ID，获取用于推理的最终模型。
    """
    # 如果请求的是基础模型，直接从基础模型缓存中获取
    if model_id == "base":
        print("--- 推理模式: 基础模型 ---")
        return get_base_model()
        
    # 如果请求的LoRA模型已在缓存中，直接返回
    if model_id in lora_model_cache:
        print(f"--- 推理模式: 从缓存加载LoRA模型 '{model_id}' ---")
        return lora_model_cache[model_id]

    # 如果LoRA模型不在缓存中，则动态加载
    lora_path = os.path.join(CHECKPOINT_BASE_PATH, model_id)
    if os.path.isdir(lora_path):
        print(f"动态加载 LoRA 权重: {lora_path} ...")
        # 1. 先获取纯净的基础模型
        base_model = get_base_model()
        # 2. 在基础模型上加载LoRA权重，生成一个新的PeftModel
        lora_model = PeftModel.from_pretrained(base_model, lora_path)
        # 3. 将新生成的LoRA模型存入缓存
        lora_model_cache[model_id] = lora_model
        print(f"--- 推理模式: '{model_id}' 已加载并缓存 ---")
        return lora_model
    else:
        print(f"警告：未找到检查点 '{model_id}'，将使用基础模型。")
        return get_base_model()

# 在服务启动时预加载tokenizer和基础模型
get_tokenizer()
get_base_model()