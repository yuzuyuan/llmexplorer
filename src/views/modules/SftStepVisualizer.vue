<template>
  <div class="card shadow-sm mt-5">
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
      <h4 class="mb-0">2. 单步训练可视化 (随堂测验)</h4>
    </div>
    <div class="card-body p-4">
      <div class="row align-items-center mb-4">
        <div class="col-md-3"><strong>选择学生 (模型):</strong></div>
        <div class="col-md-9">
          <select class="form-select" v-model="selectedModel">
            <option value="base">基础模型 (Base Model)</option>
            <option value="checkpoint-20">微调中 (checkpoint-20)</option>
            <option value="checkpoint-40">微调中 (checkpoint-40)</option>
            <option value="checkpoint-60">微调中 (checkpoint-60)</option>
            <option value="checkpoint-80">微调中 (checkpoint-80)</option>
            <option value="checkpoint-100">微调后模型 (checkpoint-100)</option>
          </select>
        </div>
      </div>

      <div v-if="datasetItem">
        <p><strong>考题:</strong></p>
        <div class="p-3 border rounded bg-light mb-3">
          <p class="mb-1"><strong>指令:</strong> {{ datasetItem.instruction }}</p>
          <p class="mb-0"><strong>输入:</strong> {{ datasetItem.input || '(无)' }}</p>
        </div>
        <p><strong>正确回答 (已过滤符号):</strong> (将鼠标悬浮在每个文字Token上进行考察)</p>
        <div v-if="targetTokens.length > 0" class="p-3 border rounded bg-light fs-5 token-container">
          <span
            v-for="(token, index) in targetTokens"
            :key="index"
            class="interactive-token"
            @mouseenter="inspectToken(index)"
          >
            {{ token.text }}
          </span>
        </div>
        <div v-else class="alert alert-warning mt-2">
          此条数据的“正确回答”中没有可供考察的文字Token。
        </div>
      </div>

      <div v-if="inspectionResult" class="mt-4 p-3 border rounded bg-white">
        <h5>测验结果 (针对 Token: <span class="text-primary fw-bold">{{ inspectionResult.targetToken }}</span>)</h5>
        <div class="row">
          <div class="col-md-4 d-flex flex-column justify-content-center align-items-center text-center">
            <h6 class="text-muted">模型 Loss (差距)</h6>
            <div :class="lossClass" class="loss-display">
              {{ inspectionResult.loss.toFixed(2) }}
            </div>
            <p class="small text-muted mt-2">{{ lossDescription }}</p>
          </div>
          <div class="col-md-8">
            <h6 class="text-muted">模型 Top 5 预测</h6>
            <div v-if="loadingInspection" class="text-center">
              <span class="spinner-border spinner-border-sm"></span>
            </div>
            <div v-else class="d-flex flex-column gap-2">
              <div v-for="p in inspectionResult.predictions" :key="p.token" class="row g-2 align-items-center">
                <div class="col-3 text-end">
                  <span
                    class="fw-bold"
                    :class="{ 'text-success': p.isCorrect, 'text-danger': !p.isCorrect }"
                  >
                    {{ p.token }}
                    <i v-if="p.isCorrect" class="bi bi-check-circle-fill"></i>
                  </span>
                </div>
                <div class="col-9">
                  <div class="progress" style="height: 24px;">
                    <div class="progress-bar" :style="{ width: p.probability + '%' }">{{ p.probability }}%</div>
                  </div>
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
import { ref, watch, defineProps, computed } from 'vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

const props = defineProps({
  datasetItem: Object,
});

const selectedModel = ref('base');
const originalTokens = ref([]);
const targetTokens = ref([]);
const inspectionResult = ref(null);
const loadingInspection = ref(false);

let tokenizerCache = {};

// **核心修改：调用新的、专用的API端点**
const tokenizeText = async (text) => {
  const cacheKey = `visualizer_${text}`;
  if (tokenizerCache[cacheKey]) return tokenizerCache[cacheKey];
  try {
    const response = await fetch(`${API_BASE_URL}/api/sft/visualizer_tokenize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) return [];
    const data = await response.json();
    const result = data.tokens.map((token, index) => ({ text: token, id: data.token_ids[index] }));
    tokenizerCache[cacheKey] = result;
    return result;
  } catch (error) {
    console.error("Visualizer Tokenization failed:", error);
    return [];
  }
};

watch(() => props.datasetItem, async (newItem) => {
  if (newItem && newItem.output) {
    inspectionResult.value = null;
    originalTokens.value = await tokenizeText(newItem.output);

    // 过滤掉符号，只保留文字和数字用于显示
    const regex = /^[\p{L}\p{N}]+$/u;
    targetTokens.value = originalTokens.value
      .map((token, originalIndex) => ({ ...token, originalIndex }))
      .filter(token => {
        const cleanedText = token.text.replace(/ /g, '').trim(); //  处理Qwen tokenizer可能产生的前缀' '
        return regex.test(cleanedText);
      });
  }
}, { immediate: true });

let debounceTimer;
const inspectToken = (filteredIndex) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    if (!props.datasetItem) return;

    const currentToken = targetTokens.value[filteredIndex];
    const originalIndex = currentToken.originalIndex;

    loadingInspection.value = true;
    inspectionResult.value = null;

    const fullPrompt = `指令: ${props.datasetItem.instruction}\n输入: ${props.datasetItem.input || ''}\n输出: `;
    const contextTokens = originalTokens.value.slice(0, originalIndex).map(t => t.text);
    const context = fullPrompt + contextTokens.join('');
    const targetToken = originalTokens.value[originalIndex];

    try {
      const [lossRes, predRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/calculate_loss`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model_id: selectedModel.value,
            context: context,
            target_token_id: targetToken.id,
          }),
        }),
        fetch(`${API_BASE_URL}/api/predict_next`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: context,
            model_id: selectedModel.value
          }),
        })
      ]);

      if (!lossRes.ok || !predRes.ok) throw new Error("API request failed");

      const lossData = await lossRes.json();
      const predData = await predRes.json();

      inspectionResult.value = {
        loss: lossData.loss,
        targetToken: targetToken.text,
        predictions: predData.predictions.map(p => ({
          ...p,
          isCorrect: p.token.trim() === targetToken.text.trim()
        }))
      };

    } catch (error) {
      console.error("Inspection failed:", error);
    } finally {
      loadingInspection.value = false;
    }
  }, 300);
};

const lossClass = computed(() => {
  if (!inspectionResult.value) return '';
  const loss = inspectionResult.value.loss;
  if (loss > 5) return 'loss-high';
  if (loss > 2) return 'loss-medium';
  return 'loss-low';
});

const lossDescription = computed(() => {
  if (!inspectionResult.value) return '';
  const loss = inspectionResult.value.loss;
  if (loss > 5) return '差距巨大，模型完全预测错了。';
  if (loss > 2) return '有一定差距，模型感到困惑。';
  return '差距很小，模型预测得很好！';
});

</script>

<style scoped>
.token-container {
  line-height: 2.5;
}
.interactive-token {
  padding: 4px 8px;
  margin: 3px;
  border-radius: 5px;
  cursor: pointer;
  display: inline-block;
  border: 1px solid #e0e0e0;
  transition: background-color 0.2s;
}
.interactive-token:hover {
  background-color: #e9ecef;
}
.loss-display {
  font-size: 2.5rem;
  font-weight: bold;
  padding: 1rem;
  border-radius: 50%;
  width: 100px;
  height: 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s;
}
.loss-high { color: #dc3545; border: 4px solid #dc3545; }
.loss-medium { color: #ffc107; border: 4px solid #ffc107; }
.loss-low { color: #198754; border: 4px solid #198754; }
.progress-bar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
