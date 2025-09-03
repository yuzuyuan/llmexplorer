<template>
  <div class="card shadow-sm">
    <div class="card-header bg-light d-flex justify-content-between align-items-center">
      <h4 class="mb-0">1. 微调数据集</h4>
      <span class="text-muted">样本 {{ currentIndex + 1 }} / {{ dataset.length }}</span>
    </div>
    <div class="card-body p-4">
      <div v-if="currentItem" class="dataset-item">
        <div class="mb-3">
          <strong class="d-block text-primary">指令 (Instruction):</strong>
          <p class="bg-light p-2 rounded">{{ currentItem.instruction }}</p>
        </div>
        <div v-if="currentItem.input" class="mb-3">
          <strong class="d-block text-success">输入 (Input):</strong>
          <p class="bg-light p-2 rounded">{{ currentItem.input }}</p>
        </div>
        <div>
          <strong class="d-block text-info">正确回答 (Output):</strong>
          <p class="bg-light p-2 rounded">{{ currentItem.output }}</p>
        </div>
      </div>
    </div>
    <div class="card-footer d-flex justify-content-center gap-3">
      <button class="btn btn-secondary" @click="prevItem" :disabled="currentIndex === 0">
        <i class="bi bi-arrow-left"></i> 上一个样本
      </button>
      <button class="btn btn-secondary" @click="nextItem" :disabled="currentIndex === dataset.length - 1">
        下一个样本 <i class="bi bi-arrow-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineEmits } from 'vue';
import dataset from '@/../backend/sft/cat_sft/cat.json';

const emit = defineEmits(['item-selected']);
const currentIndex = ref(0);
const currentItem = computed(() => dataset[currentIndex.value]);

const prevItem = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

const nextItem = () => {
  if (currentIndex.value < dataset.length - 1) {
    currentIndex.value++;
  }
};

// 当选中项变化时，通知父组件
watch(currentItem, (newItem) => {
  emit('item-selected', newItem);
}, { immediate: true });
</script>

<style scoped>
.dataset-item p {
  white-space: pre-wrap;
  word-break: break-all;
  margin-bottom: 0;
}
</style>