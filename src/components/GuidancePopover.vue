<template>
  <div class="container-fluid pb-5">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">大模型基础</h1>
      <p class="lead text-muted">揭开LLM的神秘面纱，理解它最基本的“思考”方式。</p>
    </div>

    <div class="card shadow-sm mb-5" id="tokenizer-module">
      <div class="card-header bg-light">
        <h4 class="mb-0">1. 交互式 Tokenizer (令牌化)</h4>
      </div>
      <div class="card-body p-4">
        <p class="card-text">输入任意文本，实时查看模型是如何将其“读取”为一个个Token的。这是理解大模型的第一步。</p>
        <div class="mb-3">
          <h6 class="text-muted d-inline-block me-2">当前 Tokenizer:</h6>
          <span class="badge bg-primary fs-6 fw-normal">Qwen2-0.5B</span>
        </div>
        <textarea
          id="tokenizer-input"
          class="form-control form-control-lg mb-3"
          rows="3"
          placeholder="例如：你好，世界！LLM is powerful."
          v-model="inputText"
        ></textarea>
        <div class="p-3 border rounded bg-light" style="min-height: 100px;">
          <h6 class="text-muted mb-2">
            Tokenization 结果
            <span v-if="!tokenizing">(共 {{ tokens.length }} 个 Tokens):</span>
            <span v-if="tokenizing" class="spinner-border spinner-border-sm text-primary ms-2" role="status"></span>
          </h6>
          <div v-if="!tokenizing" class="d-flex flex-wrap gap-1">
            <span
              v-for="(token, index) in tokens"
              :key="index"
              class="badge fs-6 fw-normal text-dark"
              :style="{ backgroundColor: token.color }"
            >
              {{ token.text }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-5" id="embedding-module">
      <div class="card-header bg-light">
        <h4 class="mb-0">2. 词嵌入 (Embedding) 可视化</h4>
      </div>
      <div class="card-body p-4">
        <p>模型将每个Token映射到一个高维向量空间中，意思相近的词，在空间中的距离也相近。试试看！</p>
        <div class="input-group input-group-lg mb-3">
          <input
            id="embedding-input"
            type="text"
            class="form-control"
            placeholder="输入逗号分隔的单词, e.g., king, queen, man, woman"
            v-model="embeddingWords"
          />
          <button class="btn btn-primary" @click="getAndDrawEmbeddings" :disabled="loadingEmbeddings">
            <span v-if="loadingEmbeddings" class="spinner-border spinner-border-sm" role="status"></span>
            {{ loadingEmbeddings ? '计算中...' : '可视化向量' }}
          </button>
        </div>
        <div ref="embeddingChartRef" id="embedding-chart" style="width: 100%; height: 400px;" class="border rounded bg-light"></div>
      </div>
    </div>

    <div class="card shadow-sm mb-5" id="attention-module">
        <div class="card-header bg-light">
            <h4 class="mb-0">3. 注意力机制 (Attention) 可视化</h4>
        </div>
        <div class="card-body p-4">
            <p>注意力机制允许模型在处理一个词时，动态地关注句子中的其他相关词。输入一个句子，将鼠标悬浮在某个词上，查看它的注意力分布。</p>
            <div class="input-group input-group-lg mb-3">
                <input id="attention-input" type="text" class="form-control" v-model="attentionText" />
                <button class="btn btn-primary" @click="getAttentionData" :disabled="loadingAttention">
                    <span v-if="loadingAttention" class="spinner-border spinner-border-sm" role="status"></span>
                    {{ loadingAttention ? '分析中...' : '分析注意力' }}
                </button>
            </div>
            <div class="d-flex gap-3 mb-3 align-items-center">
                <div class="col-auto">
                    <label for="layerSelect" class="form-label mb-0">注意力层 (Layer):</label>
                    <select id="layerSelect" class="form-select" v-model.number="selectedLayer">
                        <option v-for="n in 24" :key="n-1" :value="n-1">{{ n-1 }}</option>
                    </select>
                </div>
                <div class="col-auto">
                    <label for="headSelect" class="form-label mb-0">注意力头 (Head):</label>
                    <select id="headSelect" class="form-select" v-model.number="selectedHead">
                        <option v-for="n in 16" :key="n-1" :value="n-1">{{ n-1 }}</option>
                    </select>
                </div>
            </div>

            <div id="attention-vis-area" class="p-4 border rounded bg-light fs-4" style="line-height: 2.5;">
                <span v-if="!attentionData.tokens.length && !loadingAttention">在此显示注意力结果...</span>
                <span v-else>
                    <span
                        v-for="(token, index) in attentionData.tokens"
                        :key="index"
                        :data-token-index="index"
                        @mouseenter="highlightAttention(index)"
                        class="attention-token"
                    >
                        {{ token }}
                    </span>
                </span>
                <svg width="100%" height="100%" style="position: absolute; top: 0; left: 0; pointer-events: none;">
                    <line
                        v-for="(line, index) in attentionLines"
                        :key="index"
                        :x1="line.x1" :y1="line.y1"
                        :x2="line.x2" :y2="line.y2"
                        stroke="rgba(118, 75, 162, 0.6)"
                        :stroke-width="line.width"
                    />
                </svg>
            </div>
        </div>
    </div>
    
    <div class="card shadow-sm" id="prediction-module">
      <div class="card-header bg-light">
        <h4 class="mb-0">4. “猜猜下一个词”游戏</h4>
      </div>
       <div class="card-body p-4">
        <p>体验LLM的核心工作原理——按概率生成下一个Token。输入一个句子开头，看看模型会预测出什么。</p>
        <div class="input-group input-group-lg mb-3">
          <input
            id="prediction-input"
            type="text"
            class="form-control"
            placeholder="输入一个句子开头，或点击下方示例"
            v-model="predictionPrefix"
          />
          <button class="btn btn-primary" @click="predictNextToken" :disabled="loadingPrediction">
            <span v-if="loadingPrediction" class="spinner-border spinner-border-sm" role="status"></span>
            {{ loadingPrediction ? '预测中...' : '模型来预测' }}
          </button>
        </div>
        <div class="d-flex flex-wrap gap-2">
            <span class="text-muted small me-2 align-self-center">试试看:</span>
            <button 
                v-for="example in examplePrefixes" 
                :key="example" 
                class="btn btn-outline-secondary btn-sm"
                @click="setPrefix(example)"
            >
                {{ example }}
            </button>
        </div>
        <div v-if="predictions.length > 0" class="mt-4">
            <h6 class="text-muted mb-3">模型预测概率最高的 Top 5 Tokens:</h6>
            <div class="d-flex flex-column gap-3">
                <div v-for="p in predictions" :key="p.token" class="row g-2 align-items-center">
                    <div class="col-3 col-md-2 text-end">
                        <span class="fw-bold text-truncate" :title="p.token">{{ p.token }}</span>
                    </div>
                    <div class="col-9 col-md-10">
                        <div class="progress-wrapper position-relative">
                            <div class="progress" style="height: 28px;">
                                <div
                                    class="progress-bar"
                                    role="progressbar"
                                    :style="{ width: p.probability + '%' }"
                                ></div>
                            </div>
                            <span class="probability-text position-absolute w-100 h-100 top-0 start-0 d-flex align-items-center ps-2 fw-bold text-white">{{ p.probability }}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </div>

    <GuidancePopover 
      v-if="guidance.visible"
      :title="guidance.title"
      :content="guidance.content"
      :button-text="guidance.buttonText"
      @confirm="nextGuideStep"
      :style="guidance.style"
    />
  </div>
</template>

<script setup>
import { ref, watch, reactive, onMounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import GuidancePopover from '@/components/GuidancePopover.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

// --- 1. Tokenizer ---
const inputText = ref('LLM is powerful');
const tokens = ref([]);
const tokenizing = ref(false);
const colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99'];

watch(inputText, async (newText) => {
  if (!newText.trim()) {
    tokens.value = [];
    return;
  }
  tokenizing.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/tokenize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: newText }),
    });
    if (!response.ok) throw new Error('网络响应错误');
    const data = await response.json();
    tokens.value = data.tokens.map((text, i) => ({
      text,
      color: colors[i % colors.length]
    }));
  } catch (error) {
    console.error('Tokenizer API 调用失败:', error);
  } finally {
    tokenizing.value = false;
  }
}, { immediate: true });

// --- 2. Embedding ---
const embeddingWords = ref('king, queen, man, woman');
const loadingEmbeddings = ref(false);
const embeddingChartRef = ref(null);
let embeddingChart = null;

const getAndDrawEmbeddings = async () => {
  const words = embeddingWords.value.split(',').map(w => w.trim()).filter(Boolean);
  if (words.length < 2) return;
  
  loadingEmbeddings.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/get_embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ words }),
    });
    if (!response.ok) throw new Error('网络响应错误');
    const data = await response.json();
    
    const chartOption = {
      tooltip: { trigger: 'item', formatter: '{b}' },
      xAxis: { name: 'Dimension 1' },
      yAxis: { name: 'Dimension 2' },
      series: [{
        symbolSize: 20,
        data: data.vectors.map((vec, i) => ({ name: data.words[i], value: vec })),
        type: 'scatter'
      }]
    };
    embeddingChart.setOption(chartOption);
  } catch (error) {
    console.error('Embedding API 调用失败:', error);
  } finally {
    loadingEmbeddings.value = false;
  }
}

// --- 3. Attention ---
const attentionText = ref('The robot ate the apple because it was rusty');
const loadingAttention = ref(false);
const selectedLayer = ref(0);
const selectedHead = ref(0);
const attentionData = ref({ tokens: [], attention: [] });
const attentionLines = ref([]);

const getAttentionData = async () => {
    if (!attentionText.value.trim()) return;
    loadingAttention.value = true;
    attentionData.value = { tokens: [], attention: [] };
    try {
        const response = await fetch(`${API_BASE_URL}/api/get_attention`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text: attentionText.value,
                layer: selectedLayer.value,
                head: selectedHead.value
            }),
        });
        if (!response.ok) throw new Error('网络响应错误');
        attentionData.value = await response.json();
    } catch (error) {
        console.error('Attention API 调用失败:', error);
    } finally {
        loadingAttention.value = false;
    }
};

const highlightAttention = (sourceIndex) => {
    const attentionScores = attentionData.value.attention[sourceIndex];
    const tokenElements = document.querySelectorAll('[data-token-index]');
    const sourceElement = tokenElements[sourceIndex];
    if (!sourceElement) return;

    const sourceRect = sourceElement.getBoundingClientRect();
    const containerRect = sourceElement.parentElement.getBoundingClientRect();

    const newLines = [];
    attentionScores.forEach((score, targetIndex) => {
        const targetElement = tokenElements[targetIndex];
        if (!targetElement) return;

        const targetRect = targetElement.getBoundingClientRect();
        newLines.push({
            x1: sourceRect.left + sourceRect.width / 2 - containerRect.left,
            y1: sourceRect.top + sourceRect.height / 2 - containerRect.top,
            x2: targetRect.left + targetRect.width / 2 - containerRect.left,
            y2: targetRect.top + targetRect.height / 2 - containerRect.top,
            width: score * 10 // Scale line width by attention score
        });
    });
    attentionLines.value = newLines;
};


// --- 4. Prediction ---
const predictionPrefix = ref('今天天气真好，我们一起去');
const loadingPrediction = ref(false);
const predictions = ref([]);
const examplePrefixes = ['Life is like a box of', 'The future of AI is', 'To be or not to be,'];
const setPrefix = (example) => { predictionPrefix.value = example; predictNextToken(); };

const predictNextToken = async () => {
  // ... 现有 predictNextToken 函数逻辑保持不变 ...
   if (!predictionPrefix.value.trim()) return;
  loadingPrediction.value = true;
  predictions.value = [];
  try {
    const response = await fetch(`${API_BASE_URL}/api/predict_next`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: predictionPrefix.value }),
    });
    if (!response.ok) throw new Error('网络响应错误');
    const data = await response.json();
    predictions.value = data.predictions;
  } catch (error) {
    console.error('Predict API 调用失败:', error);
  } finally {
    loadingPrediction.value = false;
  }
};

// --- 5. Guidance System ---
const guidance = reactive({
  visible: false, step: 0, title: '', content: '', buttonText: '继续', style: {}
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

const startGuidance = () => {
  guidance.step = 0;
  showCurrentGuide();
};

const nextGuideStep = async () => {
  if (guidance.step < guideSteps.length - 1) {
    guidance.step++;
    // 使用 nextTick 确保DOM更新后再计算位置
    await nextTick();
    showCurrentGuide();
  } else {
    guidance.visible = false;
  }
};

const showCurrentGuide = () => {
  const currentStep = guideSteps[guidance.step];
  const targetElement = document.getElementById(currentStep.targetId);
  if (targetElement) {
    const rect = targetElement.getBoundingClientRect();
    guidance.style = {
      position: 'fixed', // 使用 fixed 定位以避免滚动问题
      top: `${rect.top}px`,
      left: `${rect.right + 15}px`,
      transform: 'translateY(-20%)' // 微调垂直位置
    };
  }
  guidance.title = currentStep.title;
  guidance.content = currentStep.content;
  guidance.buttonText = currentStep.buttonText || '继续';
  guidance.visible = true;
};

onMounted(() => {
  // 初始化 ECharts
  if (embeddingChartRef.value) {
    embeddingChart = echarts.init(embeddingChartRef.value);
  }
  // 启动引导
  startGuidance();
});

</script>

<style scoped>
.progress-wrapper {
  position: relative;
}
.probability-text {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  padding-left: 0.75rem;
  font-weight: bold;
  color: white;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}
.attention-token {
    padding: 2px 5px;
    margin: 2px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}
.attention-token:hover {
    background-color: #d6bbfb;
}
#attention-vis-area {
    position: relative;
}
</style>