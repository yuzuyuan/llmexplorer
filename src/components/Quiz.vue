<template>
  <div class="card my-4 shadow-sm quiz-card">
    <div class="card-header bg-light">
      <h5 class="card-title mb-0">📝 随堂测验</h5>
    </div>
    <div class="card-body">
      <p class="card-text fw-bold">{{ quizData.question }}</p>
      <div class="list-group">
        <button
          v-for="(option, index) in quizData.options"
          :key="index"
          type="button"
          class="list-group-item list-group-item-action"
          @click="selectAnswer(index)"
          :disabled="answered"
          :class="getOptionClass(index)"
        >
          {{ option }}
        </button>
      </div>
      <div v-if="answered" class="mt-3 alert" :class="isCorrect ? 'alert-success' : 'alert-danger'">
        <strong>{{ isCorrect ? '回答正确！' : '再想想看！' }}</strong>
        <p class="mb-0">{{ quizData.feedback[isCorrect ? 'correct' : 'incorrect'] }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  quizData: {
    type: Object,
    required: true,
  },
});

const selectedIndex = ref(null);
const answered = ref(false);

const isCorrect = computed(() => {
  return selectedIndex.value === props.quizData.correctAnswerIndex;
});

const selectAnswer = (index) => {
  if (answered.value) return;
  selectedIndex.value = index;
  answered.value = true;
};

const getOptionClass = (index) => {
  if (!answered.value) return '';
  if (index === props.quizData.correctAnswerIndex) return 'list-group-item-success';
  if (index === selectedIndex.value) return 'list-group-item-danger';
  return '';
};
</script>

<style scoped>
.quiz-card {
  border-left: 5px solid #0d6efd;
}
.list-group-item-action:hover {
  background-color: #f8f9fa;
}
</style>
