<template>
  <div class="card shadow-sm">
    <div class="card-body">
      <div ref="chartContainer" style="height: 400px; width: 100%;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';

const chartContainer = ref(null);
let chartInstance = null;
const trainingLogs = ref([]);

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:8000/api/sft/training_logs');
    if (!res.ok) throw new Error("API response was not ok.");
    trainingLogs.value = await res.json();
    initChart();
  } catch (error) {
    console.error("加载训练日志失败:", error);
  }
});

const initChart = () => {
  if (chartContainer.value && trainingLogs.value.length > 0) {
    chartInstance = echarts.init(chartContainer.value);
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value', name: 'Step' },
      yAxis: { type: 'value', name: 'Loss', min: 0 },
      series: [{ 
        data: trainingLogs.value.map(log => [log.step, log.loss]),
        type: 'line', 
        smooth: true, 
        showSymbol: false 
      }],
      grid: { left: '10%', right: '5%', bottom: '15%' }
    };
    chartInstance.setOption(option);
  }
};
</script>