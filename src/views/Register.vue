<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <h2 class="mb-4">注册</h2>
      <div v-if="message" class="alert alert-success" role="alert">
        {{ message }}
      </div>
      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="username" class="form-label">用户名</label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="formData.username"
            required
          />
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">邮箱</label>
          <input type="email" class="form-control" id="email" v-model="formData.email" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">密码</label>
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
        <div class="mb-3">
          <label for="confirmPassword" class="form-label">确认密码</label>
          <div class="input-group">
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              class="form-control"
              id="confirmPassword"
              v-model="formData.confirmPassword"
              required
            />
            <button class="btn btn-outline-secondary" type="button" @click="toggleConfirmPassword">
              <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
        </div>
        <div class="mb-3 form-check">
          <input
            type="checkbox"
            class="form-check-input"
            id="agree"
            v-model="formData.agree"
            required
          />
          <label class="form-check-label" for="agree">我同意服务条款</label>
        </div>
        <button type="submit" class="btn btn-success" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status"></span>
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <router-link to="/login" class="btn btn-link ms-2">已有账号？立即登录</router-link>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const message = ref('')
const error = ref('')

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false,
})

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const handleRegister = () => {
  if (formData.password !== formData.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }

  if (!formData.agree) {
    error.value = '请同意服务条款'
    return
  }

  loading.value = true
  error.value = ''
  message.value = ''

  try {
    // 获取现有用户数据
    const users = JSON.parse(localStorage.getItem('users') || '{}')

    // 检查邮箱是否已存在
    if (users[formData.email]) {
      throw new Error('该邮箱已被注册')
    }

    // 保存新用户
    users[formData.email] = {
      username: formData.username,
      email: formData.email,
      password: formData.password, // 实际项目中应该加密
    }

    localStorage.setItem('users', JSON.stringify(users))

    // 显示成功消息
    message.value = '注册完成！'

    // 2秒后跳转到登录页面
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
