// src/composables/quizzes.js
import { ref } from 'vue';

export function useQuizzes() {
  const quizzes = ref([
    // --- 原有的 5 个题目 ---
    {
      id: 'llm-basics-1',
      topic: '大模型基础',
      question: '在创意写作任务中，为了让模型生成更多样、更有趣的内容，应该如何调整 Temperature 参数？',
      options: [
        '调高 Temperature (例如 0.8)',
        '调低 Temperature (例如 0.2)',
        'Temperature 对创造性没有影响',
        '使用 Top-k 采样代替'
      ],
      answer: '调高 Temperature (例如 0.8)'
    },
    {
      id: 'prompt-engineering-1',
      topic: 'Prompt Engineering',
      question: '当你需要模型输出一个严格的 JSON 格式时，以下哪种 Prompt Engineering 技巧最有效？',
      options: [
        '只提高 temperature 参数',
        '使用 Few-shot Learning 提供一个 JSON 格式的示例',
        '在 Prompt 中简单地说“请给我 JSON”',
        '使用 Chain of Thought'
      ],
      answer: '使用 Few-shot Learning 提供一个 JSON 格式的示例'
    },
    {
      id: 'rag-1',
      topic: 'RAG',
      question: '如果你的目标是让一个通用大模型学会模仿你们公司独特的、略带幽默的客服沟通风格，应该优先选择哪种技术？',
      options: [
        'RAG，因为它能接入最新的产品信息。',
        'Fine-tuning，因为它能让模型学习并模仿特定的行为和风格。',
        '两种方法效果一样。',
        '不需要任何技术，直接用通用模型即可。'
      ],
      answer: 'Fine-tuning，因为它能让模型学习并模仿特定的行为和风格。'
    },
    {
      id: 'sft-1',
      topic: 'SFT',
      question: 'SFT, RLHF, DPO这三种技术在模型对齐流程中通常是什么样的关系？',
      options: [
        '它们是三种完全独立、互不相干的技术。',
        '通常先用RLHF或DPO，再用SFT进行补充。',
        '通常先用SFT进行基础的指令遵循训练，再用RLHF或DPO进行偏好对齐。',
        'DPO是SFT的升级版，可以完全替代SFT。'
      ],
      answer: '通常先用SFT进行基础的指令遵循训练，再用RLHF或DPO进行偏好对齐。'
    },
    {
      id: 'transformer-1',
      topic: 'Transformer',
      question: 'Transformer 架构相比于传统的 RNN/LSTM，其最核心的优势是什么？',
      options: [
        '它使用了更少的参数',
        '它能并行处理整个序列，并捕捉长距离依赖',
        '它的训练过程不需要梯度下降',
        '它只能用于文本翻译任务'
      ],
      answer: '它能并行处理整个序列，并捕捉长距离依赖'
    },
    // --- 新增的 5 个题目 ---
    {
      id: 'rag-2',
      topic: 'RAG',
      question: 'RAG（检索增强生成）技术最核心的价值是为了解决大模型的什么问题？',
      options: [
        '提升模型的数学计算能力',
        '知识静态与幻觉问题',
        '加快模型的训练速度',
        '降低模型的部署成本'
      ],
      answer: '知识静态与幻觉问题'
    },
    {
      id: 'sft-2',
      topic: 'SFT',
      question: '进行监督微调（SFT）时，最关键的数据集格式是什么？',
      options: [
        '大量的纯文本',
        '“指令-回答”对 (Instruction-Response pairs)',
        '用户评分数据',
        '图像和标签'
      ],
      answer: '“指令-回答”对 (Instruction-Response pairs)'
    },
    {
      id: 'prompt-engineering-2',
      topic: 'Prompt Engineering',
      question: "在Prompt Engineering中，'Let's think step by step' 这个指令主要用于触发模型的什么能力？",
      options: [
        'Few-shot学习',
        '思维链 (Chain of Thought)',
        'JSON格式输出',
        '角色扮演'
      ],
      answer: '思维链 (Chain of Thought)'
    },
    {
      id: 'transformer-2',
      topic: 'Transformer',
      question: '在一个标准的翻译任务中，Transformer模型的哪个部分主要负责理解输入的源语言句子？',
      options: [
        '编码器 (Encoder)',
        '解码器 (Decoder)',
        '注意力机制 (Attention Mechanism)',
        '前馈网络 (Feed-Forward Network)'
      ],
      answer: '编码器 (Encoder)'
    },
    {
      id: 'transformer-3',
      topic: 'Transformer',
      question: '除了自然语言处理，Transformer架构还在哪个领域取得了革命性突破，例如AlphaFold 2？',
      options: [
        '自动驾驶',
        '蛋白质结构预测',
        '股票市场预测',
        '音乐生成'
      ],
      answer: '蛋白质结构预测'
    }
  ]);

  return { quizzes };
}
