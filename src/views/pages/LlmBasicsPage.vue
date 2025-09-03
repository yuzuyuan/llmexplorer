<template>
  <div class="container my-4">
    <div class="row">
      <div class="col-lg-3 d-none d-lg-block">
        <aside class="toc-sidebar">
          <nav v-if="toc.length > 0">
            <h5 class="toc-title">文档内容</h5>
            <ul class="list-unstyled">
              <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
                <a :href="`#${item.id}`" class="toc-link">{{ item.title }}</a>
              </li>
            </ul>
          </nav>
        </aside>
      </div>
      <div class="col-lg-9">
        <div class="mb-5 pb-4 border-bottom">
          <LlmFundamentals />
        </div>
        <div class="mt-4">
          <h2 class="text-center fw-bold mb-4">相关知识文档</h2>
          <div v-html="htmlContent" class="markdown-body"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LlmFundamentals from '../modules/LlmFundamentals.vue';
import { useMarkdown } from '@/composables/useMarkdown.js';
import '@/assets/page-styles.css';

// 正确加载和使用 useMarkdown
const { htmlContent, toc } = useMarkdown('1-llm-basics');
</script>

<style scoped>
/* 侧边栏样式 */
.toc-sidebar {
  position: sticky;
  top: 2rem;
  height: calc(100vh - 4rem);
  overflow-y: auto;
}
.toc-title {
  font-weight: bold;
  margin-bottom: 1rem;
}
.toc-link {
  color: #6c757d;
  text-decoration: none;
  display: block;
  padding: 0.25rem 0;
}
.toc-link:hover {
  color: #0d6efd;
}
.toc-level-3 {
  padding-left: 1rem;
}
.toc-level-4 {
  padding-left: 2rem;
}
</style>