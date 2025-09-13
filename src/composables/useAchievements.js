import { ref } from 'vue';

// 定义 localStorage 中存储成就的键名
const ACHIEVEMENTS_STORAGE_KEY = 'llm_explorer_achievements';

export function useAchievements() {
  const achievements = ref([
  { id: 'read_llm_basics', title: 'LLM基础入门', description: '阅读完 "LLM Basics" 文章', unlocked: false },
  { id: 'read_rag', title: 'RAG探索者', description: '阅读完 "RAG" 文章', unlocked: false },
  { id: 'read_prompt_engineering', title: '提示工程师', description: '阅读完 "Prompt Engineering" 文章', unlocked: false },
  { id: 'read_sft', title: '微调大师', description: '阅读完 "SFT" 文章', unlocked: false },
  { id: 'read_transformer', title: '变形金刚爱好者', description: '阅读完 "Transformer" 文章', unlocked: false },
  { id: 'interact_llm_basics', title: 'LLM基础互动家', description: '点击过 "LLM Basics" 页面所有交互按钮', unlocked: false },
  { id: 'interact_rag', title: 'RAG互动家', description: '点击过 "RAG" 页面所有交互按钮', unlocked: false },
  { id: 'interact_prompt_engineering', title: '提示工程互动家', description: '点击过 "Prompt Engineering" 页面所有交互按钮', unlocked: false },
  { id: 'interact_sft', title: 'SFT互动家', description: '点击过 "SFT" 页面所有交互按钮', unlocked: false },
  { id: 'interact_transformer', title: 'Transformer互动家', description: '点击过 "Transformer" 页面所有交互按钮', unlocked: false },
  {
      id: 'quiz_master_5',
      title: '初学者',
      description: '正确回答5道测验题。',
      unlocked: false,
      icon: 'bi-patch-question-fill',
    },
    {
      id: 'quiz_master_10',
      title: '知识大师',
      description: '正确回答10道测验题。',
      unlocked: false,
      icon: 'bi-trophy-fill',
    },
]);

  // 从 localStorage 加载成就状态
  const loadAchievements = () => {
    try {
      const storedAchievements = JSON.parse(localStorage.getItem(ACHIEVEMENTS_STORAGE_KEY));
      if (storedAchievements) {
        achievements.value.forEach(achievement => {
          const stored = storedAchievements.find(s => s.id === achievement.id);
          if (stored) {
            achievement.unlocked = stored.unlocked;
          }
        });
      }
    } catch (e) {
      console.error("Failed to load achievements from localStorage", e);
    }
  };

  // 保存成就状态到 localStorage
  const saveAchievements = () => {
    localStorage.setItem(ACHIEVEMENTS_STORAGE_KEY, JSON.stringify(achievements.value));
  };
  const trackInteraction = (pageId, interactionId) => {
  const storageKey = `interactions_${pageId}`;
  try {
    const interactions = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (!interactions.includes(interactionId)) {
      interactions.push(interactionId);
      localStorage.setItem(storageKey, JSON.stringify(interactions));
      console.log(`Interaction tracked for ${pageId}: ${interactionId}`);
    }
  } catch (e) {
    console.error(`Failed to track interaction for ${pageId}`, e);
  }
};


  const unlockAchievement = (id) => {
    const achievement = achievements.value.find((a) => a.id === id);
    if (achievement && !achievement.unlocked) {
      achievement.unlocked = true;
      saveAchievements();
      console.log(`Achievement Unlocked: ${achievement.title}`);

      // 发出全局事件以触发通知动画
      window.dispatchEvent(new CustomEvent('achievementUnlocked', {
        detail: achievement
      }));
    }
  };

  // 检查并自动解锁某些成就
  const checkAchievements = () => {
    loadAchievements();

    if (!localStorage.getItem('visited_llm_explorer')) {
        localStorage.setItem('visited_llm_explorer', 'true');
    }
    unlockAchievement('welcome_explorer');
  };

  // 初始加载
  loadAchievements();

  return {
    achievements,
    unlockAchievement,
    checkAchievements,
    trackInteraction,
  };
} // <-- 这个是函数的右括号，后面不应再有其他括号
