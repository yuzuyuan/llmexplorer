<template>
  <div class="container my-5">
    <div class="text-center mb-5">
      <h1 class="display-4 fw-bold">知识测验中心</h1>
      <p class="lead text-muted">检验你对 LLM Explorer 各个模块知识的掌握程度。</p>
    </div>

    <div v-if="quizzes.length > 0" class="row g-4">
      <div v-for="quiz in quizzes" :key="quiz.id" class="col-12">
        <div class="card shadow-sm h-100">
          <div class="card-header bg-primary text-white">
            <h5 class="my-1"><i class="bi bi-patch-question-fill me-2"></i><strong>主题：</strong>{{ quiz.topic }}</h5>
          </div>
          <div class="card-body">
            <Quiz
              :question="quiz.question"
              :options="quiz.options"
              :answer="quiz.answer"
              @answeredCorrectly="handleCorrectAnswer"
            />
          </div>
        </div>
      </div>
    </div>
    <div v-else class="alert alert-info">
      暂无问答题目。
    </div>
  </div>
</template>

<script setup>
import Quiz from '@/components/Quiz.vue';
import { useQuizzes } from '@/composables/quizzes.js';
import { useAchievements } from '@/composables/useAchievements';

const { quizzes } = useQuizzes();
const { unlockAchievement } = useAchievements();

const handleCorrectAnswer = () => {
  // 从 localStorage 获取当前的计数值，如果没有则默认为 0
  const correctCount = parseInt(localStorage.getItem('quizCorrectCount') || '0') + 1;

  // 将新的计数值存回 localStorage
  localStorage.setItem('quizCorrectCount', correctCount.toString());

  // 检查是否达到解锁成就的条件
  if (correctCount >= 5) {
    unlockAchievement('quiz_master_5');
  }
  if (correctCount >= 10) {
    unlockAchievement('quiz_master_10');
  }
};
</script>

<style scoped>
.card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
.card-header {
  font-size: 1.1rem;
}
</style>
