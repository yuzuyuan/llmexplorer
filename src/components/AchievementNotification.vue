<template>
  <Transition name="achievement-fade">
    <div v-if="isVisible" class="achievement-notification alert alert-info shadow-lg d-flex align-items-center" role="alert">
      <i :class="['bi', achievement.icon, 'achievement-icon me-3']"></i>
      <div>
        <h5 class="alert-heading mb-1">成就解锁！</h5>
        <p class="mb-0">你解锁了 <strong>{{ achievement.title }}</strong>！</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  achievement: {
    type: Object,
    required: true,
  },
  duration: {
    type: Number,
    default: 3000, // 默认显示3秒
  },
});

const isVisible = ref(false);
let hideTimeout = null;

const showNotification = () => {
  isVisible.value = true;
  if (hideTimeout) clearTimeout(hideTimeout); // 清除旧的定时器
  hideTimeout = setTimeout(() => {
    isVisible.value = false;
  }, props.duration);
};

// 监听 achievement 变化，当有新成就传入时显示
watch(() => props.achievement, (newVal) => {
  if (newVal && newVal.id) { // 确保有实际的成就对象
    showNotification();
  }
}, { immediate: true }); // immediate: true 确保组件挂载时如果已有成就就显示

// 当组件卸载时清除定时器，避免内存泄露
onMounted(() => {
  if (props.achievement && props.achievement.id) {
    showNotification();
  }
});
</script>

<style scoped>
.achievement-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 300px; /* 固定宽度 */
  background-color: #d1ecf1; /* 信息蓝色背景 */
  border-color: #bee5eb;
  color: #0c5460;
  border-radius: 0.5rem;
  z-index: 2000; /* 确保在最上层 */
  padding: 1rem 1.25rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  display: flex; /* 使用flexbox对齐图标和文本 */
  align-items: center; /* 垂直居中对齐 */
}

.achievement-icon {
  font-size: 2.5rem; /* 增大图标 */
  color: #0d6efd; /* 图标颜色 */
  margin-right: 1rem;
}

.alert-heading {
  font-size: 1.1rem; /* 标题稍小一点 */
  font-weight: bold;
}

/* Vue Transition 动画样式 */
.achievement-fade-enter-active,
.achievement-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* 弹性动画 */
}

.achievement-fade-enter-from,
.achievement-fade-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8); /* 从右侧滑入，并略微缩小 */
}

.achievement-fade-enter-to,
.achievement-fade-leave-from {
  opacity: 1;
  transform: translateX(0) scale(1);
}
</style>
