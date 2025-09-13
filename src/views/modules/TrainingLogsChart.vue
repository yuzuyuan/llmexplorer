<template>
  <div class="training-chart card shadow-sm">
    <div class="card-header fw-bold">
      <i class="bi bi-graph-up"></i> 训练性能曲线
    </div>
    <div class="card-body">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ epochs: [], loss: [], ppl: [] })
  }
});

const chartCanvas = ref(null);
let chartInstance = null;

const chartConfig = {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: '训练损失 (Loss)',
        backgroundColor: 'rgba(220, 53, 69, 0.2)',
        borderColor: 'rgba(220, 53, 69, 1)',
        data: [],
        yAxisID: 'yLoss',
        tension: 0.1
      },
      {
        label: '训练困惑度 (PPL)',
        backgroundColor: 'rgba(13, 110, 253, 0.2)',
        borderColor: 'rgba(13, 110, 253, 1)',
        data: [],
        yAxisID: 'yPpl',
        tension: 0.1
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Epoch'
        }
      },
      yLoss: {
        type: 'linear',
        position: 'left',
        title: {
          display: true,
          text: 'Loss'
        },
        grid: {
          drawOnChartArea: false, // only draw grid for one axis to avoid clutter
        },
      },
      yPpl: {
        type: 'linear',
        position: 'right',
        title: {
          display: true,
          text: 'Perplexity'
        }
      }
    }
  }
};

onMounted(() => {
  if (chartCanvas.value) {
    chartInstance = new Chart(chartCanvas.value, chartConfig);
  }
});

watch(() => props.chartData, (newData) => {
  if (chartInstance && newData) {
    chartInstance.data.labels = newData.epochs.map(e => `Epoch ${e}`);
    chartInstance.data.datasets[0].data = newData.loss;
    chartInstance.data.datasets[1].data = newData.ppl;
    chartInstance.update();
  }
}, { deep: true });

</script>

<style scoped>
.training-chart .card-body {
  height: 350px;
  position: relative;
}
</style>
