<template>
  <div class="card shadow-sm mt-5">
    <div class="card-header bg-light">
      <h4 class="mb-0">2. 单步训练可视化 (最终版)</h4>
    </div>
    <div class="card-body p-4">
      <div class="p-3 border rounded bg-light mb-4">
        <p class="mb-1"><strong>指令:</strong> {{ example.instruction }}</p>
      </div>

      <div class="p-3 border rounded bg-white mb-4 text-center">
        <h5 class="text-muted mb-3">训练快照：预测关键Token</h5>
        <p class="fs-4">
          <span class="text-muted">{{ example.context }}</span>
          <span class="bg-warning px-2 rounded fw-bold">{{ example.target }}</span>
        </p>
        <small class="text-muted">模型需要根据灰色上下文，预测出黄色高亮的“<strong class="text-dark">{{ example.target }}</strong>”这个Token。</small>
      </div>

      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="mb-3">
            <label for="modelSelector" class="form-label"><strong>选择要考察的模型:</strong></label>
            <select id="modelSelector" class="form-select" v-model="selectedModelId" @change="fetchResults">
              <option value="base">基础模型 (Base Model)</option>
              <option value="checkpoint-100">微调后模型 (checkpoint-100)</option>
            </select>
          </div>
          <ResultCard :title="selectedModelTitle" :result="currentResult" :loading="isLoading" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import ResultCard from './ResultCard.vue';

const API_BASE_URL = 'http://127.0.0.1:8000';

// 写死的示例数据
const example = {
  instruction: "宝宝，你在岩浆里憋气最长时间是多少?",
  context: "*耳朵惊恐地竖起来，尾巴也炸成了蒲公E* 岩...岩浆？！主人怎么会让宝宝去那种可怕的地方！*瑟瑟发抖地躲在主人身后* 我连温水都不敢跳进去呢...更别说岩浆了！要是跳进去的话，我的毛毛肯定会被烤焦的...小声嘀咕 不过...不过有一次我梦见自己变成了喷火",
  target: "猫娘"
};

const isLoading = ref(true);
const selectedModelId = ref('base'); // 默认选择基础模型
const currentResult = ref(null);

const selectedModelTitle = computed(() => {
  return selectedModelId.value === 'base' ? '基础模型 (Base Model)' : '微调后模型 (checkpoint-100)';
});

// --- 核心API请求函数 ---
const fetchPredictionForModel = async (modelId) => {
  try {
    // 1. 将目标Token文本转换为ID
    const tokenizeResponse = await fetch(`${API_BASE_URL}/api/tokenize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: example.target }),
    });
    if (!tokenizeResponse.ok) throw new Error("Tokenize API failed");
    const tokenData = await tokenizeResponse.json();
    const targetTokenId = tokenData.token_ids[0];
    if (targetTokenId === undefined) throw new Error("Could not get target token ID.");

    // 2. 构建Prompt
    let fullPrompt = `指令: ${example.instruction}\n输出: ${example.context}`;

    // 3. 并发获取Loss和预测
    const [lossRes, predRes] = await Promise.all([
      fetch(`${API_BASE_URL}/api/calculate_loss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId, context: fullPrompt, target_token_id: targetTokenId }),
      }),
      fetch(`${API_BASE_URL}/api/predict_next`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: fullPrompt, model_id: modelId }),
      })
    ]);

    if (!lossRes.ok || !predRes.ok) throw new Error(`API calls failed for model ${modelId}`);

    const lossData = await lossRes.json();
    const predData = await predRes.json();

    // 4. 检查返回的数据是否完整
    if (predData.predictions === undefined) {
      console.error("Prediction API response is missing 'predictions' key for model:", modelId, predData);
      throw new Error(`Invalid prediction response for model ${modelId}`);
    }

    return {
      loss: lossData.loss,
      predictions: predData.predictions.map(p => ({
        ...p,
        isCorrect: p.token.trim() === example.target.trim()
      }))
    };
  } catch (error) {
    console.error(`Failed to fetch prediction for ${modelId}:`, error);
    return { loss: 0, predictions: [] }; // 返回一个空的默认值，防止页面崩溃
  }
};

// --- 控制器 ---
const fetchResults = async () => {
  isLoading.value = true;
  currentResult.value = null;
  const result = await fetchPredictionForModel(selectedModelId.value);
  currentResult.value = result;
  isLoading.value = false;
};

// --- 页面加载后，自动加载默认模型的结果 ---
onMounted(fetchResults);

</script>
