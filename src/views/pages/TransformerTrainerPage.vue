<template>
  <div class="container my-4">
    <div class.center="row">
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
          <h1 class="text-center fw-bold mb-4">Transformer Builder</h1>
          <TransformerBuilder />
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
// Import the interactive component
import TransformerBuilder from '../modules/TransformerBuilder.vue';
// Import the composable to handle markdown rendering
import { useMarkdown } from '@/composables/useMarkdown.js';
// Import shared page styles, including for the markdown body and TOC
import '@/assets/page-styles.css';

// Use the composable to get HTML content and TOC from the new markdown file
const { htmlContent, toc } = useMarkdown('5-transformer');
</script>

<style scoped>
/* Scoped styles can be added here if needed */
</style>