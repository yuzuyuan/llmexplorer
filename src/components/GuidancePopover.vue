<template>
  <div class="guidance-card shadow-lg">
    <h5 class="guidance-header">{{ title }}</h5>
    <div class="guidance-body" v-html="renderedContent"></div>
    <div class="p-2 text-end">
        <button @click="$emit('confirm')" class="btn btn-primary btn-sm">{{ buttonText }}</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { marked } from 'marked'; // 1. 引入 marked 库

const props = defineProps({
  title: String,
  content: String,
  buttonText: String,
});

defineEmits(['confirm']);

// 2. 创建一个计算属性，用于将传入的 content 字符串解析为 HTML
const renderedContent = computed(() => {
  if (props.content) {
    return marked.parse(props.content);
  }
  return '';
});
</script>

<style scoped>
.guidance-card {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 320px;
  z-index: 1050; 
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: .3rem;
  animation: fadeIn 0.3s ease-in-out;
}
.guidance-header {
  padding: .8rem 1rem;
  margin: 0;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  border-top-left-radius: .3rem;
  border-top-right-radius: .3rem;
}
.guidance-body {
  padding: 1rem;
}
/* :deep() 选择器可以确保样式能应用到 v-html 生成的内容上 */
.guidance-body :deep(strong) {
  color: #0d6efd;
}
.guidance-body :deep(p) {
  margin-bottom: 0; /* 移除 marked 可能添加的默认 p 标签边距 */
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>