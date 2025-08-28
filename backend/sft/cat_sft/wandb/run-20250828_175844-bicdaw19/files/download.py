import wandb
import pandas as pd

# 1. 初始化 W&B API 客户端
api = wandb.Api()

# 2. 定义最终确定的实体和项目名
#    实体名来自您在 W&B 网站上看到的完整工作区名称
#    项目名来自 W&B 网页截图
ENTITY = "3098767024-beijing-institute-of-technology"
PROJECT = "qwen3-0.6B-catgirl-finetune"

try:
    # 3. 获取该项目下的所有运行
    print(f"正在从 '{ENTITY}/{PROJECT}' 获取运行列表...")
    runs = api.runs(f"{ENTITY}/{PROJECT}")

    # 4. 通过运行的显示名称 "run_vanilla_trl_with_local_model" 来精确匹配
    #    这个名称来自你的W&B截图左侧的运行列表
    target_run = None
    for r in runs:
        if r.name == "run_vanilla_trl_with_local_model":
            target_run = r
            break

    if target_run:
        print(f"成功找到运行: {target_run.name} (ID: {target_run.id})")
        
        # 5. 获取历史数据
        #    将 samples 设置得足够大以确保获取所有数据点
        history = target_run.history(samples=10000)

        # 6. 将历史数据转换为 Pandas DataFrame
        df = pd.DataFrame(history)

        # 7. 保存为 CSV 文件
        output_filename = 'wandb_history_data.csv'
        df.to_csv(output_filename, index=False)

        print(f"数据已成功导出到 {output_filename}")
    else:
        print(f"错误: 在项目 '{ENTITY}/{PROJECT}' 中未找到名为 'run_vanilla_trl_with_local_model' 的运行。")
        print("请检查运行名称是否拼写正确。")

except Exception as e:
    print(f"发生错误: {e}")