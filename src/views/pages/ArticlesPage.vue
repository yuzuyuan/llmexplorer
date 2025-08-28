<template>
  <div class="container my-4">
    <SearchControl
      :visible="search.visible"
      :search-term="search.term"
      :current-index="search.currentIndex"
      :total="search.results.length"
      @next="goToNextMatch"
      @previous="goToPreviousMatch"
      @close="clearSearchAndQuery"
    />

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
          <div ref="contentContainer" v-if="htmlContent" v-html="htmlContent" class="markdown-body"></div>
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
import { ref, watch, nextTick, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCombinedMarkdown } from '@/composables/useCombinedMarkdown.js';
import SearchControl from '@/components/SearchControl.vue';
import '@/assets/page-styles.css';

const route = useRoute();
const router = useRouter();
const slugs = ['1-llm-basics', '2-prompt-engineering', '3-rag', '4-sft'];
const { htmlContent, toc } = useCombinedMarkdown(slugs);

const contentContainer = ref(null);
let originalHtml = '';
let isContentLoaded = false;

const search = reactive({
  visible: false,
  term: '',
  results: [],
  currentIndex: 0,
});

const clearHighlight = () => {
  if (originalHtml && contentContainer.value) {
    contentContainer.value.innerHTML = originalHtml;
  }
};

const clearSearchAndQuery = () => {
  clearHighlight();
  search.visible = false;
  search.term = '';
  search.results = [];
  search.currentIndex = 0;
  router.replace({ query: {} });
};

const performSearch = async (query) => {
  if (!query || !isContentLoaded) {
    clearHighlight();
    search.visible = false;
    return;
  }
  
  await nextTick();
  clearHighlight();
  
  const regex = new RegExp(`(${query})`, 'gi');
  if (!originalHtml.match(regex)) {
    search.results = [];
  } else {
    contentContainer.value.innerHTML = originalHtml.replace(regex, `<mark class="search-highlight">$1</mark>`);
    search.results = Array.from(contentContainer.value.querySelectorAll('.search-highlight'));
  }
  
  search.term = query;
  search.visible = true;

  if (search.results.length > 0) {
    search.currentIndex = 0;
    navigateToMatch(0);
  }
};

const navigateToMatch = (index) => {
  if (!search.results[index]) return;
  document.querySelector('.search-highlight-active')?.classList.remove('search-highlight-active');
  const target = search.results[index];
  target.classList.add('search-highlight-active');
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  search.currentIndex = index;
};

const goToNextMatch = () => {
  if (search.results.length === 0) return;
  const nextIndex = (search.currentIndex + 1) % search.results.length;
  navigateToMatch(nextIndex);
};

const goToPreviousMatch = () => {
  if (search.results.length === 0) return;
  const prevIndex = (search.currentIndex - 1 + search.results.length) % search.results.length;
  navigateToMatch(prevIndex);
};

watch(
  () => route.query.search,
  (newQuery) => {
    if (isContentLoaded) {
      performSearch(newQuery);
    }
  },
  { immediate: true }
);


watch(htmlContent, async (newContent) => { // 1. 将回调函数设为 async
  if (newContent && !isContentLoaded) {
    // 2. 等待 DOM 更新
    await nextTick();
    
    // 3. 确保 contentContainer 存在后再执行操作
    if (contentContainer.value) {
      isContentLoaded = true;
      originalHtml = contentContainer.value.innerHTML; // 现在这里是安全的
      if (route.query.search) {
        performSearch(route.query.search);
      }
    }
  }
});
</script>


<style scoped>
.articles-content-wrapper {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>