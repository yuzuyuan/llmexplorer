<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h2>用户账户</h2>
          </div>
          <div class="card-body">
            <div v-if="currentUser">
              <p><strong>用户名:</strong> {{ currentUser.username }}</p>
              <p><strong>邮箱:</strong> {{ currentUser.email }}</p>
            </div>
            <hr />
            <h4>成就</h4>
            <div v-if="achievements.length > 0">
              <ul>
                <li v-for="achievement in achievements" :key="achievement.id">
                  {{ achievement.name }} - {{ achievement.description }}
                </li>
              </ul>
            </div>
            <div v-else>
              <p>暂无成就，继续探索吧！</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getAchievements, initializeAchievements } from '../services/achievementService';

const currentUser = ref(null);
const achievements = ref([]);

onMounted(() => {
  const user = JSON.parse(localStorage.getItem('currentUser'));
  if (user) {
    currentUser.value = user;
    initializeAchievements(user.email);
    achievements.value = getAchievements(user.email);
  }
});
</script>

<style scoped>
.card {
  margin-top: 20px;
}
</style>
