<template>
  <header class="navbar">
    <div class="container navbar-container">
      <router-link to="/" class="navbar-brand">ScienceLab</router-link>

      <div class="nav-menu" :class="{ active: isMenuOpen }">
        <div class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/articles" class="nav-link">文章</router-link>
          <router-link to="/team" class="nav-link">关于我们</router-link>
        </div>

        <div class="search-container">
          <i class="bi bi-search search-icon"></i>
          <input
            type="text"
            class="search-input"
            placeholder="搜索..."
            v-model="searchQuery"
            @keyup.enter="handleSearch"
          />
        </div>

        <template v-if="currentUser">
          <div class="dropdown">
            <div class="user-avatar">
              {{ getUserInitials(currentUser.username) }}
            </div>
            <div class="dropdown-menu">
              <span class="dropdown-item">欢迎, {{ currentUser.username }}</span>
              <hr class="dropdown-divider" />
              <button class="dropdown-item" @click="handleLogout">退出登录</button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="nav-link">登录</router-link>
          <router-link to="/register" class="nav-link">注册</router-link>
        </template>
      </div>

      <div class="hamburger" @click="toggleMenu">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isMenuOpen = ref(false)
const searchQuery = ref('')
const currentUser = ref(null)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const getUserInitials = (username) => {
  if (!username) return '??'
  return username.substring(0, 2).toUpperCase()
}

const checkLoginStatus = () => {
  const user = localStorage.getItem('currentUser')
  if (user) {
    try {
      currentUser.value = JSON.parse(user)
    } catch (e) {
      console.error('解析用户信息失败:', e)
      localStorage.removeItem('currentUser')
    }
  }
}

const handleLogout = () => {
  localStorage.removeItem('currentUser')
  currentUser.value = null
  router.push('/login')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 这里可以实现搜索功能
    console.log('搜索:', searchQuery.value)
  }
}

onMounted(() => {
  checkLoginStatus()

  router.afterEach(() => {
    checkLoginStatus()
    isMenuOpen.value = false
  })
})
</script>