<template>
  <div class="markdown-content" v-if="htmlContent" v-html="htmlContent"></div>
  <div v-else class="text-center my-5">
    <div class="spinner-border text-primary" role="status"></div>
    <p class="mt-2">加载中...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'

const route = useRoute()
const htmlContent = ref('')

onMounted(async () => {
  const slug = route.params.slug
  try {
    const mdText = await fetch(`/src/content/${slug}.md`).then((res) => res.text())
    const md = new MarkdownIt()
    htmlContent.value = md.render(mdText)
  } catch (error) {
    htmlContent.value = `<p class="text-danger">内容加载失败: ${error.message}</p>`
  }
})
</script>
