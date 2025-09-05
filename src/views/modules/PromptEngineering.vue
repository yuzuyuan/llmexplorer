<template>
  <div class="prompt-engineering-container" id="prompt-main-card">
    <h2 class="text-center fw-bold mb-4">Prompt Engineering 试验场</h2>
    <div class="row">
      <div class="col-md-4">
        <div class="card h-100" id="prompt-goal">
          <div class="card-body">
            <h5 class="card-title fw-bold">你的挑战任务：邮件助手</h5>
            <p class="card-text">
              你的目标是编写一个高质量的 Prompt，指导 <strong>Qwen3-0.6B 模型</strong> 生成一封专业的会议邀请邮件。
            </p>
            <hr>
            <h6>邮件核心要点:</h6>
            <ul class="list-unstyled">
              <li><i class="bi bi-bullseye text-primary me-2"></i><strong>主题:</strong> 第二季度产品规划</li>
              <li><i class="bi bi-clock text-primary me-2"></i><strong>时间:</strong> 下周三下午2点</li>
              <li><i class="bi bi-geo-alt text-primary me-2"></i><strong>地点:</strong> 301会议室</li>
              <li><i class="bi bi-people text-primary me-2"></i><strong>参会人:</strong> 产品部、研发部负责人</li>
            </ul>
            <hr>
            <h6>高分 Prompt 提示:</h6>
            <p class="small text-muted">
              一个好的 Prompt 通常包含：<br>
              - <strong>角色扮演</strong> (例如: "你是一位专业的行政助理...")<br>
              - <strong>明确任务</strong> (例如: "请写一封会议邀请邮件...")<br>
              - <strong>格式要求</strong> (例如: "邮件应包含标题、正文和落款...")<br>
              - <strong>风格语气</strong> (例如: "语气应正式、礼貌...")
            </p>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title fw-bold">你的 Prompt</h5>
            <div class="mb-3" id="prompt-input-area">
              <textarea
                class="form-control"
                rows="5"
                v-model="prompt"
                placeholder="在这里输入你的指令，指导AI完成任务..."
              ></textarea>
            </div>
            <button class="btn btn-primary w-100" @click="generateOutput" :disabled="loading" id="prompt-generate-button">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ loading ? '生成中...' : '生成并获取评分' }}
            </button>

            <div v-if="result" class="mt-4 result-display-area" id="prompt-result-display">
              <h5 class="fw-bold">结果评估</h5>
              <div class="d-flex align-items-center mb-3">
                <div class="progress w-100" style="height: 25px;">
                  <div
                    :class="scoreProgressClass"
                    role="progressbar"
                    :style="{ width: result.score + '%' }"
                    :aria-valuenow="result.score"
                    aria-valuemin="0"
                    aria-valuemax="100"
                  >
                    <strong>得分: {{ result.score }}</strong>
                  </div>
                </div>
                <span :class="scoreBadgeClass" class="ms-3">{{ result.score >= 80 ? '优秀' : result.score >= 50 ? '良好' : '待改进' }}</span>
              </div>
              <p class="mb-3"><strong><i class="bi bi-chat-right-quote me-1"></i>裁判反馈:</strong> {{ result.feedback }}</p>

              <h6 class="fw-bold mt-4"><i class="bi bi-robot me-1"></i>Qwen3-0.6B 模型生成内容:</h6>
              <div class="generated-output p-3 border rounded bg-light">
                <pre>{{ result.output }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const prompt = ref('请帮我写一封会议邀请邮件，内容应清晰、正式。');
const loading = ref(false);
const result = ref(null);
const API_BASE_URL = 'http://127.0.0.1:8000'; // 确保这个地址与你的后端服务匹配

const generateOutput = async () => {
  if (!prompt.value.trim()) {
    alert('请输入您的 Prompt!');
    return;
  }
  loading.value = true;
  result.value = null;

  try {
    const response = await fetch(`${API_BASE_URL}/api/prompt-eng-judge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt.value }),
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || '与后端服务通信失败');
    }

    result.value = await response.json();

  } catch (error) {
    result.value = {
      score: 0,
      feedback: '调用后端API失败，请检查服务是否正常。',
      output: `错误: ${error.message}`
    };
  } finally {
    loading.value = false;
  }
};

const scoreProgressClass = computed(() => {
  if (!result.value) return 'progress-bar';
  const score = result.value.score;
  if (score >= 80) return 'progress-bar bg-success';
  if (score >= 50) return 'progress-bar bg-warning';
  return 'progress-bar bg-danger';
});

const scoreBadgeClass = computed(() => {
  if (!result.value) return 'badge';
  const score = result.value.score;
  if (score >= 80) return 'badge bg-success-light text-success';
  if (score >= 50) return 'badge bg-warning-light text-warning';
  return 'badge bg-danger-light text-danger';
});
</script>

<style scoped>
.prompt-engineering-container {
  max-width: 1200px;
  margin: auto;
}
.generated-output {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9rem;
  max-height: 300px;
  overflow-y: auto;
}
.result-display-area {
  animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Custom badge colors */
.bg-success-light { background-color: #e6f7f0; }
.text-success { color: #155724 !important; }
.bg-warning-light { background-color: #fff8e1; }
.text-warning { color: #856404 !important; }
.bg-danger-light { background-color: #f8d7da; }
.text-danger { color: #721c24 !important; }
</style>
