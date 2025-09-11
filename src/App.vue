<template>
  <div id="app">
    <AppHeader />
    <router-view />
    <AppFooter />

    <AchievementNotification
      v-if="currentAchievement"
      :achievement="currentAchievement"
      :duration="4000"
      @after-leave="clearAchievement"
    />
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
import AchievementNotification from './components/AchievementNotification.vue'; // 导入通知组件

// --- 新增：用于成就通知的状态 ---
const currentAchievement = ref(null); // 存储当前要显示的成就
let notificationQueue = []; // 成就队列
let isShowingNotification = ref(false); // 是否正在显示通知

// 处理成就解锁事件
const handleAchievementUnlocked = (event) => {
  const achievement = event.detail;
  notificationQueue.push(achievement); // 将成就添加到队列
  showNextAchievement(); // 尝试显示下一个成就
};

const showNextAchievement = () => {
  if (notificationQueue.length > 0 && !isShowingNotification.value) {
    isShowingNotification.value = true;
    currentAchievement.value = notificationQueue.shift(); // 取出队列中的第一个成就
    // AchievementNotification 组件会监听 currentAchievement 的变化并显示
    // 并在 duration 后自行清除 currentAchievement
  }
};

// AchievementNotification 组件在动画结束后会触发此方法来清除 currentAchievement
const clearAchievement = () => {
  currentAchievement.value = null;
  isShowingNotification.value = false;
  // 在当前通知消失后，尝试显示队列中的下一个通知
  showNextAchievement();
};
// --- 结束新增 ---


onMounted(() => {
  // --- 新增：注册全局事件监听器 ---
  window.addEventListener('achievementUnlocked', handleAchievementUnlocked);
  // --- 结束新增 ---
});

onUnmounted(() => {
  // --- 新增：移除全局事件监听器 ---
  window.removeEventListener('achievementUnlocked', handleAchievementUnlocked);
  // --- 结束新增 ---
});
</script>

<style>
/* ... 保持你已有的全局样式 ... */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex-grow: 1;
}
</style>
