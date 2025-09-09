<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h2 class="mb-4">Login</h2>
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" v-model="formData.email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <div class="input-group">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="form-control"
              id="password"
              v-model="formData.password"
              required
            />
            <button class="btn btn-outline-secondary" type="button" @click="togglePassword">
              <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
        </div>
        <div class="mb-3 form-check">
          <input
            type="checkbox"
            class="form-check-input"
            id="remember"
            v-model="formData.remember"
          />
          <label class="form-check-label" for="remember">Remember me</label>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <router-link to="/register" class="btn btn-link ms-2">Don't have an account? Register now</router-link>
        <a href="#" class="ms-3">Forgot password?</a>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const formData = reactive({
  email: '',
  password: '',
  remember: false,
})

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = () => {
  loading.value = true
  error.value = ''

  try {
    // 获取用户数据
    const users = JSON.parse(localStorage.getItem('users') || '{}')
    const user = users[formData.email]

    // 验证用户
    if (!user || user.password !== formData.password) {
      throw new Error('邮箱或密码错误')
    }

    // 保存当前用户信息
    const currentUser = {
      username: user.username,
      email: user.email,
    }

    localStorage.setItem('currentUser', JSON.stringify(currentUser))

    // 如果选择了"记住我"，保存到 localStorage
    if (formData.remember) {
      localStorage.setItem(
        'rememberedUser',
        JSON.stringify({
          email: user.email,
        }),
      )
    }

    // 跳转到账户页面
    router.push('/account')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
