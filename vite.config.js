import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // 将所有 /api 开头的请求代理到 http://127.0.0.1:8000
      '/api': {
        target: 'http://127.0.0.1:8000', // 你的 FastAPI 后端地址
        changeOrigin: true, // 支持跨域
        // 可选：如果你不希望路径中带有 /api，可以重写
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
