<template>
  <div class="card h-100">
    <div class="card-header bg-light">
      <h5 class="mb-0">{{ title }}</h5>
    </div>
    <div class="card-body">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div v-else-if="result">
        <div class="text-center mb-4">
          <h6 class="text-muted">模型 Loss (差距)</h6>
          <div :class="lossClass" class="loss-display mx-auto">
            {{ result.loss.toFixed(2) }}
          </div>
          <p class="small text-muted mt-2">{{ lossDescription }}</p>
        </div>
        <div>
          <h6 class="text-muted">模型 Top 5 预测</h6>
          <div class="d-flex flex-column gap-2">
            <div v-for="p in result.predictions" :key="p.token" class="row g-2 align-items-center">
              <div class="col-4 text-end">
                <span class="fw-bold" :class="{ 'text-success': p.isCorrect, 'text-danger': !p.isCorrect }">
                  {{ p.token.replace(/\n/g, "\\n") }}
                  <i v-if="p.isCorrect" class="bi bi-check-circle-fill ms-1"></i>
                </span>
              </div>
              <div class="col-8">
                <div class="progress" style="height: 24px;">
                  <div class="progress-bar" :style="{ width: p.probability + '%' }">{{ p.probability }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-5 text-muted">
        (无结果)
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue';

const props = defineProps({
  title: String,
  result: Object,
  loading: Boolean,
});

const lossClass = computed(() => {
  if (!props.result) return '';
  const loss = props.result.loss;
  if (loss > 5) return 'loss-high';
  if (loss > 2) return 'loss-medium';
  return 'loss-low';
});

const lossDescription = computed(() => {
  if (!props.result) return '';
  const loss = props.result.loss;
  if (loss > 5) return '差距巨大，模型完全预测错了。';
  if (loss > 2) return '有一定差距，模型感到困惑。';
  return '差距很小，模型预测得很好！';
});
</script>

<style scoped>
.loss-display {
  font-size: 2rem;
  font-weight: bold;
  padding: 1rem;
  border-radius: 50%;
  width: 90px;
  height: 90px;
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
