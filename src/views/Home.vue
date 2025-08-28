<template>
  <section class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title">探索科学的无限可能</h1>
      <p class="hero-subtitle">通过简洁易懂的内容，深入了解前沿科技与科学原理</p>
      <router-link to="/kb/1-llm-basics" class="btn">
        <i class="bi bi-compass"></i> 探索文章
      </router-link>
    </div>
  </section>

  <div class="container">
    <h2 style="text-align: center; margin-bottom: 2rem; font-weight: 600">热门科普内容</h2>

    <div class="articles-grid">
      <div class="card" v-for="item in modules" :key="item.title">
        <img :src="item.image" :alt="item.title" class="card-img" loading="lazy" />
        <div class="card-content">
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-excerpt">{{ item.desc }}</p>
          <router-link :to="item.link" class="card-link">
            阅读更多 <i class="bi bi-arrow-right"></i>
          </router-link>
        </div>
      </div>
    </div>
  </div>

  <!-- 新增小组介绍区域 -->
  <div class="container" style="margin-top: 4rem;">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="font-weight: 600; color: #333;">认识我们的团队</h2>
      <p style="color: #666; margin-top: 0.5rem;">了解背后的专业团队和开发者</p>
    </div>
    
    <div style="text-align: center; margin-bottom: 2rem;">
      <router-link 
        to="/team" 
        style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: 500; transition: transform 0.2s ease;"
        onmouseover="this.style.transform='translateY(-2px)'" 
        onmouseout="this.style.transform='translateY(0)'"
      >
        👥 认识我们的小组
      </router-link>
    </div>
  </div>
</template>

<script setup>
import llmBasicsImage from '@/assets/images/tokenizer.png';
import promptEngineeringImage from '@/assets/images/prompt.png';
import ragImage from '@/assets/images/rag.png';
import sftImage from '@/assets/images/sft.png';
const modules = [
  {
    title: '大模型基础',
    desc: '了解大模型的架构、训练方式与基本原理，从零开始掌握AI核心技术。',
    link: '/kb/1-llm-basics',
    image:
      llmBasicsImage,
  },
  {
    title: 'Prompt 工程',
    desc: '掌握如何设计有效的 Prompt 来引导模型输出，提升AI应用效果。',
    link: '/kb/2-prompt-engineering',
    image:
      promptEngineeringImage,
  },
  {
    title: 'RAG 技术',
    desc: '学习如何结合外部知识库增强模型能力，实现更精准的AI问答。',
    link: '/kb/3-rag',
    image:
      ragImage,
  },
  {
    title: '有监督微调',
    desc: '了解如何通过微调提升模型在特定任务上的表现，定制专属AI助手。',
    link: '/kb/4-sft',
    image:
      sftImage,
  }
]

// 保持原有功能不变，只增加新功能
</script>