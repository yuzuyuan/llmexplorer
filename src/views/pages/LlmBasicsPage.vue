<template>
  <div class="container my-4" ref="pageContainerRef">
    <div class="page-header-actions">
      <button @click="restartGuidance" class="btn btn-outline-info me-2">
        <i class="bi bi-arrow-clockwise me-1"></i>重看引导
      </button>
      <button @click="toggleGuidance" class="btn btn-outline-primary">
        <i class="bi bi-info-circle-fill me-1"></i>
        {{ guidance.visible ? '关闭引导' : '入门引导' }}
      </button>
    </div>

    <GuidancePopover
      v-if="guidance.visible"
      :title="guidance.title"
      :content="guidance.content"
      :button-text="guidance.buttonText"
      @confirm="nextGuideStep"
    />

    <div class="row">
      <div class="col-lg-3 d-none d-lg-block">
        <aside class="toc-sidebar">
          <nav v-if="toc.length > 0">
            <h5 class="toc-title">文档内容</h5>
            <ul class="list-unstyled">
              <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
                <a :href="`#${item.id}`" class="toc-link">{{ item.title }}</a>
              </li>
            </ul>
          </nav>
        </aside>
      </div>
      <div class="col-lg-9">
        <div class="mb-5 pb-4 border-bottom">
          <LlmFundamentals @interaction="handleInteraction" />
        </div>
        <div class="mt-4">
          <h2 class="text-center fw-bold mb-4">相关知识文档</h2>
          <div v-html="htmlContent" class="markdown-body"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, nextTick, onMounted, onUnmounted, ref } from 'vue';
import LlmFundamentals from '../modules/LlmFundamentals.vue';
import GuidancePopover from '@/components/GuidancePopover.vue';
import { useMarkdown } from '@/composables/useMarkdown.js';
import { useAchievements } from '@/composables/useAchievements';
import '@/assets/page-styles.css';

const { htmlContent, toc } = useMarkdown('1-llm-basics');
const { unlockAchievement, trackInteraction } = useAchievements();
const pageContainerRef = ref(null);

// --- Achievement Tracking ---
const achievementId = 'read_llm_basics';
const interactionAchievementId = 'interact_llm_basics';
const requiredInteractions = ['visualize-vectors', 'analyze-attention', 'predict-next'];

const handleScroll = () => {
  const element = document.documentElement;
  if (element.scrollHeight - element.scrollTop <= element.clientHeight + 1) {
    unlockAchievement(achievementId);
  }
};

const handleInteraction = (interactionId) => {
  // 1. Record the interaction
  trackInteraction('llm_basics', interactionId);

  // 2. Check if all required interactions are now complete
  const interactions = JSON.parse(localStorage.getItem('interactions_llm_basics') || '[]');
  const allInteracted = requiredInteractions.every(id => interactions.includes(id));

  // 3. Unlock if complete
  if (allInteracted) {
    unlockAchievement(interactionAchievementId);
  }
};

// --- Guidance System ---
const guidance = reactive({
  visible: false,
  step: 0,
  title: '入门引导',
  content: '',
  buttonText: '开始',
});

const guideSteps = [
  {
    targetId: 'tokenizer-module',
    title: '欢迎来到大模型的世界！',
    content: '您好！大语言模型（LLM）看似神秘，但其核心是由一系列精巧的组件构成的。这个页面将带您互动式地探索最重要的四个核心组件。让我们从第一步开始：模型如何“阅读”文字。'
  },
  {
    targetId: 'tokenizer-module',
    title: '1. Tokenizer (令牌化)',
    content: '计算机不理解文字，只理解数字。**Tokenizer** 的工作就是把我们输入的文本，切分成一个个模型能理解的最小单元（Token），并将其转换为数字 ID。这是模型处理自然语言的第一步，也是最重要的一步。'
  },
  {
    targetId: 'tokenizer-input',
    title: '动手试试 Tokenizer',
    content: '在输入框里试试各种词句，比如长单词 "**unbelievable**" 或者短语 "**role-playing games**"。观察它们是如何被拆分成更基础的 Token 的。'
  },
  {
    targetId: 'embedding-module',
    title: '2. Embedding (词嵌入)',
    content: '文本被切分成 Token 并变成数字后，下一步是让模型理解它们的“含义”。**词嵌入**技术将每个 Token ID 映射到一个高维的数学向量（Vector）。在这个向量空间中，意思相近的词，它们的向量在空间中的距离也更近。'
  },
  {
    targetId: 'embedding-input',
    title: '探索词向量空间',
    content: '试试输入 "**king, queen, man, woman**" 并点击可视化。观察它们的空间位置关系。'
  },
  {
    targetId: 'embedding-chart',
    title: '理论与实践的观察',
    content: '您可能注意到，`king` 到 `queen` 的向量关系与 `man` 到 `woman` 的关系**几乎平行**。这符合我们认知的语义关系'
  },
  {
    targetId: 'embedding-chart',
    title: '事实上',
    content: 'Qwen3 输出的原始向量高达数千维，我们为了在二维图上展示，使用了 **t-SNE 降维**算法。这个过程就像把一个三维的地球仪压平成一张二维地图，必然会牺牲一些信息。'
  },
    {
    targetId: 'embedding-chart',
    title: 't-SNE 的价值',
    content: 't-SNE 算法的强大之处在于，它极力保持了高维空间中数据点之间的**局部近邻关系**。因此，尽管全局的平行关系可能扭曲，您仍能清晰地看到语义相关的词（如 `king`、`queen`、`prince`、`princess`）在空间中**紧密地聚集在了一起**，这正是词嵌入有效性的核心证明！'
  },
  {
    targetId: 'attention-module',
    title: '3. Attention (注意力机制)',
    content: '为了理解一句话，模型需要知道哪些词是重点，以及词与词之间是如何相互关联的。**注意力机制**允许模型在处理一个 Token 时，动态地分配不同的“注意力权重”给句子中的其他所有 Token。'
  },
  {
    targetId: 'attention-layer-selector',
    title: '深入理解: 注意力层 (Layer)',
    content: '一个大模型通常包含数十个**注意力层 (Layer)**。您可以把它想象成模型的多轮“深度思考”。每一层都会在前一层的基础上，重新计算和提炼词与词之间的关联度，从而捕捉到从表层到深层的不同语义信息。'
  },
  {
    targetId: 'attention-head-selector',
    title: '深入理解: 注意力头 (Head)',
    content: '为了让模型更“多才多艺”，在每一层中，又会包含多个独立的**注意力头 (Head)**。每个“头”都是一套独立的 Q, K, V 权重，可以学习一种特定的关系模式。比如，一个头可能专注于语法结构，另一个头可能专注于同义词关联。'
  },
  {
    targetId: 'attention-vis-area',
    title: '观察注意力的“原材料”',
    content: '我们这里的可视化是基于一个**未经训练的、随机初始化**的注意力计算层。点击“分析注意力”，然后将鼠标悬浮在 "**it**" 上。您看到的颜色深浅反映的是词向量在随机变换下的数学相似度，而不是真正的语义指代。'
  },
  {
    targetId: 'attention-vis-area',
    title: '训练的魔力',
    content: '真正的 LLM 会在大规模数据上训练这些注意力权重，直到它们能准确地找出 "**it**" 指代 "**robot**"。我们当前的结果恰好说明了：**算法本身只是骨架，经过海量数据训练的权重才是赋予模型智能的灵魂**。'
  },
  {
    targetId: 'prediction-module',
    title: '4. Prediction (生成预测)',
    content: '经过前面所有组件的复杂计算，模型最终对输入文本形成了深刻的理解。它的核心任务就是基于这个理解，预测出下一个最有可能出现的 Token 是什么。不断地重复这个预测过程，就形成了我们看到的流畅对话和文章。'
  },
  {
    targetId: 'prediction-input',
    title: '体验模型预测',
    content: '在输入框里输入一个句子的开头，比如 "**The best way to learn is**"，然后点击“模型来预测”。看看模型的“第一反应”是什么，这会帮您更好地理解它的工作原理。'
  },
];

const toggleGuidance = () => {
  guidance.visible = !guidance.visible;
  if (guidance.visible) {
    guidance.step = 0;
    updateGuidanceContent();
  } else {
    document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
  }
};

const nextGuideStep = () => {
  if (guidance.step < guideSteps.length - 1) {
    guidance.step++;
    updateGuidanceContent();
  } else {
    guidance.visible = false;
    document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
  }
};

const restartGuidance = () => {
  guidance.visible = true;
  guidance.step = 0;
  updateGuidanceContent();
};

const updateGuidanceContent = async () => {
    await nextTick();
    document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
    const currentStep = guideSteps[guidance.step];
    guidance.title = currentStep.title;
    guidance.content = currentStep.content;
    guidance.buttonText = (guidance.step >= guideSteps.length - 1) ? '完成' : '继续';
    const targetElement = document.getElementById(currentStep.targetId);
    if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetElement.classList.add('highlight-guide');
    }
};

onMounted(() => {
    toggleGuidance();
    window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.page-header-actions {
  text-align: right;
  margin-bottom: 1rem;
}
</style>
