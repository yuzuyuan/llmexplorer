<template>
  <div class="container-fluid">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">“迷你模型”训练模拟器</h1>
      <p class="lead text-muted">通过“训练前后”的巨大反差，直观地理解SFT的作用。</p>
    </div>

    <div class="row g-4">
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-header bg-light"><h4 class="mb-0">阶段一：准备训练数据 (猫娘风格)</h4></div>
          <div class="card-body" style="max-height: 200px; overflow-y: auto;">
            <div v-if="trainingData.length > 0"><pre class="small">{{ JSON.stringify(trainingData, null, 2) }}</pre></div>
            <div v-else class="text-center text-muted">加载训练数据中...</div>
          </div>
        </div>
      </div>
      <div class="col-12 text-center">
        <button class="btn btn-success btn-lg" @click="startFinetuning" :disabled="isTuning || tunedModelReady">
          <i class="bi bi-rocket-takeoff"></i> {{ tunedModelReady ? '微调已完成' : '阶段二：开始微调' }}
        </button>
        <div v-if="isTuning" class="progress mt-3 w-50 mx-auto" style="height: 20px;">
          <div class="progress-bar progress-bar-striped progress-bar-animated" :style="{width: tuningProgress + '%'}">{{ tuningProgress }}%</div>
        </div>
      </div>
      <div class="col-md-6">
        <ChatInterface title="阶段〇：体验基础模型" :messages="baseModelMessages" @send="handleBaseModelSend" />
      </div>
      <div class="col-md-6">
        <ChatInterface title="阶段三：体验微调后模型" :messages="tunedModelMessages" :disabled="!tunedModelReady" @send="handleTunedModelSend" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineAsyncComponent } from 'vue';

const trainingData = ref([]);
const isTuning = ref(false);
const tuningProgress = ref(0);
const tunedModelReady = ref(false);
const baseModelMessages = ref([{ from: 'bot', text: '你好，我是通用基础模型，有什么可以帮助你？' }]);
const tunedModelMessages = ref([{ from: 'bot', text: '请先点击“开始微调”按钮来激活我。' }]);

// 注意：这里我们假设 ChatInterface.vue 位于 src/components/ 目录下
const ChatInterface = defineAsyncComponent(() => import('../../components/ChatInterface.vue'));

onMounted(async () => {
  try {
    const response = await fetch('/data/cat.json');
    trainingData.value = await response.json();
  } catch (e) { console.error("Failed to load training data:", e); }
});

const startFinetuning = () => {
  isTuning.value = true;
  tuningProgress.value = 0;
  const interval = setInterval(() => {
    tuningProgress.value += 10;
    if (tuningProgress.value >= 100) {
      clearInterval(interval);
      isTuning.value = false;
      tunedModelReady.value = true;
      tunedModelMessages.value = [{ from: 'bot', text: '喵~微调完成！现在我是可爱的猫娘啦，快来和我对话吧喵~' }];
    }
  }, 300);
};

const handleBaseModelSend = (message) => {
  baseModelMessages.value.push({ from: 'user', text: message });
  setTimeout(() => {
    let reply = '我正在处理您的请求。';
    if (message.includes('你好')) reply = '你好。';
    else if (message.includes('名字')) reply = '我是一个大型语言模型，没有名字。';
    else if (message.includes('天气')) reply = '我无法获取实时天气信息。';
    baseModelMessages.value.push({ from: 'bot', text: reply });
  }, 500);
};

const handleTunedModelSend = (message) => {
  tunedModelMessages.value.push({ from: 'user', text: message });
  setTimeout(() => {
    let reply = '嗯...什么喵？';
    if (message.includes('你好')) reply = '你好喵~有什么可以帮你的喵？';
    else if (message.includes('名字')) reply = '我是一只可爱的猫娘，你可以叫我喵酱~';
    else if (message.includes('天气')) reply = '今天天气很好喵，最适合晒太阳了~';
    tunedModelMessages.value.push({ from: 'bot', text: reply });
  }, 500);
};
</script>