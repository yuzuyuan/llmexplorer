<template>
  <div class="rag-explorer-container" id="rag-main-card">
    <h2 class="text-center mb-4">RAG 揭秘：从海量法规到精准答案</h2>

    <div class="card mb-4 bg-light" id="offline-process-explainer">
        <div class="card-body">
            <h5 class="card-title">第一步：知识的准备 (离线处理)</h5>
            <p class="card-text small text-muted">
                在您与页面交互前，我们已完成“幕后工作”：<br>
                1. <strong>文档加载与切分</strong>: 读取所有法规文件，并将它们智能地切分成独立的“法条卡片”。<br>
                2. <strong>向量化与索引</strong>: 使用 Embedding 模型将每张“法条卡片”的语义压缩成一个数学向量（它的“坐标”），并存入可供高速检索的向量数据库中。
            </p>
        </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">第二步：输入问题，执行向量召回 (Recall)</h5>
        <p class="small text-muted">
            “大海捞针”的第一步。系统会将您的问题也转换成一个向量“坐标”，然后在数据库中快速捞出与它语义最相近的一批“候选法条”。这一步追求“快”和“全”。
        </p>
        <div class="form-group mb-3" id="rag-query-input">
          <label for="query-input" class="form-label"><strong>输入你的问题:</strong></label>
          <input type="text" id="query-input" class="form-control" v-model="query" placeholder="例如：山东省关于环境保护有哪些规定？">
        </div>
        <button class="btn btn-primary" @click="runRetrieval" :disabled="loading.retrieve || !query">
          <span v-if="loading.retrieve" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ loading.retrieve ? '检索中...' : '1. 执行向量检索' }}
        </button>
      </div>
    </div>

    <div v-if="results.retrieved_docs.length > 0" class="mt-4" id="rag-flow-diagram">
      <div class="row">
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">向量召回结果</h5>
              <p class="small text-muted">这是初步捞出的10个候选者，按语义相似度排序。</p>
              <ul class="list-group list-group-flush">
                <li v-for="doc in results.retrieved_docs" :key="doc.id" class="list-group-item">
                  <span class="badge bg-secondary me-2">相似度: {{ (1 - doc.distance).toFixed(3) }}</span>
                  <p class="mb-0 doc-text">{{ doc.text }}</p>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="col-md-6" id="reranker-section">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">第三步：Reranker 精准排序 (Precision)</h5>
              <p class="small text-muted">
                优中选优。Reranker 模型会逐一精读左侧的每个候选条文，并根据与问题的真实关联度重新打分排序。这一步追求“准”和“精”。
              </p>
              <button class="btn btn-success mb-3" @click="applyReranker" :disabled="loading.rerank">
                <span v-if="loading.rerank" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ loading.rerank ? '精排中...' : '2. 应用 Reranker' }}
              </button>
              <ul v-if="results.reranked_docs.length > 0" class="list-group list-group-flush">
                <li v-for="doc in results.reranked_docs" :key="doc.id" class="list-group-item list-group-item-success">
                   <span class="badge bg-success me-2">相关分: {{ doc.rerank_score }}</span>
                   <p class="mb-0 doc-text">{{ doc.text }}</p>
                </li>
              </ul>
              <div v-else class="text-center text-muted mt-4">
                <p>点击上方按钮对检索结果进行精排，直观对比效果。</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card mt-4" id="rag-output">
         <div class="card-body">
            <h5 class="card-title">第四步：增强生成 (Generation)</h5>
            <p class="small text-muted">
                最后一步，让大模型“开卷考试”。系统会将最相关的几条法规（上下文）和您的原始问题打包成一个全新的、信息丰富的 Prompt，交给大模型生成最终答案。
            </p>
             <div class="btn-group mb-3" role="group">
                <button class="btn" :class="contextSource === 'retrieval' ? 'btn-primary' : 'btn-outline-primary'" @click="setContextSource('retrieval')">
                    使用【召回】结果生成
                </button>
                <button class="btn" :class="contextSource === 'rerank' ? 'btn-success' : 'btn-outline-success'" @click="setContextSource('rerank')" :disabled="results.reranked_docs.length === 0">
                    使用【精排】结果生成
                </button>
            </div>

            <button class="btn btn-info ms-3" @click="runGeneration" :disabled="loading.generate || !contextSource">
                <span v-if="loading.generate" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                3. 生成答案
            </button>

            <div v-if="results.final_answer" class="mt-3">
                <div class="accordion" id="prompt-accordion">
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                            点击查看发送给大模型的“考卷”(Final Prompt)
                        </button>
                        </h2>
                        <div id="collapseOne" class="accordion-collapse collapse" data-bs-parent="#prompt-accordion">
                        <div class="accordion-body"><pre class="prompt-display">{{ results.final_prompt }}</pre></div>
                        </div>
                    </div>
                </div>
                <h6 class="mt-3"><strong>最终答案:</strong></h6>
                <p class="final-answer">{{ results.final_answer }}</p>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// ... (script 部分与上一版完全相同，无需修改) ...
import { ref, reactive,defineEmits} from 'vue';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

const API_BASE_URL = 'http://127.0.0.1:8000';
const emit = defineEmits(['interaction'])
const query = ref('山东省关于环境保护有哪些规定？');
const loading = reactive({ retrieve: false, rerank: false, generate: false });
const results = reactive({
    retrieved_docs: [],
    reranked_docs: [],
    final_prompt: '',
    final_answer: ''
});
const contextSource = ref(null);

const runRetrieval = async () => {
  loading.retrieve = true;
  emit('interaction', 'run-retrieval');
  Object.assign(results, { retrieved_docs: [], reranked_docs: [], final_prompt: '', final_answer: '' });
  contextSource.value = null;

  try {
    const response = await fetch(`${API_BASE_URL}/api/rag/retrieve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query.value }),
    });
    if (!response.ok) throw new Error((await response.json()).detail || '检索失败');
    const data = await response.json();
    results.retrieved_docs = data.retrieved_docs;
  } catch (error) {
    alert(`检索时发生错误: ${error.message}`);
  } finally {
    loading.retrieve = false;
  }
};

const applyReranker = async () => {
    emit('interaction', 'apply-reranker');
    loading.rerank = true;
    results.reranked_docs = [];
    try {
        const response = await fetch(`${API_BASE_URL}/api/rag/rerank`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query.value, documents: results.retrieved_docs }),
        });
        if (!response.ok) throw new Error((await response.json()).detail || '重排序失败');
        const data = await response.json();
        results.reranked_docs = data.reranked_docs;
    } catch (error) {
        alert(`重排序时发生错误: ${error.message}`);
    } finally {
        loading.rerank = false;
    }
};

const setContextSource = (source) => {
    contextSource.value = source;
};

const runGeneration = async () => {
    emit('interaction', 'generate-answer');
    if (!contextSource.value) {
        alert("请先选择一个上下文来源（召回结果或精排结果）。");
        return;
    }
    loading.generate = true;
    results.final_prompt = '';
    results.final_answer = '';

    const docsForContext = contextSource.value === 'rerank' ? results.reranked_docs : results.retrieved_docs;
    const context = docsForContext.slice(0, 3).map(d => d.text).join('\n\n---\n\n');

    try {
        const response = await fetch(`${API_BASE_URL}/api/rag/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query.value, context: context }),
        });
        if (!response.ok) throw new Error((await response.json()).detail || '生成答案失败');
        const data = await response.json();
        results.final_prompt = data.final_prompt;
        results.final_answer = data.final_answer;
    } catch (error) {
        alert(`生成答案时发生错误: ${error.message}`);
    } finally {
        loading.generate = false;
    }
};
</script>

<style scoped>
/* 样式与之前版本保持一致 */
.rag-explorer-container { max-width: 1200px; margin: auto; }
.doc-text { font-size: 0.85rem; color: #333; white-space: pre-wrap; word-break: break-word; }
.prompt-display { background-color: #f8f9fa; padding: 1rem; border-radius: 5px; white-space: pre-wrap; word-break: break-all; font-size: 0.9rem; }
.final-answer { background-color: #e9f5ff; border-left: 4px solid #0d6efd; padding: 1rem; border-radius: 4px; white-space: pre-wrap; }
.list-group-item { padding-top: 0.75rem; padding-bottom: 0.75rem; }
</style>
