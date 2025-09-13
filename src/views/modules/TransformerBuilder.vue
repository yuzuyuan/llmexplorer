<template>
  <div class="transformer-builder">
    <div class="controls card shadow-sm mb-3">
      <div class="card-body">
        <h5 class="card-title mb-3">控制与配置</h5>
        <div class="d-flex flex-wrap align-items-center justify-content-between">

          <div class="d-flex flex-wrap align-items-center me-md-3 mb-2 mb-md-0">
            <div class="me-3">
              <label for="epochs" class="form-label me-2">Epochs:</label>
              <input type="number" id="epochs" class="form-control form-control-sm" style="width: 80px;" v-model.number="trainingParams.epochs" min="1" max="50">
            </div>
            <div>
              <label for="learningRate" class="form-label me-2">学习率:</label>
              <input type="number" id="learningRate" class="form-control form-control-sm" style="width: 120px;" v-model.number="trainingParams.learningRate" min="0.00001" max="0.01" step="0.00001">
            </div>
          </div>

          <div class="d-flex flex-wrap">
            <button @click="loadClassicModel" class="btn btn-success me-2 mb-2 mb-md-0">
              <i class="bi bi-gear-wide-connected"></i> 一键配置
            </button>
            <button @click="startTraining" class="btn btn-primary me-2 mb-2 mb-md-0" :disabled="components.length === 0 || trainingState.isTraining">
              <i class="bi bi-play-fill"></i> 开始训练
            </button>
            <button @click="clearCanvas" class="btn btn-warning mb-2 mb-md-0" :disabled="components.length === 0">
              <i class="bi bi-x-lg"></i> 清空画布
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showInstructions" class="alert alert-info alert-dismissible fade show shadow-sm" role="alert">
      <h5 class="alert-heading"><i class="bi bi-info-circle-fill"></i> 搭建提示</h5>
      <p class="mb-1">
        一个经典的翻译模型通常遵循以下顺序：
      </p>
      <ol class="mb-2" style="padding-left: 1.5rem;">
        <li><b>编码器部分</b>: <code>源语言输入</code> → <code>嵌入层</code> → <code>位置编码</code> → <code>编码器块</code> (可堆叠多个)。</li>
        <li><b>解码器部分</b>: <code>目标语言输入</code> → <code>嵌入层</code> → <code>位置编码</code> → <code>解码器块</code> (可堆叠多个)。</li>
        <li><b>连接</b>: 将最后的 <code>编码器块</code> 连接到每一个 <code>解码器块</code> (形成交叉注意力)。</li>
        <li><b>输出</b>: 将最后的 <code>解码器块</code> 连接到 <code>输出层</code>。</li>
      </ol>
      <small>您也可以点击“一键配置优秀网络”快速加载示例。</small>
      <button type="button" class="btn-close" @click="showInstructions = false" aria-label="Close"></button>
    </div>

    <div v-if="trainingState.isTraining || trainingState.logs.length > 0" class="training-dashboard">
        <TrainingLogChart v-if="trainingMetrics.epochs.length > 0" :chart-data="trainingMetrics" class="mb-3" />

        <div class="training-log card shadow-sm">
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
        tabindex="0"
        @dragover.prevent
        @drop="onDrop"
        @mousemove="onCanvasMouseMove"
        @mouseup="onCanvasMouseUp"
        @mouseleave="cancelConnection"
      >
        <div
          v-for="component in components"
          :key="component.id"
          class="canvas-component"
          :id="component.id"
          :style="{ top: component.position.y + 'px', left: component.position.x + 'px', borderColor: getComponentColor(component.type) }"
          @mousedown.left="startDragComponent(component, $event)"
          @click="selectComponent(component)"
          @mouseup="finishConnecting(component)"
          :class="{ 'selected': selectedComponent && selectedComponent.id === component.id }"
        >
          {{ component.label }}
          <div class="connection-handle" @mousedown.stop="startConnecting(component, $event)"></div>
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
          <path v-if="isConnecting" :d="tempConnectionPath" class="connection-path normal" marker-end="url(#arrow)"></path>
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
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue';
import TrainingLogChart from './TrainingLogsChart.vue';

const components = ref([]);
const connections = ref([]);
const selectedComponent = ref(null);
const canvasRef = ref(null);

const showInstructions = ref(true);

const isConnecting = ref(false);
const connectionStartComponent = ref(null);
const tempConnectionPath = ref('');

const trainingState = reactive({
  isTraining: false,
  logs: [],
});

const trainingMetrics = ref({
  epochs: [],
  loss: [],
  ppl: []
});
const trainingParams = reactive({
  epochs: 5,
  learningRate: 0.0001,
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

let draggedComponent = null;
let offset = { x: 0, y: 0 };

const startDragComponent = (component, event) => {
    if (event.target.classList.contains('connection-handle')) {
        return;
    }
    draggedComponent = component;
    const compElement = document.getElementById(component.id);
    const compRect = compElement.getBoundingClientRect();

    offset.x = event.clientX - compRect.left;
    offset.y = event.clientY - compRect.top;

    document.addEventListener('mousemove', onDragComponent);
    document.addEventListener('mouseup', stopDragComponent, { once: true });
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
};

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
  trainingMetrics.value = { epochs: [], loss: [], ppl: [] };
}

const handleKeyDown = (event) => {
  if (selectedComponent.value && (event.key === 'Delete' || event.key === 'Backspace')) {
    event.preventDefault();
    deleteComponent(selectedComponent.value.id);
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

const connectionRules = [
    ['source_input', 'embedding'],
    ['target_input', 'embedding'],
    ['embedding', 'positional_encoding'],
    ['positional_encoding', 'encoder_block'],
    ['positional_encoding', 'decoder_block'],
    ['encoder_block', 'encoder_block'],
    ['encoder_block', 'decoder_block'],
    ['decoder_block', 'decoder_block'],
    ['decoder_block', 'output_layer'],
];

const isValidConnection = (fromComponent, toComponent) => {
    if (!fromComponent || !toComponent || fromComponent.id === toComponent.id) {
        return false;
    }
    const exists = connections.value.some(c => c.from === fromComponent.id && c.to === toComponent.id);
    if (exists) {
        alert('错误：这两个组件之间已经存在连接。');
        return false;
    }

    return connectionRules.some(rule => rule[0] === fromComponent.type && rule[1] === toComponent.type);
}

const startConnecting = (component, event) => {
    isConnecting.value = true;
    connectionStartComponent.value = component;
    event.stopPropagation();
};

const finishConnecting = (targetComponent) => {
    if (isConnecting.value && connectionStartComponent.value && targetComponent) {
        if (isValidConnection(connectionStartComponent.value, targetComponent)) {
            const newConnection = {
                from: connectionStartComponent.value.id,
                to: targetComponent.id,
                type: 'normal'
            };
            if (connectionStartComponent.value.type === 'encoder_block' && targetComponent.type === 'decoder_block') {
                newConnection.type = 'cross_attention';
            }
            connections.value.push(newConnection);
        } else if (connectionStartComponent.value.id !== targetComponent.id) {
            alert(`无效连接：无法从 '${connectionStartComponent.value.label}' 连接到 '${targetComponent.label}'。`);
        }
    }
    cancelConnection();
};

const onCanvasMouseMove = (event) => {
    if (isConnecting.value && connectionStartComponent.value) {
        const fromEl = document.getElementById(connectionStartComponent.value.id);
        if (!fromEl || !canvasRef.value) return;

        const canvasRect = canvasRef.value.getBoundingClientRect();
        const fromRect = fromEl.getBoundingClientRect();

        const startX = fromRect.right - canvasRect.left;
        const startY = fromRect.top - canvasRect.top + fromRect.height / 2;
        const endX = event.clientX - canvasRect.left;
        const endY = event.clientY - canvasRect.top;

        tempConnectionPath.value = `M ${startX},${startY} C ${startX + 50},${startY} ${endX - 50},${endY} ${endX},${endY}`;
    }
};

const onCanvasMouseUp = () => {
    if (isConnecting.value) {
        cancelConnection();
    }
};

const cancelConnection = () => {
    isConnecting.value = false;
    connectionStartComponent.value = null;
    tempConnectionPath.value = '';
};

const getConnectionPath = (conn) => {
  if (!canvasRef.value) return '';
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
  trainingMetrics.value = { epochs: [], loss: [], ppl: [] };

  try {
    const response = await fetch('/api/transformer/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
  components: components.value,
  connections: connections.value,
  // MODIFICATION: Send new training params
  epochs: trainingParams.epochs,
  learning_rate: trainingParams.learningRate,
}),
    });

    if (!response.ok || !response.body) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');

      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim() === '') continue;
        try {
          const data = JSON.parse(line);
          if (data.type === 'log') {
            trainingState.logs.push(data.payload);
          } else if (data.type === 'metric') {
            // **FIX:** Create a new object to avoid reactivity loop
            const newMetrics = {
              epochs: [...trainingMetrics.value.epochs, data.payload.epoch],
              loss: [...trainingMetrics.value.loss, data.payload.loss],
              ppl: [...trainingMetrics.value.ppl, data.payload.ppl],
            };
            trainingMetrics.value = newMetrics;
          }
        } catch (e) {
          console.error("Error parsing streaming data line:", line, e);
        }
      }
    }
  } catch (error) {
    console.error("训练请求失败:", error);
    trainingState.logs.push(`错误: ${error.message}`);
    trainingState.logs.push("请检查后端服务是否已启动，以及网络连接是否正常。");
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
  grid-template-columns: 240px 1fr 320px;
  grid-template-rows: auto minmax(600px, 1fr);
  gap: 1.5rem;
  min-height: 80vh;
}
.component-library {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
}
.parameter-panel {
  grid-column: 3 / 4;
  grid-row: 1 / 2;
}
.canvas {
  grid-column: 1 / 4;
  grid-row: 2 / 3;
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
.canvas:focus {
    outline: 2px solid rgba(13, 110, 253, 0.5);
    outline-offset: 2px;
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

.connection-handle {
    position: absolute;
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 16px;
    background-color: #fff;
    border: 2px solid #6c757d;
    border-radius: 50%;
    cursor: crosshair;
    z-index: 11;
    transition: background-color 0.2s, transform 0.2s;
}
.connection-handle:hover {
    background-color: #0d6efd;
    border-color: #0a58ca;
    transform: translateY(-50%) scale(1.2);
}

.connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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
  height: 250px;
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
