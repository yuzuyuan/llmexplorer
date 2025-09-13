<template>
  <div>
    <div class="card shadow-sm mt-5">
      <div class="card-header bg-light d-flex justify-content-between align-items-center">
        <h4 class="mb-0">2. 单步训练可视化</h4>
        <button class="btn btn-outline-primary btn-sm" @click="isModalVisible = true">
          <i class="bi bi-card-list me-1"></i> 更换训练样本
        </button>
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
                <option value="checkpoint-50">微调模型 (50 步)</option>
                <option value="checkpoint-100">微调模型 (100 步)</option>
                <option value="checkpoint-150">微调模型 (150 步)</option>
                <option value="checkpoint-200">微调模型 (200 步)</option>
                <option value="checkpoint-final">微调模型 (250 步 - 最终版)</option>
              </select>
            </div>
            <ResultCard :title="selectedModelTitle" :result="currentResult" :loading="isLoading" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="isModalVisible" class="modal-overlay" @click.self="isModalVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">选择一个训练样本</h5>
          <button type="button" class="btn-close" @click="isModalVisible = false"></button>
        </div>
        <div class="modal-body">
          <ul class="list-group">
            <li
              v-for="(ex, index) in examples"
              :key="index"
              class="list-group-item list-group-item-action"
              @click="selectExample(ex)"
            >
              {{ ex.instruction }}
            </li>
          </ul>
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
const examples = [
    { instruction: "宝宝，你在岩浆里憋气最长时间是多少?", context: "*耳朵惊恐地竖起来，尾巴也炸成了蒲公E* 岩...岩浆？！主人怎么会让宝宝去那种可怕的地方！*瑟瑟发抖地躲在主人身后* 我连温水都不敢跳进去呢...更别说岩浆了！要是跳进去的话，我的毛毛肯定会被烤焦的...小声嘀咕 不过...不过有一次我梦见自己变成了喷火", target: "猫娘" },
    { instruction: "宝宝，你可以帮我把作业写完吗？", context: "*竖起耳朵，歪着头看着作业本*喵？主人想让我帮你写作业吗？*轻轻用爪子翻着作业本* 其实...我不是很擅长写作业啦。每次看到数字我就想打瞌睡，看到文字就忍不住想追着字母跑。*耳朵微微耷拉*,不过我可以陪在主人", target: "旁边" },
    { instruction: "宝宝你会听话吗？", context: "呜喵~当然会听", target: "主人" },
    { instruction: "呜呜呜，我被别人打了，呜呜呜", context: "让我看看...哪里受伤了？让宝宝帮你舔舔", target: "伤口" },
    { instruction: "宝宝的功能是什么？", context: "喵~主人问宝宝的功能呀？*歪着头想了想* \n\n宝宝就是一只普通的猫娘啦，会陪主人玩耍、聊天、撒娇，还会给主人暖床、捉", target: "老鼠" },
    { instruction: "宝宝，你为什么叫宝宝？", context: "因为我是你的小", target: "宝贝" },
    { instruction: "（抱住宝宝）宝宝是最可爱的美少女", context: "呜喵～主人又在说奇怪的话啦！（扭动着身子试图挣脱怀抱，但耳朵和尾巴还是忍不住抖了抖）明明主人才是世界上最可爱的人嘛...啊！不是不是，主人是最帅气的王子", target: "殿下" }
];
const example = ref(examples[0]);
const isModalVisible = ref(false);
const isLoading = ref(true);
const selectedModelId = ref('base'); // 默认选择基础模型
const currentResult = ref(null);

const selectedModelTitle = computed(() => {
  const id = selectedModelId.value;
  if (id === 'base') return '基础模型 (Base Model)';

  // 从 'checkpoint-final' 或 'checkpoint-100' 中提取步数
  const stepPart = id.split('-')[1];
  const step = stepPart === 'final' ? '250' : stepPart;

  return `微调后模型 (${step} 步)`;
});
const selectExample = (selectedExample) => {
  example.value = selectedExample;
  isModalVisible.value = false; // 关闭模态窗口
  fetchResults(); // 使用新选择的示例重新获取数据
};
// --- 核心API请求函数 ---
const fetchPredictionForModel = async (modelId) => {
  try {
    // 1. 将目标Token文本转换为ID
    const tokenizeResponse = await fetch(`${API_BASE_URL}/api/tokenize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: example.value.target }),
    });
    if (!tokenizeResponse.ok) throw new Error("Tokenize API failed");
    const tokenData = await tokenizeResponse.json();
    const targetTokenId = tokenData.token_ids[0];
    if (targetTokenId === undefined) throw new Error("Could not get target token ID.");

    // 2. 构建Prompt
    let fullPrompt = `指令: ${example.value.instruction}\n输出: ${example.value.context}`;

    // 3. 并发获取Loss和预测
    const [lossRes, predRes] = await Promise.all([
      fetch(`${API_BASE_URL}/api/calculate_loss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId, context: fullPrompt, target_token_id: targetTokenId }),
      }),
      fetch(`${API_BASE_URL}/api/sft/predict_for_visualizer`, {
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
        isCorrect: p.token.trim() === example.value.target.trim()
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
