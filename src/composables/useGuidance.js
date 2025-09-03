import { reactive } from 'vue';

export const guidanceState = reactive({
  visible: false,
  step: 0,
  title: '入门引导',
  content: '点击下方的“继续”按钮，开始探索大模型的核心组件。',
  buttonText: '开始',
});

const guideSteps = [
  { targetId: 'tokenizer-module', title: '第一站：分词器', content: '模型不认识单词，只认识“Tokens”。分词器就是把你的话翻译成模型能懂的语言。' },
  { targetId: 'tokenizer-input', title: '动手试试！', content: '在输入框里试试长单词，比如 "<strong>photosynthesis</strong>"，看看它如何被拆分。' },
  { targetId: 'embedding-module', title: '第二站：词嵌入', content: '模型把每个Token变成高维空间中的一个“点”（向量）。意思相近的词，它们的“点”在空间中的距离也相近。' },
  { targetId: 'embedding-input', title: '发现关系！', content: '输入 <strong>king, queen, man, woman</strong>，然后点击“可视化”，看看它们在空间中的位置关系！' },
  { targetId: 'attention-module', title: '第三站：注意力', content: '这允许模型在处理一个词时，动态地关注句子中的其他相关词，从而理解上下文。' },
  { targetId: 'attention-input', title: '探索上下文！', content: '点击“分析注意力”，然后将鼠标悬浮在 <strong>it</strong> 上，看看模型认为 <strong>it</strong> 指的是 <strong>robot</strong> 还是 <strong>apple</strong>。' },
  { targetId: 'prediction-module', title: '最后一站：预测', content: '理解了前面的步骤后，模型就可以根据前面的Tokens，预测下一个最有可能出现的Token了。' },
  { targetId: 'prediction-input', title: '来玩个游戏！', content: '输入一个句子的开头，看看模型续写的内容是否符合你的预期！' },
];

export function toggleGuidance() {
    guidanceState.visible = !guidanceState.visible;
    // 如果是打开，则从第一步开始
    if (guidanceState.visible) {
        guidanceState.step = 0;
        updateGuidanceContent();
    }
}

export function nextGuideStep() {
    if (guidanceState.step < guideSteps.length - 1) {
        guidanceState.step++;
        updateGuidanceContent();
    } else {
        guidanceState.visible = false;
    }
}

function updateGuidanceContent() {
    const currentStep = guideSteps[guidanceState.step];
    guidanceState.title = currentStep.title;
    guidanceState.content = currentStep.content;
    guidanceState.buttonText = (guidanceState.step === guideSteps.length - 1) ? '完成' : '继续';

    // (可选) 高亮目标元素
    document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
    const targetElement = document.getElementById(currentStep.targetId);
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetElement.classList.add('highlight-guide');
    }
}