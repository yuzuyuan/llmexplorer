<template>
  <div class="container-fluid">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">SFT 训练模拟与体验</h1>
      <p class="lead text-muted">通过高保真模拟和真实模型切换，直观感受微调的力量。</p>
    </div>

    <div class="card shadow-sm mb-5">
      <div class="card-header bg-light">
        <h4 class="mb-0">阶段一：高保真训练过程模拟</h4>
      </div>
      <div class="card-body p-4">
        <div class="text-center mb-3">
          <button class="btn btn-success btn-lg" @click="startSimulation" :disabled="isPlaying || simulationDone">
            <i class="bi bi-play-fill"></i> {{ simulationDone ? '模拟已完成' : '开始模拟训练' }}
          </button>
        </div>
        <div v-if="trainingLogs.length > 0" class="row align-items-center">
          <div class="col-lg-8">
            <div ref="chartContainer" style="height: 300px; width: 100%;"></div>
          </div>
          <div class="col-lg-4">
            <h5 class="text-center">实时指标</h5>
            <ul class="list-group">
              <li class="list-group-item d-flex justify-content-between align-items-center">
                训练步数 (Step)
                <span class="badge bg-primary rounded-pill fs-6">{{ currentStep }} / 250</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                训练损失 (Loss)
                <span class="badge bg-danger rounded-pill fs-6">{{ currentLoss.toFixed(4) }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                学习率 (LR)
                <span class="badge bg-info text-dark rounded-pill fs-6">{{ currentLR.toExponential(1) }}</span>
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="text-center text-muted p-5">
          <div class="spinner-border" role="status"></div>
          <p class="mt-2">正在加载训练日志...</p>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-header bg-light">
        <h4 class="mb-0">阶段二：与不同阶段的模型对话</h4>
      </div>
      <div class="card-body p-4">
        <label for="checkpoint-slider" class="form-label">**拖动滑块，选择不同训练阶段的模型进行对话：**</label>
        <div class="d-flex align-items-center gap-3">
            <span class="fw-bold">基础模型</span>
            <input type="range" class="form-range" min="0" :max="checkpoints.length - 1" :step="1" id="checkpoint-slider" v-model.number="selectedCheckpointIndex">
            <span class="fw-bold text-success">完全体 (250步)</span>
        </div>
        <div class="text-center mt-2">
            当前选择: <span class="badge fs-6" :class="selectedModelId === 'base' ? 'bg-secondary' : 'bg-success'">{{ selectedModelName }}</span>
        </div>
        <hr/>
        <div class="row g-4 mt-2">
          <div class="col-12">
            <ChatInterface
              :title="`正在与 ${selectedModelName} 对话`"
              :messages="chatMessages"
              :disabled="isChatting"
              @send="handleChatSend"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineAsyncComponent, watch } from 'vue';
import * as echarts from 'echarts';

// --- 组件和状态定义 ---
const ChatInterface = defineAsyncComponent(() => import('../../components/ChatInterface.vue'));

const trainingLogs = ref([]);
const goldenPredictions = ref({});
const chartContainer = ref(null);
let chartInstance = null;

// 模拟状态
const isPlaying = ref(false);
const simulationDone = ref(false);
const currentStep = ref(0);
const currentLoss = ref(0);
const currentLR = ref(0);

// 对话状态
const checkpoints = ref(['base', 'checkpoint-50', 'checkpoint-100', 'checkpoint-150', 'checkpoint-200', 'checkpoint-250']);
const selectedCheckpointIndex = ref(0);
const chatMessages = ref([]);
const isChatting = ref(false);

// --- 计算属性 ---
const selectedModelId = computed(() => checkpoints.value[selectedCheckpointIndex.value]);
const selectedModelName = computed(() => {
    const id = selectedModelId.value;
    if (id === 'base') return '基础模型';
    return `微调模型 (${id.split('-')[1]} 步)`;
});


// --- 数据获取 ---
onMounted(async () => {
  try {
    const [logsRes, predsRes] = await Promise.all([
      fetch('http://127.0.0.1:8000/api/sft/training_logs'),
      fetch('http://127.0.0.1:8000/api/sft/golden_predictions'),
    ]);
    trainingLogs.value = await logsRes.json();
    goldenPredictions.value = await predsRes.json();
    
    // 初始化图表
    initChart();
  } catch (error) {
    console.error("加载SFT数据失败:", error);
  }
});

// --- ECharts 图表 ---
const initChart = () => {
  if (chartContainer.value) {
    chartInstance = echarts.init(chartContainer.value);
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value', name: 'Step' },
      yAxis: { type: 'value', name: 'Loss', min: 0, max: 4 },
      series: [{ data: [], type: 'line', smooth: true, showSymbol: false }],
      grid: { left: '10%', right: '5%', bottom: '15%' }
    };
    chartInstance.setOption(option);
  }
};

// --- 模拟动画 ---
const startSimulation = () => {
  if (isPlaying.value || !chartInstance) return;
  isPlaying.value = true;
  simulationDone.value = false;
  
  let logIndex = 0;
  chartInstance.setOption({ series: [{ data: [] }] }); // 清空图表

  const interval = setInterval(() => {
    if (logIndex >= trainingLogs.value.length) {
      clearInterval(interval);
      isPlaying.value = false;
      simulationDone.value = true;
      return;
    }
    const log = trainingLogs.value[logIndex];
    currentStep.value = log.step;
    currentLoss.value = log.loss;
    currentLR.value = log.learning_rate;
    
    chartInstance.appendData({
        seriesIndex: 0,
        data: [[log.step, log.loss]]
    });
    
    logIndex++;
  }, 50); // 每50ms播放一帧
};

// --- 对话逻辑 ---
const handleChatSend = async (message) => {
  chatMessages.value.push({ from: 'user', text: message });
  isChatting.value = true;
  
  // 不再发送历史记录，只发送当前用户输入
  // const currentHistory = chatMessages.value.map(msg => ({ role: msg.from === 'user' ? 'user' : 'assistant', content: msg.text }));
  
  try {
    const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prompt: message, // 只发送 prompt 字段
            model_id: selectedModelId.value
        })
    });
    if (!response.ok) { // 捕获 422 等错误
        throw new Error(`API 请求失败，状态码: ${response.status}`);
    }
    const data = await response.json();
    chatMessages.value.push({ from: 'bot', text: data.reply });
  } catch (error) {
    console.error("对话API调用失败:", error);
    chatMessages.value.push({ from: 'bot', text: `抱歉，模型连接失败。(${error.message})` });
  } finally {
    isChatting.value = false;
  }
};

watch(selectedModelId, (newId, oldId) => {
    // 增加一个判断，避免组件初始化时触发不必要的重置
    if (newId !== oldId) {
        chatMessages.value = [{from: 'bot', text: `你好！我是${selectedModelName.value}，有什么可以帮你的吗？`}];
    }
}, { immediate: true }); // immediate: true 保证首次加载时设置欢迎语
</script>