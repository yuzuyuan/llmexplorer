import { ref, onMounted, onUnmounted } from 'vue';

const achievementList = [
  { id: 'read_llm_basics', name: 'LLM基础入门', description: '阅读完 "LLM Basics" 文章', unlocked: false },
  { id: 'read_rag', name: 'RAG探索者', description: '阅读完 "RAG" 文章', unlocked: false },
  { id: 'read_prompt_engineering', name: '提示工程师', description: '阅读完 "Prompt Engineering" 文章', unlocked: false },
  { id: 'read_sft', name: '微调大师', description: '阅读完 "SFT" 文章', unlocked: false },
  { id: 'read_transformer', name: '变形金刚爱好者', description: '阅读完 "Transformer" 文章', unlocked: false },
  { id: 'interact_llm_basics', name: 'LLM基础互动家', description: '点击过 "LLM Basics" 页面所有交互按钮', unlocked: false },
  { id: 'interact_rag', name: 'RAG互动家', description: '点击过 "RAG" 页面所有交互按钮', unlocked: false },
  { id: 'interact_prompt_engineering', name: '提示工程互动家', description: '点击过 "Prompt Engineering" 页面所有交互按钮', unlocked: false },
  { id: 'interact_sft', name: 'SFT互动家', description: '点击过 "SFT" 页面所有交互按钮', unlocked: false },
  { id: 'interact_transformer', name: 'Transformer互动家', description: '点击过 "Transformer" 页面所有交互按钮', unlocked: false },
];

const achievements = ref(achievementList);

export function useAchievements() {
  const loadAchievements = () => {
    const saved = localStorage.getItem('achievements');
    if (saved) {
      const savedAchievements = JSON.parse(saved);
      achievements.value = achievementList.map(ach => {
        const savedAch = savedAchievements.find(sa => sa.id === ach.id);
        return savedAch ? savedAch : ach;
      });
    }
  };

  const saveAchievements = () => {
    localStorage.setItem('achievements', JSON.stringify(achievements.value));
  };

  const unlockAchievement = (id) => {
    const achievement = achievements.value.find(a => a.id === id);
    if (achievement && !achievement.unlocked) {
      achievement.unlocked = true;
      saveAchievements();
    }
  };

  const trackInteraction = (page, buttonId) => {
    const key = `interactions_${page}`;
    let interactions = JSON.parse(localStorage.getItem(key) || '[]');
    if (!interactions.includes(buttonId)) {
      interactions.push(buttonId);
      localStorage.setItem(key, JSON.stringify(interactions));
    }
  };

  onMounted(loadAchievements);

  return {
    achievements,
    unlockAchievement,
    trackInteraction
  };
}
