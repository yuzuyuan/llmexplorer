import os
import re
import time
import hashlib
import torch
import nltk 
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import DirectoryLoader

# --- 自动下载 NLTK 依赖 ---
def download_nltk_data():
    required_packages = {
        "punkt": "tokenizers/punkt",
        "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger"
    }
    for pkg_name, pkg_path in required_packages.items():
        try:
            nltk.data.find(pkg_path)
            print(f"NLTK '{pkg_name}' 数据包已安装。")
        except LookupError:
            print(f"未找到 NLTK '{pkg_name}' 数据包，正在下载...")
            nltk.download(pkg_name)
            print(f"'{pkg_name}' 下载完成。")

download_nltk_data()

# --- 1. 配置与模型加载 ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_MODEL_NAME = os.path.join(backend_dir, "models", "qwen3-0.6b-embedding")
project_root = os.path.dirname(backend_dir) 
KNOWLEDGE_BASE_DIR = os.path.join(project_root, "law", "Laws")
CHROMA_PERSIST_DIR = os.path.join(backend_dir, "chroma_db_law")
CHROMA_COLLECTION_NAME = "law_collection_md"

def build():
    print("\n--- 开始构建或更新向量数据库 ---")

    # --- 2. 路径和模型校验 ---
    if not os.path.exists(EMBEDDING_MODEL_NAME):
        print(f"错误: Embedding模型路径不存在: {EMBEDDING_MODEL_NAME}")
        return
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"错误: 知识库目录 '{KNOWLEDGE_BASE_DIR}' 不存在。")
        return

    # --- 3. 初始化 Embedding 模型和 ChromaDB ---
    print(f"正在从本地加载 Embedding 模型: {EMBEDDING_MODEL_NAME}")
    start_time = time.time()
    try:
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        print(f"模型加载完成，耗时: {time.time() - start_time:.2f} 秒")
    except Exception as e:
        print(f"加载Embedding模型时出错: {e}")
        return

    # --- 4. 全量扫描并切分文件 (在内存中完成) ---
    print(f"正在从 '{KNOWLEDGE_BASE_DIR}' 扫描所有 .md 文件...")
    loader = DirectoryLoader(
        KNOWLEDGE_BASE_DIR, glob="**/*.md", show_progress=True, 
        use_multithreading=True, loader_kwargs={"encoding": "utf-8"}, silent_errors=True
    )
    documents = loader.load()

    if not documents:
        print(f"错误: 未能从 '{KNOWLEDGE_BASE_DIR}' 目录中成功加载任何 .md 文件。")
        return

    def process_documents(docs):
        all_chunks = []
        for doc in docs:
            content = doc.page_content; metadata = doc.metadata
            source_path = metadata.get('source', ''); relative_path = os.path.relpath(source_path, KNOWLEDGE_BASE_DIR)
            path_parts = relative_path.split(os.sep)
            category = path_parts[-2] if len(path_parts) > 1 else "general"; file_name = path_parts[-1]
            main_title = content.split('\n')[0].lstrip('# ').strip()
            chunks = re.split(r'(?=^第[\u4e00-\u9fa5\d]+条)', content, flags=re.MULTILINE)
            for chunk_content in chunks:
                chunk_content = chunk_content.strip()
                if not chunk_content.startswith("第"): continue
                clause_match = re.match(r'^(第[\u4e00-\u9fa5\d]+条)', chunk_content)
                clause = clause_match.group(1) if clause_match else "未知条款"
                chunk_metadata = {'source_title': main_title, 'file_name': file_name, 'category': category, 'relative_path': relative_path, 'clause': clause}
                unique_str = f"{relative_path}-{clause}-{chunk_content[:50]}"; chunk_id = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
                all_chunks.append({"id": chunk_id, "text": chunk_content, "metadata": chunk_metadata})
        return all_chunks

    all_chunks = process_documents(documents)
    print(f"文件扫描完成，共发现 {len(all_chunks)} 个潜在法条片段。")

    # --- 5. 实现断点续传机制 ---
    print(f"正在连接到集合: '{CHROMA_COLLECTION_NAME}'")
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME, embedding_function=embedding_function, metadata={"hnsw:space": "cosine"}
    )

    # 获取数据库中已存在的ID
    existing_ids = set(collection.get(include=[])['ids'])
    print(f"数据库中已存在 {len(existing_ids)} 个条目。")

    # 筛选出需要新增的条目
    new_chunks = [chunk for chunk in all_chunks if chunk['id'] not in existing_ids]

    if not new_chunks:
        print("所有法条都已是最新，无需更新。")
        print(f"--- 数据库更新完成！ ---")
        return
        
    print(f"需要新增 {len(new_chunks)} 个条目。开始增量处理...")

    # --- 6. 增量处理与内存优化 ---
    start_time = time.time()
    batch_size = 100 # 保持较小的批次大小以节省内存
    for i in range(0, len(new_chunks), batch_size):
        batch = new_chunks[i:i+batch_size]
        
        # 对于每个批次，我们先提取需要的数据
        batch_ids = [item['id'] for item in batch]
        batch_documents = [item['text'] for item in batch]
        batch_metadatas = [item['metadata'] for item in batch]

        # 直接调用 upsert，ChromaDB 的 embedding_function 会自动处理
        # 这种小批量的方式可以有效避免显存溢出
        collection.upsert(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas
        )
        
        # 释放不再需要的对象，并清理GPU缓存（作为保险措施）
        del batch, batch_ids, batch_documents, batch_metadatas
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print(f"已处理 {i + len(new_chunks[i:i+batch_size])} / {len(new_chunks)} 条新增法条...")

    print(f"增量处理完成，耗时: {time.time() - start_time:.2f} 秒")
    print(f"--- 向量数据库更新成功！ ---")
    print(f"数据库位置: {CHROMA_PERSIST_DIR}")
    print(f"总条目数: {collection.count()}")

if __name__ == "__main__":
    build()