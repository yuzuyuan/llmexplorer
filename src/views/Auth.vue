<template>
  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow-sm">
          <div class="card-body p-5">
            <h2 class="text-center mb-4">{{ isLogin ? '登录' : '注册' }}</h2>

            <form v-if="isLogin" @submit.prevent="handleLogin">
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <div class="mb-3">
                <label for="email" class="form-label">邮箱</label>
                <input type="email" class="form-control" id="email" v-model="formData.email" required />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input type="password" class="form-control" id="password" v-model="formData.password" required />
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? '登录中...' : '登录' }}
              </button>
              <p class="text-center mt-3">
                没有账户？ <a href="#" @click.prevent="isLogin = false">立即注册</a>
              </p>
            </form>

            <form v-else @submit.prevent="handleRegister">
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
               <div v-if="message" class="alert alert-success">{{ message }}</div>
              <div class="mb-3">
                <label for="reg-username" class="form-label">用户名</label>
                <input type="text" class="form-control" id="reg-username" v-model="formData.username" required />
              </div>
              <div class="mb-3">
                <label for="reg-email" class="form-label">邮箱</label>
                <input type="email" class="form-control" id="reg-email" v-model="formData.email" required />
              </div>
              <div class="mb-3">
                <label for="reg-password" class="form-label">密码</label>
                <input type="password" class="form-control" id="reg-password" v-model="formData.password" required />
              </div>
              <button type="submit" class="btn btn-success w-100" :disabled="loading">
                {{ loading ? '注册中...' : '注册' }}
              </button>
              <p class="text-center mt-3">
                已有账户？ <a href="#" @click.prevent="isLogin = true">立即登录</a>
              </p>
            </form>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLogin = ref(true);
const loading = ref(false);
const error = ref('');
const message = ref('');

const formData = reactive({
  username: '',
  email: '',
  password: '',
});

// 清空表单和提示信息
const resetForm = () => {
  formData.username = '';
  formData.email = '';
  formData.password = '';
  error.value = '';
  message.value = '';
};

watch(isLogin, resetForm);

const handleLogin = () => {
  loading.value = true;
  error.value = '';
  try {
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    const user = users[formData.email];
    if (!user || user.password !== formData.password) {
      throw new Error('邮箱或密码错误');
    }
    localStorage.setItem('currentUser', JSON.stringify({ username: user.username, email: user.email }));
    router.push('/account');
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const handleRegister = () => {
  loading.value = true;
  error.value = '';
  message.value = '';
  try {
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    if (users[formData.email]) {
      throw new Error('该邮箱已被注册');
    }
    users[formData.email] = {
      username: formData.username,
      password: formData.password,
    };
    localStorage.setItem('users', JSON.stringify(users));
    message.value = '注册成功！请登录。';
    setTimeout(() => {
        isLogin.value = true;
    }, 2000)
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>
