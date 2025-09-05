import os
import torch
import chromadb
from chromadb.utils import embedding_functions
from transformers import AutoTokenizer, AutoModelForCausalLM

# --- 1. 全局变量和模型初始化 ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_MODEL_NAME = os.path.join(backend_dir, "models", "qwen3-0.6b-embedding")
RERANKER_MODEL_NAME = os.path.join(backend_dir, "models", "qwen3-reranker-0.6b")
CHROMA_PERSIST_DIR = os.path.join(backend_dir, "chroma_db_law")
CHROMA_COLLECTION_NAME = "law_collection_md"

# --- 2. 初始化 Embedding 函数和 ChromaDB 客户端 ---
print("正在加载预构建的向量数据库...")
if not os.path.exists(CHROMA_PERSIST_DIR):
    raise FileNotFoundError(
        f"数据库目录 '{CHROMA_PERSIST_DIR}' 不存在。请先运行 'build_vector_db.py' 脚本来构建数据库。"
    )
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_NAME,
    device='cuda' if torch.cuda.is_available() else 'cpu'
)
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# --- 3. Reranker 模型初始化 ---
try:
    print("Initializing Qwen Reranker model...")
    rerank_tokenizer = AutoTokenizer.from_pretrained(RERANKER_MODEL_NAME, padding_side='left', trust_remote_code=True)
    rerank_model = AutoModelForCausalLM.from_pretrained(
        RERANKER_MODEL_NAME, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
    ).eval()
    TOKEN_FALSE_ID = rerank_tokenizer.convert_tokens_to_ids("no")
    TOKEN_TRUE_ID = rerank_tokenizer.convert_tokens_to_ids("yes")
    print("Qwen Reranker model initialized successfully.")
except Exception as e:
    print(f"Warning: Could not initialize Reranker model: {e}")
    rerank_tokenizer, rerank_model = None, None

# --- 4. 获取已存在的集合 ---
try:
    collection = client.get_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_function
    )
    print(f"成功加载向量数据库集合 '{CHROMA_COLLECTION_NAME}'，包含 {collection.count()} 个条目。")
except ValueError:
     raise ValueError(f"集合 '{CHROMA_COLLECTION_NAME}' 在数据库中不存在。请确认数据库已正确构建。")

# --- 5. 核心功能函数 ---
@torch.no_grad()
def rerank_documents(query, docs):
    if not rerank_model:
        print("Warning: Reranker model not available. Skipping reranking.")
        return docs
    instruction = 'Given a web search query, retrieve relevant passages that answer the query'
    pairs = [f"<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc['text']}" for doc in docs]
    inputs = rerank_tokenizer(pairs, padding=True, truncation=True, return_tensors="pt", max_length=rerank_model.config.max_position_embeddings).to(rerank_model.device)
    outputs = rerank_model(**inputs, use_cache=False)
    batch_scores = outputs.logits[:, -1, :]
    true_scores = batch_scores[:, TOKEN_TRUE_ID]
    false_scores = batch_scores[:, TOKEN_FALSE_ID]
    scores = torch.stack([false_scores, true_scores], dim=1)
    scores = torch.nn.functional.log_softmax(scores, dim=1)
    final_scores = scores[:, 1].exp().tolist()
    for doc, score in zip(docs, final_scores):
        doc['rerank_score'] = round(score, 4)
    reranked_docs = sorted(docs, key=lambda x: x['rerank_score'], reverse=True)
    return reranked_docs

def retrieve_only(query: str):
    """
    只执行第一阶段的向量检索 (Recall)。
    """
    k = 10
    retrieved_results = collection.query(query_texts=[query], n_results=k)
    retrieved_docs = [{"id": retrieved_results['ids'][0][i], "text": doc_text, "distance": round(retrieved_results['distances'][0][i], 4)} for i, doc_text in enumerate(retrieved_results['documents'][0])]
    return {"retrieved_docs": retrieved_docs}

# --- 新增函数：只执行重排序 ---
def rerank_only(query: str, documents: list):
    """
    只对已有的文档列表执行第二阶段的重排序 (Precision)。
    """
    if not rerank_model:
        return {"reranked_docs": documents} # 如果模型不可用，返回原始文档

    reranked_docs = rerank_documents(query, documents)
    return {"reranked_docs": reranked_docs}