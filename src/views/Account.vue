<template>
  <div class="container my-5">
    <div v-if="user" class="card shadow-sm">
      <div class="card-header bg-light">
        <h2 class="mb-0">欢迎, {{ user.username }}!</h2>
      </div>
      <div class="card-body">
        <p><strong>邮箱:</strong> {{ user.email }}</p>
        <hr>
        <h3 class="mt-4">我的成就</h3>
        <div v-if="achievements.length > 0" class="row">
          <div v-for="achievement in achievements" :key="achievement.id" class="col-md-6 col-lg-4 mb-3">
            <div class="card h-100" :class="{ 'border-success': achievement.unlocked }">
              <div class="card-body text-center">
                <h5 class="card-title">{{ achievement.title }}</h5>
                <p class="card-text text-muted">{{ achievement.description }}</p>
                <p v-if="achievement.unlocked" class="text-success fw-bold">已解锁!</p>
                <p v-else class="text-secondary">未解锁</p>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="text-muted">还没有获得任何成就，继续探索吧！</p>
      </div>
    </div>
    <div v-else class="alert alert-warning">
      请先 <router-link to="/login">登录</router-link> 查看您的账户信息。
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAchievements } from '@/composables/useAchievements';

const user = ref(null);
const { achievements } = useAchievements();

onMounted(() => {
  const currentUser = localStorage.getItem('currentUser');
  if (currentUser) {
    user.value = JSON.parse(currentUser);
  }
});
</script>
