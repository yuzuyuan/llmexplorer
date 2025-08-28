<template>
  <div class="container my-4">
    <div class="row">
      <div class="col-lg-3 d-none d-lg-block">
        <aside class="toc-sidebar">
          <nav v-if="toc.length > 0">
            <h5 class="toc-title">文章目录</h5>
            <ul class="list-unstyled">
              <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
                <a :href="`#${item.id}`" class="toc-link">{{ item.title }}</a>
              </li>
            </ul>
          </nav>
        </aside>
      </div>
      <div class="col-lg-9">
        <div class="articles-content-wrapper">
          <h1 class="text-center fw-bold mb-5 border-bottom pb-3">知识库文章</h1>
          <div v-if="htmlContent" v-html="htmlContent" class="markdown-body"></div>
          <div v-else class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCombinedMarkdown } from '@/composables/useCombinedMarkdown.js';
import '@/assets/page-styles.css';

// 需要加载的 Markdown 文件 slugs
const slugs = ['1-llm-basics', '2-prompt-engineering', '3-rag', '4-sft'];
const { htmlContent, toc } = useCombinedMarkdown(slugs);
</script>

<style scoped>
.articles-content-wrapper {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>