import os
import chromadb
from collections import defaultdict

# --- 配置 ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(backend_dir, "chroma_db_law")
CHROMA_COLLECTION_NAME = "law_collection_md"
OUTPUT_FILE = "vectorized_files_report.txt"

def report():
    """
    连接到现有的ChromaDB，统计并报告所有已向量化的文件及其条目数。
    """
    print("--- 开始生成已向量化文件报告 ---")

    # --- 1. 检查数据库是否存在 ---
    if not os.path.exists(CHROMA_PERSIST_DIR):
        print(f"错误: 数据库目录 '{CHROMA_PERSIST_DIR}' 不存在。无法生成报告。")
        return

    try:
        # --- 2. 连接到数据库 ---
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        print(f"成功连接到集合 '{CHROMA_COLLECTION_NAME}'。")

        # --- 3. 获取所有条目的元数据 (这是一个轻量级操作) ---
        # 我们只需要元数据，所以这是一个高效的查询
        total_entries = collection.count()
        if total_entries == 0:
            print("数据库为空，没有已处理的文件。")
            return
            
        print(f"正在从数据库中获取 {total_entries} 条记录的元数据...")
        # 分批获取以防数据量过大导致内存问题
        batch_size = 5000
        all_metadata = []
        for offset in range(0, total_entries, batch_size):
            print(f"正在获取 {offset} 到 {offset+batch_size} 的记录...")
            results = collection.get(
                limit=batch_size,
                offset=offset,
                include=["metadatas"]
            )
            all_metadata.extend(results['metadatas'])
        
        print("元数据获取完毕。")

        # --- 4. 统计每个文件的条目数 ---
        file_counts = defaultdict(int)
        for metadata in all_metadata:
            if 'relative_path' in metadata:
                file_counts[metadata['relative_path']] += 1
        
        if not file_counts:
            print("未能从元数据中提取任何文件路径信息。")
            return

        # --- 5. 生成并保存报告 ---
        sorted_files = sorted(file_counts.items(), key=lambda item: item[0]) # 按文件名排序

        report_content = []
        report_content.append("--- 已成功向量化的文件列表 ---")
        report_content.append(f"总计文件数: {len(sorted_files)}")
        report_content.append(f"总计法条数: {sum(file_counts.values())}")
        report_content.append("-" * 30)

        for file_path, count in sorted_files:
            report_line = f"文件: {file_path.replace(os.sep, '/')} - (包含 {count} 条法条)"
            report_content.append(report_line)

        final_report = "\n".join(report_content)

        # 写入文件
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_report)

        # 打印到控制台
        print("\n" + final_report)
        print(f"\n报告已成功保存到文件: {os.path.join(os.getcwd(), OUTPUT_FILE)}")

    except Exception as e:
        print(f"生成报告时发生错误: {e}")

if __name__ == "__main__":
    report()