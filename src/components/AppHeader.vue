<template>
  <header class="app-header">
    <div class="container header-container">
      <router-link to="/" class="logo">
        <img src="@/assets/images/bot-avatar.png" alt="LLM Explorer Logo" class="logo-img" />
        <span class="logo-text">LLM Explorer</span>
      </router-link>
      <nav class="main-nav">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/kb/1-llm-basics" class="nav-link">LLM Basics</router-link>
        <router-link to="/kb/2-prompt-engineering" class="nav-link">Prompt Engineering</router-link>
        <router-link to="/kb/3-rag" class="nav-link">RAG</router-link>
        <router-link to="/kb/4-sft" class="nav-link">Fine-Tuning</router-link>
        <router-link to="/transformer-trainer" class="nav-link">Transformer Builder</router-link>
        <router-link to="/quiz" class="nav-link">知识测验</router-link>
        <router-link to="/team" class="nav-link">Our Team</router-link>
      </nav>
      <div class="header-actions">
        <div class="dropdown">
          <button class="btn btn-light rounded-circle" type="button" @click="handleUserIconClick">
            <i class="bi bi-person-circle fs-4"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const user = ref(null);
const router = useRouter();

const checkUserStatus = () => {
  const currentUser = localStorage.getItem('currentUser');
  user.value = currentUser ? JSON.parse(currentUser) : null;
};

const handleUserIconClick = () => {
  if (user.value) {
    router.push('/account');
  } else {
    router.push('/auth');
  }
};

onMounted(() => {
  checkUserStatus();
  window.addEventListener('storage', checkUserStatus);
});

onUnmounted(() => {
  window.removeEventListener('storage', checkUserStatus);
});
</script>

<style scoped>
.header-actions .btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}
/* 其他样式保持不变 */
.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.8);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #111827;
}

.logo-img {
  height: 40px;
  width: 40px;
  margin-right: 0.75rem;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
}

.main-nav {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  text-decoration: none;
  color: #4b5563;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: color 0.3s ease, border-color 0.3s ease;
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}
</style>
