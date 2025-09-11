<template>
  <div class="quiz-container">
    <p class="quiz-question fw-bold">{{ question }}</p>
    <div class="quiz-options">
      <button
        v-for="(option, index) in options"
        :key="index"
        @click="selectAnswer(option)"
        :class="['btn', 'quiz-option-btn', getButtonClass(option)]"
        :disabled="isAnswered"
      >
        {{ option }}
      </button>
    </div>
    <div v-if="isAnswered" class="quiz-feedback mt-3 p-3 rounded" :class="feedbackClass">
      {{ feedbackMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// 必须先用 defineEmits 声明组件要发出的所有事件
const emit = defineEmits(['answeredCorrectly']);

// 定义从父组件接收的必需属性
const props = defineProps({
  question: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    required: true,
  },
  answer: {
    type: String,
    required: true,
  }
});

const selectedAnswer = ref(null);
const isAnswered = ref(false);

const selectAnswer = (option) => {
  if (!isAnswered.value) {
    selectedAnswer.value = option;
    isAnswered.value = true;

    // 如果答案正确，就使用 emit 函数发出 'answeredCorrectly' 事件
    if (isCorrect.value) {
      emit('answeredCorrectly');
    }
  }
};

const isCorrect = computed(() => {
  return selectedAnswer.value === props.answer;
});

const feedbackMessage = computed(() => {
  if (!isAnswered.value) return '';
  return isCorrect.value ? '✅ 回答正确！' : `❌ 正确答案是: ${props.answer}`;
});

const feedbackClass = computed(() => {
  return isCorrect.value ? 'feedback-correct' : 'feedback-incorrect';
});

const getButtonClass = (option) => {
  if (!isAnswered.value) {
    return 'btn-outline-primary';
  }
  if (option === props.answer) {
    return 'btn-success'; // 正确答案按钮
  }
  if (option === selectedAnswer.value) {
    return 'btn-danger'; // 用户选择的错误答案按钮
  }
  return 'btn-outline-secondary'; // 其他未选中的错误选项
};
</script>

<style scoped>
.quiz-container {
  background-color: #f8f9fa;
  border-left: 5px solid #0d6efd;
  padding: 1.5rem;
}

.quiz-question {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.quiz-options {
  display: grid;
  gap: 0.75rem;
}

.quiz-option-btn {
  width: 100%;
  text-align: left;
  padding: 0.75rem 1rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease-in-out;
}

.feedback-correct {
  background-color: #d1e7dd;
  color: #0f5132;
  border: 1px solid #badbcc;
}

.feedback-incorrect {
  background-color: #f8d7da;
  color: #842029;
  border: 1px solid #f5c2c7;
}
</style>
