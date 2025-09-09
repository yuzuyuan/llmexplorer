<template>
  <div class="container my-4" ref="pageContainerRef">
    <div class="page-header-actions">
      <button @click="startGuidance('prompt')" class="btn btn-outline-primary">
        <i class="bi bi-info-circle-fill me-1"></i>
        入门引导
      </button>
    </div>

    <GuidancePopover
      v-if="guidanceState.visible"
      :title="guidanceState.title"
      :content="guidanceState.content"
      :button-text="guidanceState.buttonText"
      @confirm="nextGuideStep"
      @close="closeGuidance"
    />

    <div class="row">
      <div class="col-lg-3 d-none d-lg-block">
        <aside class="toc-sidebar">
          <nav v-if="toc.length > 0">
            <h5 class="toc-title">文档内容</h5>
            <ul class="list-unstyled">
              <li v-for="item in toc" :key="item.id" :class="`toc-level-${item.level}`">
                <a :href="`#${item.id}`" class="toc-link">{{ item.title }}</a>
              </li>
            </ul>
          </nav>
        </aside>
      </div>
      <div class="col-lg-9">
        <div class="mb-5 pb-4 border-bottom">
          <PromptEngineering @interaction="handleInteraction" />
        </div>
        <div class="mt-4">
          <h2 class="text-center fw-bold mb-4">相关知识文档</h2>
          <div v-html="htmlContent" class="markdown-body"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import PromptEngineering from '../modules/PromptEngineering.vue';
import { useMarkdown } from '@/composables/useMarkdown.js';
import GuidancePopover from '@/components/GuidancePopover.vue';
import { useGuidance } from '@/composables/useGuidance.js';
import { useAchievements } from '@/composables/useAchievements';
import '@/assets/page-styles.css';

const { htmlContent, toc } = useMarkdown('2-prompt-engineering');
const { guidanceState, startGuidance, nextGuideStep, closeGuidance } = useGuidance();
const { unlockAchievement, trackInteraction } = useAchievements();
const pageContainerRef = ref(null);

// --- Achievement Tracking ---
const achievementId = 'read_prompt_engineering';
const interactionAchievementId = 'interact_prompt_engineering';

const handleScroll = () => {
  const element = document.documentElement;
  if (element.scrollHeight - element.scrollTop <= element.clientHeight + 1) {
    unlockAchievement(achievementId);
  }
};

const handleInteraction = (interactionId) => {
  trackInteraction('prompt_engineering', interactionId);
  // This page only has one main interaction button, so we can unlock directly.
  unlockAchievement(interactionAchievementId);
};

onMounted(() => {
  startGuidance('prompt');
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.page-header-actions {
  text-align: right;
  margin-bottom: 1rem;
  position: relative;
  z-index: 10;
}
</style>
