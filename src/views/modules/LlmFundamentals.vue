<template>
  <div class="container-fluid">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">大模型基础</h1>
      <p class="lead text-muted">揭开LLM的神秘面纱，理解它最基本的“思考”方式。</p>
    </div>

    <div class="card shadow-sm mb-5">
      <div class="card-header bg-light">
        <h4 class="mb-0">交互式 Tokenizer (令牌化)</h4>
      </div>
      <div class="card-body p-4">
        <p class="card-text">输入任意文本，实时查看模型是如何将其“读取”为一个个Token的。这是理解大模型的第一步。</p>
        
        <div class="row g-3 align-items-center mb-3">
          <div class="col-auto">
            <label for="tokenizer-select" class="col-form-label">模拟 Tokenizer:</label>
          </div>
          <div class="col-auto">
            <select id="tokenizer-select" class="form-select" v-model="selectedTokenizer">
              <option value="gpt2">GPT-2 (通用)</option>
              <option value="bert">BERT (词汇更丰富)</option>
            </select>
          </div>
        </div>

        <textarea
          class="form-control form-control-lg mb-3"
          rows="3"
          placeholder="例如：你好，世界！LLM is powerful."
          v-model="inputText"
        ></textarea>
        
        <div class="p-3 border rounded bg-light" style="min-height: 100px;">
          <h6 class="text-muted mb-2">Tokenization 结果 (共 {{ tokens.length }} 个 Tokens):</h6>
          <div class="d-flex flex-wrap gap-1">
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

    <div class="card shadow-sm">
      <div class="card-header bg-light">
        <h4 class="mb-0">“猜猜下一个词”游戏</h4>
      </div>
      <div class="card-body p-4">
        <p>体验LLM的核心工作原理——按概率生成下一个Token。输入一个句子开头，看看模型会预测出什么。</p>
        <div class="input-group input-group-lg mb-3">
          <input
            type="text"
            class="form-control"
            placeholder="例如：今天天气真好，我们一起去..."
            v-model="predictionPrefix"
          />
          <button class="btn btn-primary" @click="predictNextToken" :disabled="loadingPrediction">
            <span v-if="loadingPrediction" class="spinner-border spinner-border-sm" role="status"></span>
            {{ loadingPrediction ? '预测中...' : '模型来预测' }}
          </button>
        </div>

        <div v-if="predictions.length > 0" class="mt-4">
           <h6 class="text-muted mb-3">模型预测概率最高的 Top 5 Tokens:</h6>
           <div class="d-flex flex-column gap-2">
             <div v-for="p in predictions" :key="p.token" class="progress" style="height: 30px;">
               <div
                 class="progress-bar"
                 role="progressbar"
                 :style="{ width: p.probability + '%' }"
                 :aria-valuenow="p.probability"
                 aria-valuemin="0"
                 aria-valuemax="100"
               >
                 <span class="fw-bold px-2">{{ p.token }} ({{ p.probability }}%)</span>
               </div>
             </div>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const inputText = ref('LLM is powerful');
const selectedTokenizer = ref('gpt2');
const tokens = ref([]);
const colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99'];

const mockTokenize = (text, type) => {
  if (!text) return [];
  let segments;
  if (type === 'bert') {
    segments = text.match(/\w+|[^\w\s]/g) || [];
  } else {
    segments = text.replace(/(\w+)/g, ' $1').split(/\s+/).filter(Boolean);
    segments = segments.flatMap(s => s.length > 4 ? [s.slice(0, 3), s.slice(3)] : [s]);
  }
  return segments.map((text, i) => ({ text, color: colors[i % colors.length] }));
};

watch([inputText, selectedTokenizer], () => { tokens.value = mockTokenize(inputText.value, selectedTokenizer.value); }, { immediate: true });

const predictionPrefix = ref('今天天气真好，我们一起去');
const loadingPrediction = ref(false);
const predictions = ref([]);
const mockPredictions = { "公园": 45, "爬山": 20, "吃饭": 15, "看电影": 10, "散步": 10 };

const predictNextToken = () => {
  if (!predictionPrefix.value) return;
  loadingPrediction.value = true;
  predictions.value = [];
  setTimeout(() => {
    const sorted = Object.entries(mockPredictions).sort(([,a],[,b]) => b-a).map(([token, probability]) => ({ token, probability }));
    predictions.value = sorted;
    loadingPrediction.value = false;
  }, 1000);
};
</script>

<style scoped>
.progress-bar { text-align: left; color: white; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
</style>