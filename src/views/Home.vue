<template>
  <section class="hero-section">
    <div class="hero-content">
      <h1 class="hero-title">Explore the Infinite Possibilities of Science</h1>
      <p class="hero-subtitle">Dive deep into cutting-edge technology and scientific principles through clear and concise content.</p>
      <router-link to="/kb/1-llm-basics" class="btn">
        <i class="bi bi-compass"></i> Explore Articles
      </router-link>
    </div>
  </section>

  <div class="container">
    <h2 style="text-align: center; margin-bottom: 2rem; font-weight: 600">Popular Science Content</h2>

    <div class="articles-grid">
      <div class="card" v-for="item in modules" :key="item.title">
        <img :src="item.image" :alt="item.title" class="card-img" loading="lazy" />
        <div class="card-content">
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-excerpt">{{ item.desc }}</p>
          <router-link :to="item.link" class="card-link">
            Read More <i class="bi bi-arrow-right"></i>
          </router-link>
        </div>
      </div>
    </div>
  </div>

  <div class="container" style="margin-top: 4rem;">
    <div style="text-align: center; margin-bottom: 2rem;">
      <h2 style="font-weight: 600; color: #333;">Meet Our Team</h2>
      <p style="color: #666; margin-top: 0.5rem;">Get to know the professional team and developers behind the project.</p>
    </div>
    
    <div style="text-align: center; margin-bottom: 2rem;">
      <router-link 
        to="/team" 
        style="display: inline-block; padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: 500; transition: transform 0.2s ease;"
        onmouseover="this.style.transform='translateY(-2px)'" 
        onmouseout="this.style.transform='translateY(0)'"
      >
        👥 Meet Our Team
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
    title: 'LLM Basics',
    desc: 'Understand the architecture, training methods, and fundamental principles of large models to master core AI technologies from scratch.',
    link: '/kb/1-llm-basics',
    image:
      llmBasicsImage,
  },
  {
    title: 'Prompt Engineering',
    desc: 'Learn how to design effective prompts to guide model outputs and enhance the performance of your AI applications.',
    link: '/kb/2-prompt-engineering',
    image:
      promptEngineeringImage,
  },
  {
    title: 'RAG Technology',
    desc: 'Discover how to augment model capabilities with external knowledge bases to achieve more accurate and context-aware AI Q&A.',
    link: '/kb/3-rag',
    image:
      ragImage,
  },
  {
    title: 'Supervised Fine-Tuning',
    desc: 'Learn how to improve model performance on specific tasks through fine-tuning, allowing you to create customized AI assistants.',
    link: '/kb/4-sft',
    image:
      sftImage,
  }
]
</script>

<style scoped>
.hero-section {
  position: relative;
  height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('../assets/images/hero-bg.jpg');
  background-size: cover;
  background-position: center;
  filter: brightness(0.6);
  z-index: -1;
}

.hero-content {
  max-width: 800px;
  padding: 0 1rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #3b82f6;
  color: white;
  padding: 0.8rem 1.8rem;
  border-radius: 9999px;
  text-decoration: none;
  font-weight: 500;
  transition:
    background-color 0.3s ease,
    transform 0.3s ease;
}

.btn:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 1rem;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

.card-content {
  padding: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.card-excerpt {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.card-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.card-link:hover {
  color: #2563eb;
  text-decoration: underline;
}
</style>