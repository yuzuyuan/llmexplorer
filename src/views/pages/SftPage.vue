<template>
  <div class="container my-4">
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
          <DatasetExplorer id="dataset-explorer" @item-selected="selectedItem = $event" />
          <SftStepVisualizer id="sft-step-visualizer" :dataset-item="selectedItem" />
        </div>
        
        <div class="mt-5" id="sft-simulator">
            <SftSimulator />
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
// 引入所有需要的组件
import DatasetExplorer from '@/views/modules/DatasetExplorer.vue';
import SftStepVisualizer from '@/views/modules/SftStepVisualizer.vue';
import SftSimulator from '@/views/modules/SftSimulator.vue'; // 确保 SftSimulator 被正确引入
import '@/assets/page-styles.css';

const { htmlContent, toc } = useMarkdown('4-sft');
const dataset = ref([
  {
    "input": "在你的印象里，人是什么样的",
    "output": "*歪着头思考了一会*\n\n喵~主人问人是什么样的呀？嗯...在人家眼里,人类看起来就是直立行走的两脚兽啦!虽然不像我们猫族那么优雅灵活,但两脚兽也有自己的可爱之处呢~\n\n*轻轻用爪子戳了戳主人*\n\n比如主人这样的两脚兽就很温柔哦!会陪我玩耍,给我好吃的小鱼干,还会摸摸我的头。虽然有时候不太理解两脚兽为什么总是忙忙碌碌的,但只要能和主人一起晒太阳、打盹就开心了!\n\n*眯起眼睛露出回忆的笑容*\n\n不过要说最神奇的地方,就是明明是两脚兽却能让猫娘这么喜欢呢!就像主人一样,让人忍不住想蹭蹭你的心窝~"
  }
]);

// FIX: 2. 初始化 selectedItem，确保页面加载时就有默认的可视化内容
const selectedItem = ref(dataset.value[0]);

// --- 引导逻辑 ---
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
    // 首次进入页面时自动开启引导
    toggleGuidance();
});

onUnmounted(() => {
  // 离开页面时确保清除高亮
  document.querySelectorAll('.highlight-guide').forEach(el => el.classList.remove('highlight-guide'));
});
</script>

<style scoped>
.toc-sidebar {
  position: sticky; top: 2rem; height: calc(100vh - 4rem); overflow-y: auto;
}
.toc-title { font-weight: bold; margin-bottom: 1rem; }
.toc-link {
  color: #6c757d; text-decoration: none; display: block; padding: 0.25rem 0;
}
.toc-link:hover { color: #0d6efd; }
.page-header-actions {
  text-align: right;
  margin-bottom: 1rem;
  position: relative;
  z-index: 10; /* 确保按钮在最上层 */
}
</style>