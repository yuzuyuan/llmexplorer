<template>
  <div class="transformer-builder">
    <div class="controls card shadow-sm mb-3">
      <div class="card-body d-flex flex-wrap justify-content-between align-items-center">
        <h5 class="mb-2 mb-md-0 me-md-3">控制与配置</h5>
        <div class="d-flex flex-wrap">
          <button @click="loadClassicModel" class="btn btn-success me-2 mb-2 mb-md-0">
            <i class="bi bi-gear-wide-connected"></i> 一键配置优秀网络
          </button>
          <button @click="startTraining" class="btn btn-primary mb-2 mb-md-0" :disabled="components.length === 0 || trainingState.isTraining">
            <i class="bi bi-play-fill"></i> 开始训练
          </button>
           <button @click="clearCanvas" class="btn btn-warning ms-2 mb-2 mb-md-0" :disabled="components.length === 0">
            <i class="bi bi-x-lg"></i> 清空画布
          </button>
        </div>
      </div>
    </div>

    <div v-if="trainingState.isTraining || trainingState.logs.length > 0" class="training-log card shadow-sm mb-3">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="bi bi-terminal"></i> 训练日志
        </h5>
        <div v-if="trainingState.isTraining" class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <div class="card-body bg-dark text-white font-monospace">
        <pre v-for="(log, index) in trainingState.logs" :key="index">{{ log }}</pre>
      </div>
    </div>

    <div class="main-layout">
      <div class="component-library card shadow-sm">
        <div class="card-header fw-bold">组件库</div>
        <div class="card-body">
          <div
            v-for="comp in componentLibrary"
            :key="comp.type"
            class="draggable-component"
            :style="{ borderColor: comp.color, '--component-color': comp.color }"
            draggable="true"
            @dragstart="onDragStart($event, comp.type)"
          >
            {{ comp.name }}
          </div>
        </div>
      </div>

      <div
        class="canvas card shadow-sm"
        id="canvas"
        ref="canvasRef"
        @dragover.prevent
        @drop="onDrop"
      >
        <div
          v-for="component in components"
          :key="component.id"
          class="canvas-component"
          :id="component.id"
          :style="{ top: component.position.y + 'px', left: component.position.x + 'px', borderColor: getComponentColor(component.type) }"
          @mousedown.left="startDragComponent(component, $event)"
          @click="selectComponent(component)"
          :class="{ 'selected': selectedComponent && selectedComponent.id === component.id }"
        >
          {{ component.label }}
        </div>

        <svg class="connections-svg">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#6c757d" />
            </marker>
             <marker id="arrow-cross" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#fd7e14" />
            </marker>
          </defs>
          <path v-for="(conn, index) in connections" :key="index" :d="getConnectionPath(conn)" class="connection-path" :class="conn.type || 'normal'" :marker-end="conn.type === 'cross_attention' ? 'url(#arrow-cross)' : 'url(#arrow)'"></path>
        </svg>

      </div>

      <div class="parameter-panel card shadow-sm">
        <div class="card-header fw-bold">参数面板</div>
        <div class="card-body">
          <div v-if="selectedComponent">
            <h5 class="mb-3">{{ selectedComponent.label }}</h5>
            <div v-if="selectedComponent.params && Object.keys(selectedComponent.params).length > 0">
              <div v-for="(value, key) in selectedComponent.params" :key="key" class="mb-3">
                <label :for="key" class="form-label text-capitalize">{{ key.replace('_', ' ') }}</label>
                <input type="number" class="form-control" :id="key" v-model.number="selectedComponent.params[key]">
              </div>
            </div>
            <p v-else class="text-muted">该组件没有可配置参数。</p>
            <button class="btn btn-danger btn-sm mt-3" @click="deleteComponent(selectedComponent.id)">
              <i class="bi bi-trash"></i> 删除组件
            </button>
          </div>
          <div v-else class="text-muted text-center mt-5">
            <i class="bi bi-cursor" style="font-size: 2rem;"></i>
            <p class="mt-2">点击一个组件以查看和编辑其参数。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue';

const components = ref([]);
const connections = ref([]);
const selectedComponent = ref(null);
const canvasRef = ref(null);

// 训练状态管理
const trainingState = reactive({
  isTraining: false,
  logs: [],
  error: null,
});

const componentLibrary = reactive([
  { type: 'source_input', name: '源语言输入', color: '#0d6efd' },
  { type: 'target_input', name: '目标语言输入', color: '#8d33d6' },
  { type: 'embedding', name: '嵌入层', color: '#198754' },
  { type: 'positional_encoding', name: '位置编码', color: '#0dcaf0' },
  { type: 'encoder_block', name: '编码器块', color: '#6f42c1' },
  { type: 'decoder_block', name: '解码器块', color: '#d63384' },
  { type: 'output_layer', name: '输出层', color: '#dc3545' },
]);

const getComponentColor = (type) => {
  const comp = componentLibrary.find(c => c.type === type);
  return comp ? comp.color : '#6c757d';
};

// --- Drag and Drop Logic ---
const onDragStart = (event, type) => {
  event.dataTransfer.setData('componentType', type);
};

const onDrop = (event) => {
  const type = event.dataTransfer.getData('componentType');
  if (!type) return;

  const canvasRect = canvasRef.value.getBoundingClientRect();
  const x = event.clientX - canvasRect.left;
  const y = event.clientY - canvasRect.top;

  const compInfo = componentLibrary.find(c => c.type === type);
  const newId = `${type}_${Date.now()}`;

  components.value.push({
    id: newId,
    type: type,
    label: compInfo.name,
    params: getInitialParams(type),
    position: { x, y }
  });
};

const getInitialParams = (type) => {
    switch (type) {
        case 'embedding': return { embed_dim: 512 };
        case 'positional_encoding': return { dropout: 0.1 };
        case 'encoder_block': return { heads: 8, ff_dim: 2048 };
        case 'decoder_block': return { heads: 8, ff_dim: 2048 };
        default: return {};
    }
}

// --- Component Dragging on Canvas ---
let draggedComponent = null;
let offset = { x: 0, y: 0 };

const startDragComponent = (component, event) => {
    draggedComponent = component;
    const compElement = document.getElementById(component.id);
    const compRect = compElement.getBoundingClientRect();

    offset.x = event.clientX - compRect.left;
    offset.y = event.clientY - compRect.top;

    document.addEventListener('mousemove', onDragComponent);
    document.addEventListener('mouseup', stopDragComponent);
};

const onDragComponent = (event) => {
    if (!draggedComponent) return;
    const canvasRect = canvasRef.value.getBoundingClientRect();
    draggedComponent.position.x = event.clientX - canvasRect.left - offset.x;
    draggedComponent.position.y = event.clientY - canvasRect.top - offset.y;
};

const stopDragComponent = () => {
    draggedComponent = null;
    document.removeEventListener('mousemove', onDragComponent);
    document.removeEventListener('mouseup', stopDragComponent);
};

// --- Panel and Selection Logic ---
const selectComponent = (component) => {
  selectedComponent.value = component;
};

const deleteComponent = (id) => {
    components.value = components.value.filter(c => c.id !== id);
    connections.value = connections.value.filter(conn => conn.from !== id && conn.to !== id);
    if (selectedComponent.value && selectedComponent.value.id === id) {
        selectedComponent.value = null;
    }
};

const clearCanvas = () => {
  components.value = [];
  connections.value = [];
  selectedComponent.value = null;
  trainingState.logs = [];
}

// --- Connection Drawing ---
const getConnectionPath = (conn) => {
  const fromEl = document.getElementById(conn.from);
  const toEl = document.getElementById(conn.to);
  if (!fromEl || !toEl) return '';

  const canvasRect = canvasRef.value.getBoundingClientRect();
  const fromRect = fromEl.getBoundingClientRect();
  const toRect = toEl.getBoundingClientRect();

  const startX = fromRect.right - canvasRect.left;
  const startY = fromRect.top - canvasRect.top + fromRect.height / 2;
  const endX = toRect.left - canvasRect.left;
  const endY = toRect.top - canvasRect.top + toRect.height / 2;

  const controlX1 = startX + Math.abs(endX - startX) * 0.5;
  const controlY1 = startY;
  const controlX2 = endX - Math.abs(endX - startX) * 0.5;
  const controlY2 = endY;

  return `M ${startX},${startY} C ${controlX1},${controlY1} ${controlX2},${controlY2} ${endX},${endY}`;
};

// --- Core Functionality ---
const loadClassicModel = async () => {
  try {
    const response = await fetch('/architectures/classic_translation.json');
    if (!response.ok) throw new Error('网络错误!');
    const data = await response.json();
    components.value = data.architecture;
    connections.value = data.connections;
    selectedComponent.value = null;
    await nextTick();
    alert('经典翻译模型已加载！');
  } catch (error) {
    console.error('加载模型配置失败:', error);
    alert('加载模型配置失败！');
  }
};

const startTraining = async () => {
  trainingState.isTraining = true;
  trainingState.logs = ["发起训练请求，请稍候..."];
  trainingState.error = null;

  try {
    const response = await fetch('/api/transformer/train', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        components: components.value,
        connections: connections.value,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    trainingState.logs = result.logs || ['训练完成，但未收到日志。'];

  } catch (error) {
    console.error("训练请求失败:", error);
    trainingState.error = error.message;
    trainingState.logs.push(`错误: ${error.message}`);
    trainingState.logs.push("请检查后端服务是否已启动，以及数据集路径是否正确。");
  } finally {
    trainingState.isTraining = false;
  }
};
</script>

<style scoped>
.transformer-builder {
  border: 1px solid #dee2e6;
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
}
.main-layout {
  display: grid;
  /* 定义3列用于对齐：左侧组件库，中间弹性空白，右侧参数面板 */
  grid-template-columns: 240px 1fr 320px;
  /* 定义2行：一行给顶部面板，一行给画布 */
  grid-template-rows: auto minmax(600px, 1fr);
  gap: 1.5rem;
  min-height: 80vh;
}
.component-library {
  grid-column: 1 / 2; /* 放置在第1列 */
  grid-row: 1 / 2;    /* 放置在第1行 */
}
.parameter-panel {
  grid-column: 3 / 4; /* 放置在第3列 */
  grid-row: 1 / 2;    /* 放置在第1行 */
}
.canvas {
  grid-column: 1 / 4; /* 让画布横跨所有3列 */
  grid-row: 2 / 3;    /* 放置在第2行 */
  position: relative;
  min-height: 600px;
  background-color: #e9ecef;
  background-image:
    linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  overflow: auto;
  border: 1px solid #ced4da;
  border-radius: 0.5rem;
}

.component-library .card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.draggable-component {
  padding: 1rem;
  border: 2px solid;
  border-radius: 0.5rem;
  text-align: center;
  font-weight: 600;
  background-color: #fff;
  cursor: grab;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.08);
}
.draggable-component:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.12);
  color: var(--component-color);
}

.canvas-component {
  position: absolute;
  border: 2px solid;
  padding: 1.25rem 1.5rem;
  background: white;
  cursor: move;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s, transform 0.2s;
  user-select: none;
  min-width: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.canvas-component.selected {
  border-width: 3px;
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.3), 0 6px 15px rgba(0,0,0,0.2);
  transform: scale(1.03);
  z-index: 10;
}

.connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 200%;
  height: 200%;
  pointer-events: none;
}
.connection-path {
  stroke-width: 2.5;
  fill: none;
}
.connection-path.normal {
  stroke: #6c757d;
}
.connection-path.cross_attention {
  stroke: #fd7e14;
  stroke-dasharray: 6,6;
}
.parameter-panel .form-label {
  font-weight: 500;
}

.training-log .card-body {
  height: 300px;
  overflow-y: auto;
}
.training-log pre {
  margin: 0;
  padding: 2px 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.85rem;
}
</style>
