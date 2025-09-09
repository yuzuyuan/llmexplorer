import { reactive, nextTick } from 'vue';

// 步骤1：为每个页面定义引导步骤

// LLM 基础页面的引导步骤 (从您的旧文件迁移而来)
const llmBasicsSteps = [
    { targetId: 'tokenizer-module', title: '第一站：分词器', content: '模型不认识单词，只认识“Tokens”。分词器就是把你的话翻译成模型能懂的语言。' },
    { targetId: 'tokenizer-input', title: '动手试试！', content: '在输入框里试试长单词，比如 "<strong>photosynthesis</strong>"，看看它如何被拆分。' },
    { targetId: 'embedding-module', title: '第二站：词嵌入', content: '模型把每个Token变成高维空间中的一个“点”（向量）。意思相近的词，它们的“点”在空间中的距离也相近。' },
    { targetId: 'embedding-input', title: '发现关系！', content: '输入 <strong>king, queen, man, woman</strong>，然后点击“可视化”，看看它们在空间中的位置关系！' },
    { targetId: 'attention-module', title: '第三站：注意力', content: '这允许模型在处理一个词时，动态地关注句子中的其他相关词，从而理解上下文。' },
    { targetId: 'attention-input', title: '探索上下文！', content: '点击“分析注意力”，然后将鼠标悬浮在 <strong>it</strong> 上，看看模型认为 <strong>it</strong> 指的是 <strong>robot</strong> 还是 <strong>apple</strong>。' },
    { targetId: 'prediction-module', title: '最后一站：预测', content: '理解了前面的步骤后，模型就可以根据前面的Tokens，预测下一个最有可能出现的Token了。' },
    { targetId: 'prediction-input', title: '来玩个游戏！', content: '输入一个句子的开头，看看模型续写的内容是否符合你的预期！' },
];

// RAG 页面的引导步骤
const ragGuideSteps = [
    {
        targetId: 'rag-main-card',
        title: '欢迎来到 RAG 揭秘之旅！',
        content: '大模型虽强，但不知道您的“私有知识”。RAG (Retrieval-Augmented Generation) 就是给它外挂一个知识库，让它能“开卷考试”。准备好了吗？'
    },
    {
        targetId: 'offline-process-explainer', // 我们将在UI中新增一个讲解区域
        title: '【幕后】第一步：知识库的准备 (已完成)',
        content: '在您看到这个页面前，我们已经将海量的法规文档切分成独立的“法条卡片”，并用 Embedding 模型将每张卡片转化为了在数学空间中的“坐标点”，存入了向量数据库。'
    },
    {
        targetId: 'rag-query-input',
        title: '【互动】第二步：向量召回 (Recall)',
        content: '现在，请您输入问题，然后点击“执行向量检索”。系统会把您的问题也变成一个“坐标点”，然后在数据库中快速找出与它“距离”最近的一批“候选法条”。'
    },
    {
        targetId: 'reranker-section', // 我们将为精排区域添加一个ID
        title: '【互动】第三步：Reranker 精排 (Precision)',
        content: '“向量召回”追求快和全，但可能不够准。现在，请点击“应用 Reranker”，这个更强大的模型会精读每个候选法条，并按真实相关度打分排序，优中选优。'
    },
    {
        targetId: 'rag-output',
        title: '【互动】第四步：增强生成 (Generation)',
        content: '最后一步！选择一个上下文来源（对比一下精排前后的区别），然后点击“生成答案”。系统会将最相关的法条和您的问题打包，交给大模型，生成有理有据的回答。'
    }
];

// Prompt Engineering 页面的引导步骤
const promptGuideSteps = [
    { targetId: 'prompt-main-card', title: '欢迎来到 Prompt 对比试验台！', content: 'Prompt Engineering 是一门与 LLM 高效对话的艺术。一个好的 Prompt 能让模型输出的质量天差-地别。在这里，您将通过一个游戏来掌握这门艺术。'},
    { targetId: 'prompt-goal', title: '挑战任务：邮件助手', content: '您的任务是扮演一位邮件助手，根据左侧列出的要点，生成一封专业的会议邀请邮件。一个好的 Prompt 应该包含所有要点，并且清晰、具体。'},
    { targetId: 'prompt-input-area', title: '编写您的 Prompt', content: '在这里输入您的指令。尝试包含不同的元素，比如 **角色** (例如，“你是一位专业的行政助理”)、**任务** (例如，“请写一封会议邀请邮件”)、**格式要求** (例如，“邮件应包含标题、正文和落款”) 和 **风格要求** (例如，“语气应正式、礼貌”)。'},
    { targetId: 'prompt-generate-button', title: '生成并获取评分', content: '点击此按钮，“裁判模型”会根据您 Prompt 的质量和生成结果的好坏给出一个分数。'},
    { targetId: 'prompt-result-display', title: '查看结果与反馈', content: '在这里您可以看到模型的输出、您的得分以及裁判的反馈。不断尝试优化您的 Prompt，争取获得更高的分数，成为一名 Prompt 工程师吧！'}
];
const transformerBuilderSteps = [
    { targetId: 'component-library', title: '欢迎来到 Transformer Builder!', content: '在这里，您将亲手搭建一个完整的 Transformer 翻译模型。首先，让我们认识一下您的“乐高积木”——组件库。' },
    { targetId: 'component-library', title: '认识组件', content: '左侧是构建 Transformer 所需的所有核心组件，例如**嵌入层**、**编码器**和**解码器**。将它们拖拽到右侧的画布上，开始您的搭建之旅吧！' },
    { targetId: 'canvas', title: '搭建您的模型', content: '这里是您的工作区。尝试拖拽一个“源语言输入”和一个“嵌入层”到画布上，将它们连接起来，构成模型的第一步。' },
    { targetId: 'classic-model-btn', title: '一键配置经典模型', content: '如果您想快速开始，可以点击此按钮，系统会自动为您加载一个经典的翻译模型架构。' },
    { targetId: 'parameter-panel', title: '调整参数', content: '点击画布上的任意组件，您可以在右侧的“参数面板”中调整其内部参数，例如**嵌入维度(embed_dim)**或**注意力头数(heads)**。' },
    { targetId: 'start-training-btn', title: '开始训练', content: '当您的模型搭建完成后，点击此按钮即可开始训练！您可以在下方的日志窗口中观察训练过程中的损失(loss)变化。' },
];

// 步骤2：重构引导逻辑以支持多页面

const guidanceState = reactive({
  visible: false,
  step: 0,
  title: '',
  content: '',
  buttonText: '',
  currentSteps: [], // 用于存储当前页面的引导步骤
});

// 存储所有引导流程的映射
const allGuides = {
    llmBasics: llmBasicsSteps,
    rag: ragGuideSteps,
    prompt: promptGuideSteps,
    transformer: transformerBuilderSteps,
};

// 启动函数：接收一个类型参数
export function startGuidance(type = 'llmBasics') {
    if (!allGuides[type]) {
        console.error("未找到指定的引导类型:", type);
        return;
    }
    guidanceState.currentSteps = allGuides[type];
    guidanceState.visible = true;
    guidanceState.step = 0;
    updateGuidanceContent();
}

export function closeGuidance() {
    guidanceState.visible = false;
    document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
}

export function nextGuideStep() {
    if (guidanceState.step < guidanceState.currentSteps.length - 1) {
        guidanceState.step++;
        updateGuidanceContent();
    } else {
        closeGuidance();
    }
}

async function updateGuidanceContent() {
    await nextTick(); // 确保DOM更新完毕

    const currentStep = guidanceState.currentSteps[guidanceState.step];
    if (!currentStep) return;

    guidanceState.title = currentStep.title;
    guidanceState.content = currentStep.content;
    guidanceState.buttonText = (guidanceState.step >= guidanceState.currentSteps.length - 1) ? '完成' : '继续';

    // 高亮目标元素
    document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
    const targetElement = document.getElementById(currentStep.targetId);
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetElement.classList.add('highlight-guide');
    }
}

// 导出一个统一的对象，方便页面使用
export function useGuidance() {
    return {
        guidanceState,
        startGuidance,
        nextGuideStep,
        closeGuidance,
    };
}
