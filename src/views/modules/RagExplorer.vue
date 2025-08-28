<template>
  <div class="container-fluid">
    <div class="text-center mb-5">
      <h1 class="display-5 fw-bold">RAG 流程可视化</h1>
      <p class="lead text-muted">探索RAG如何通过“检索-增强-生成”来解决大模型的知识局限问题。</p>
    </div>

    <div class="form-check form-switch fs-4 mb-4 d-flex justify-content-center">
      <input class="form-check-input" type="checkbox" role="switch" id="use-rag-switch" v-model="useRAG">
      <label class="form-check-label ms-2" for="use-rag-switch">{{ useRAG ? '启用 RAG' : '关闭 RAG' }} (点击切换)</label>
    </div>

    <div class="row g-4">
      <div :class="useRAG ? 'col-lg-4' : 'd-none'">
        <div class="card h-100 shadow-sm">
          <div class="card-header"><i class="bi bi-database"></i> 知识库 (太阳系行星)</div>
          <div class="card-body">
            <div v-for="(doc, index) in knowledgeBase" :key="index" class="p-2 mb-2 border rounded small" :class="{ 'bg-warning-subtle': doc.highlighted }">
              {{ doc.content }}
            </div>
          </div>
        </div>
      </div>
      <div :class="useRAG ? 'col-lg-8' : 'col-12'">
        <div class="card h-100 shadow-sm">
          <div class="card-header"><i class="bi bi-diagram-3"></i> 处理流程</div>
          <div class="card-body">
            <div class="input-group mb-3">
              <input type="text" class="form-control" placeholder="基于知识库提问，例如：哪颗行星最大？" v-model="query">
              <button class="btn btn-primary" @click="runQuery" :disabled="loading">
                 <span v-if="loading" class="spinner-border spinner-border-sm"></span> {{ useRAG ? 'RAG 生成' : '直接生成' }}
              </button>
            </div>
            <div v-if="useRAG" class="d-flex flex-column align-items-center gap-3 my-4 text-center">
              <div :class="['p-2 border rounded', stage >= 1 ? 'border-primary' : '']" style="transition: all 0.5s;"><i class="bi bi-search"></i> 1. 检索<p v-if="stage >= 1" class="small text-muted mb-0">从知识库中找到最相关的段落。</p></div>
              <i class="bi bi-arrow-down fs-4 text-primary" v-if="stage >= 1"></i>
              <div :class="['p-2 border rounded w-100', stage >= 2 ? 'border-primary' : '']" style="transition: all 0.5s;"><i class="bi bi-files"></i> 2. 增强<div v-if="stage >= 2" class="mt-2 p-2 bg-light rounded text-start small"><strong>[上下文]:</strong> {{ augmentedContext }}<br/><strong>[问题]:</strong> {{ query }}</div></div>
              <i class="bi bi-arrow-down fs-4 text-primary" v-if="stage >= 2"></i>
              <div :class="['p-2 border rounded', stage >= 3 ? 'border-primary' : '']" style="transition: all 0.5s;"><i class="bi bi-robot"></i> 3. 生成<p v-if="stage >= 3" class="small text-muted mb-0">LLM根据增强后的Prompt生成答案。</p></div>
            </div>
            <div v-if="output" class="mt-4">
              <h5><i class="bi bi-chat-dots"></i> 模型输出:</h5>
              <div class="p-3 border rounded bg-success-subtle">{{ output }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const useRAG = ref(true);
const query = ref('哪颗行星最大？');
const loading = ref(false);
const output = ref('');
const stage = ref(0);
const augmentedContext = ref('');
const knowledgeBase = ref([
  { content: '水星是太阳系八大行星中最小和最靠近太阳的行星，没有天然卫星。', highlighted: false },
  { content: '木星是太阳系中从内到外的第五颗行星，也是体积最大、自转最快的行星。', highlighted: false },
  { content: '地球是太阳系中唯一已知存在生命的行星，表面约71%是海洋。', highlighted: false },
]);

const runQuery = () => {
  loading.value = true;
  output.value = '';
  stage.value = 0;
  knowledgeBase.value.forEach(d => d.highlighted = false);

  if (useRAG.value) {
    setTimeout(() => {
      stage.value = 1;
      const relevantDocIndex = 1;
      knowledgeBase.value[relevantDocIndex].highlighted = true;
      augmentedContext.value = knowledgeBase.value[relevantDocIndex].content;
      setTimeout(() => {
        stage.value = 2;
        setTimeout(() => {
          stage.value = 3;
          output.value = '根据上下文，木星是最大的行星。';
          loading.value = false;
        }, 800);
      }, 800);
    }, 800);
  } else {
    setTimeout(() => {
      output.value = '作为语言模型，我无法确定哪颗行星最大，因为我的知识是截至训练时的。不过，通常认为是木星。';
      loading.value = false;
    }, 1000);
  }
};
</script>

<style scoped>
.bg-warning-subtle { transition: background-color 0.5s ease; }
</style>