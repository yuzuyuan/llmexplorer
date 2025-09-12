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
          <div class="text-center mb-4">
            <h2 class="fw-bold">SFT 微调原理探究</h2>
            <p class="lead text-muted">深入训练的每一步，亲眼见证模型如何通过“批改作业”来学习。</p>
          </div>
          <DatasetExplorer id="dataset-explorer" @item-selected="selectedItem = $event" @interaction="handleInteraction('dataset-nav')" />
          <SftStepVisualizer id="sft-step-visualizer" :dataset-item="selectedItem" @interaction="handleInteraction('model-select')" />
        </div>

        <div class="mt-5" id="sft-simulator">
            <SftSimulator @interaction="handleInteraction" />
        </div>

        <div class="mt-5">
          <h2 class="text-center fw-bold mb-4">相关知识文档</h2>
          <div v-html="htmlContent" class="markdown-body"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue';
import { useMarkdown } from '@/composables/useMarkdown.js';
import GuidancePopover from '@/components/GuidancePopover.vue';
import DatasetExplorer from '@/views/modules/DatasetExplorer.vue';
import SftStepVisualizer from '@/views/modules/SftStepVisualizer.vue';
import SftSimulator from '@/views/modules/SftSimulator.vue';
import { useAchievements } from '@/composables/useAchievements';
import '@/assets/page-styles.css';

const { htmlContent, toc } = useMarkdown('4-sft');
const { unlockAchievement, trackInteraction } = useAchievements();
const pageContainerRef = ref(null);

// --- 核心修复 ---
// 彻底移除所有写死的数据，将 selectedItem 初始化为 null
// 它将会等待 DatasetExplorer 加载完毕后发出的第一个数据
const selectedItem = ref(null);

// --- Achievement Tracking (无需改动) ---
const achievementId = 'read_sft';
const interactionAchievementId = 'interact_sft';
const requiredInteractions = ['dataset-nav', 'model-select', 'chat-send', 'start-simulation'];

const handleScroll = () => {
  const element = document.documentElement;
  if (element.scrollHeight - element.scrollTop <= element.clientHeight + 1) {
    unlockAchievement(achievementId);
  }
};

const handleInteraction = (interactionId) => {
  trackInteraction('sft', interactionId);

  const interactions = JSON.parse(localStorage.getItem('interactions_sft') || '[]');
  const allInteracted = requiredInteractions.every(id => interactions.includes(id));

  if (allInteracted) {
    unlockAchievement(interactionAchievementId);
  }
};


// --- Guidance (无需改动) ---
const guidance = reactive({
  visible: false, step: 0, title: '', content: '', buttonText: '',
});

const guideSteps = [
    { targetId: 'sft-step-visualizer', title: '欢迎来到 SFT 微调实验室！', content: '如果说基础大模型是一个博学的‘通才’，那么 **SFT (监督微调)** 就是把它训练成某个领域‘专家’的过程。在这里，您将扮演‘老师’的角色，亲眼见证一个通用模型是如何学会‘角色扮演’的。'},
    { targetId: 'dataset-explorer', title: '第一步: 准备“教科书”', content: 'SFT 的第一步，也是最重要的一步，就是准备一本高质量的‘教科书’——**数据集**。请点击左右按钮浏览，每一页都是一条我们希望模型学会的问答。这种‘指令-输入-输出’的格式，就是模型学习的‘标准答案’。'},
    { targetId: 'sft-step-visualizer', title: '第二步: 选择你的“学生”', content: '我们为您准备了两位‘学生’：一位是未经训练的‘**基础模型 (Base Model)**’，另一位是经过我们教科书微调毕业的‘**微调后模型 (checkpoint-100)**’。让我们先从基础模型开始，看看它的初始水平如何。'},
    { targetId: 'sft-step-visualizer', title: '第三步: 开始“随堂测验”', content: '现在，请将鼠标悬浮在下面‘正确回答’的**第一个 Token** 上。这相当于您指着教科书上的一个字，考察‘基础模型’是否知道这里应该填什么。'},
    { targetId: 'sft-step-visualizer', title: '观察“基础模型”的答卷', content: '您看到了吗？基础模型完全预测错了，因此它的**损失 (Loss) 值非常高**！Loss 是衡量‘模型预测’与‘正确答案’之间差距的指标，**Loss 越高，说明模型错得越离谱**。'},
    { targetId: 'sft-step-visualizer', title: '第四步: 换一位“优秀毕业生”', content: '现在，奇迹的时刻到了！请将模型切换到微调完成的‘**checkpoint-100**’，然后将鼠标再次悬浮在**同一个 Token** 上。'},
    { targetId: 'sft-step-visualizer', title: '见证“学习的成果”！', content: '看！**Loss 值变得极低**，而且模型准确地预测出了正确答案！这正是监督微调的魔力：通过成千上万次这样‘计算 Loss -> 调整自己’的循环，模型最终掌握了我们教科书里的知识。'},
    { targetId: 'sft-simulator', title: '毕业考试！', content: '恭喜！您已经理解了 SFT 的核心原理。现在，您可以在下方的对话模拟器中，**自由地向不同阶段的模型提问**，亲身感受微调带来的巨大变化！'}
];

const toggleGuidance = () => { guidance.visible = !guidance.visible; if (guidance.visible) { guidance.step = 0; updateGuidanceContent(); }};
const nextGuideStep = () => { if (guidance.step < guideSteps.length - 1) { guidance.step++; updateGuidanceContent(); } else { guidance.visible = false; document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide')); }};
const restartGuidance = () => { guidance.visible = true; guidance.step = 0; updateGuidanceContent(); };
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
  position: relative;
  z-index: 10;
}
</style>
