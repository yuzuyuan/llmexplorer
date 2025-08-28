<template>
  <div class="container-fluid">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">Prompt 对比试验台</h1>
      <p class="lead text-muted">在游戏中掌握与LLM高效对话的艺术，成为Prompt工程师！</p>
    </div>

    <div class="card shadow-sm">
      <div class="card-header bg-light">
        <h4 class="mb-0">挑战任务：邮件助手</h4>
      </div>
      <div class="card-body p-4">
        <div class="row">
          <div class="col-md-4">
            <h5><i class="bi bi-joystick"></i> 游戏目标</h5>
            <p>你是一位邮件助手，需要根据给出的要点，生成一封专业、礼貌且简洁的会议邀请邮件。</p>
            <div class="alert alert-info">
              <h6 class="fw-bold">邮件要点：</h6>
              <ul class="mb-0 small">
                <li>主题：第二季度产品规划会</li>
                <li>时间：下周三下午2点</li>
                <li>地点：301会议室</li>
                <li>参会人：产品部、研发部负责人</li>
                <li>目的：同步Q2目标，讨论新功能</li>
              </ul>
            </div>
            <p class="mt-3">一个好的Prompt应该清晰、具体。请尝试不同的Prompt，让“裁判模型”给你打出高分！</p>
          </div>
          <div class="col-md-8">
            <div class="mb-3">
              <label for="prompt-input" class="form-label fw-bold">你的 Prompt:</label>
              <textarea id="prompt-input" class="form-control" rows="5" placeholder="例如：请根据以下要点写一封会议邀请邮件..." v-model="prompt"></textarea>
            </div>
            <button class="btn btn-primary w-100 btn-lg" @click="generateOutput" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm"></span> {{ loading ? '生成并评分中...' : '生成并获取评分' }}
            </button>
            <div v-if="result" class="mt-4">
              <hr />
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">裁判评分</h5>
                <span class="badge rounded-pill fs-4" :class="scoreBadgeClass">{{ result.score }}/100</span>
              </div>
              <div class="progress mt-2" style="height: 25px;">
                <div class="progress-bar" :class="scoreProgressClass" :style="{ width: result.score + '%' }"></div>
              </div>
              <p class="small text-muted mt-1">{{ result.feedback }}</p>
              <h5 class="mt-4">模型输出</h5>
              <div class="p-3 border rounded bg-light">
                <pre style="white-space: pre-wrap; word-wrap: break-word; font-family: inherit;">{{ result.output }}</pre>
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

const prompt = ref('');
const loading = ref(false);
const result = ref(null);

const generateOutput = () => {
  if (!prompt.value) return;
  loading.value = true;
  result.value = null;
  setTimeout(() => {
    let score = 30;
    let feedback = '评分较低。提示词可能不够清晰，导致邮件格式或内容有欠缺。';
    let output = `会议通知：下周三下午2点在301开会，关于Q2产品规划，请产品部和研发部负责人参加。`;
    const p = prompt.value.toLowerCase();
    if (p.includes('邮件') && p.includes('邀请')) score += 20;
    if (p.includes('专业') || p.includes('正式')) score += 15;
    if (p.includes('角色') || p.includes('扮演')) score += 10;
    if (p.includes('简洁')) score += 5;
    if (score >= 80) {
      feedback = '非常棒的Prompt！清晰、具体，包含了角色、任务和风格要求，生成了高质量的邮件。';
      output = `标题：诚邀参加第二季度产品规划会议\n\n尊敬的产品部、研发部负责人：\n\n您好！\n\n我们计划于下周三下午2点，在301会议室召开第二季度产品规划会议。\n\n本次会议旨在同步第二季度的核心目标，并深入讨论即将开发的新功能特性。您的参与对我们至关重要。\n\n期待您的莅临！\n\n祝好，\n[您的姓名]`;
    } else if (score >= 50) {
      feedback = '不错的尝试！Prompt提供了基本信息，但可以更具体，比如指定语气或格式。';
      output = `标题：第二季度产品规划会邀请\n时间：下周三下午2点\n地点：301会议室\n参会人：产品部、研发部负责人\n\n大家好，\n邀请各位参加Q2产品规划会，讨论目标和新功能。\n请准时参加。`;
    }
    result.value = { score, feedback, output };
    loading.value = false;
  }, 1500);
};

const scoreBadgeClass = computed(() => {
  if (!result.value) return 'bg-secondary';
  if (result.value.score >= 80) return 'bg-success';
  if (result.value.score >= 50) return 'bg-warning text-dark';
  return 'bg-danger';
});
const scoreProgressClass = computed(() => {
  if (!result.value) return '';
  if (result.value.score >= 80) return 'bg-success';
  if (result.value.score >= 50) return 'bg-warning';
  return 'bg-danger';
});
</script>

<style scoped>
pre { font-size: 0.95rem; }
.progress-bar { transition: width 0.5s ease-in-out; }
</style>