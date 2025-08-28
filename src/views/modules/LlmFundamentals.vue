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
        
        <div class="mb-3">
          <h6 class="text-muted d-inline-block me-2">当前 Tokenizer:</h6>
          <span class="badge bg-primary fs-6 fw-normal">Qwen3-0.6B</span>
        </div>

        <textarea
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
                    <div class="progress-wrapper">
                        <div class="progress" style="height: 28px;">
                            <div
                                class="progress-bar"
                                role="progressbar"
                                :style="{ width: p.probability + '%' }"
                            ></div>
                        </div>
                        <span class="probability-text">{{ p.probability }}%</span>
                    </div>
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

// --- Tokenizer ---
const inputText = ref('LLM is powerful');
const tokens = ref([]);
const tokenizing = ref(false); // 新增：用于显示加载状态
const colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99'];

// 旧的 mockTokenize 函数已被移除

// 使用 watch 监听输入文本的变化，并调用后端API
watch(inputText, async (newText) => {
  if (!newText.trim()) {
    tokens.value = [];
    return;
  }
  
  tokenizing.value = true; // 开始请求，显示加载状态
  try {
    const response = await fetch('http://127.0.0.1:8000/api/tokenize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: newText }),
    });

    if (!response.ok) {
      throw new Error('网络响应错误');
    }

    const data = await response.json();
    
    // 用后端返回的真实Token更新界面
    tokens.value = data.tokens.map((text, i) => ({
      text,
      color: colors[i % colors.length]
    }));

  } catch (error) {
    console.error('Tokenizer API 调用失败:', error);
    // 可以在这里添加错误提示UI
  } finally {
    tokenizing.value = false; // 请求结束，取消加载状态
  }
}, { immediate: true }); // immediate: true 确保组件加载时就执行一次

const predictionPrefix = ref('今天天气真好，我们一起去');
const loadingPrediction = ref(false);
const predictions = ref([]);
// 移除 mockPredictions

const predictNextToken = async () => {
  if (!predictionPrefix.value.trim()) return;
  
  loadingPrediction.value = true;
  predictions.value = [];
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/predict_next', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: predictionPrefix.value }),
    });

    if (!response.ok) {
      throw new Error('网络响应错误');
    }

    const data = await response.json();
    predictions.value = data.predictions;

  } catch (error) {
    console.error('Predict API 调用失败:', error);
    // 可以在这里添加错误提示UI
  } finally {
    loadingPrediction.value = false;
  }
};
</script>

<style scoped>
.progress-bar { text-align: left; color: white; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
</style>