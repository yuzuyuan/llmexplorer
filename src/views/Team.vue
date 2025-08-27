<template>
  <div class="container" style="padding: 2rem 0">
    <h1 style="text-align: center; margin-bottom: 2rem; font-weight: 600">我们的团队</h1>
    <p
      style="
        text-align: center;
        margin-bottom: 3rem;
        color: #616161;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
      "
    >
      我们是一支致力于科学普及的专业团队，专注于将复杂的科学知识转化为易于理解的内容，让每个人都能享受到科学的魅力。
    </p>

    <div class="team-grid">
      <div class="member-card" v-for="member in members" :key="member.name">
        <div class="member-avatar-container">
          <img :src="`/src/images/members/${member.image}`" :alt="member.name" class="member-avatar" />
        </div>
        <div class="member-info">
          <h3 class="member-name">{{ member.name }}</h3>
          <p class="member-bio">{{ member.bio }}</p>
          <router-link :to="member.route" class="member-link">查看详情</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const members = [
  {
    name: '喻祖源',
    bio: '软件工程师，Python开发者，动漫和游戏爱好者，专注于软件工程和大型语言模型应用开发。',
    image: 'yuzuyuan.jpg',
    route: '/member/yuzuyuan'
  },
  {
    name: '宋春成',
    bio: '后端开发工程师，Java和Python专家，系统架构师，专注于构建高性能、高可用的后端服务。',
    image: 'Sok_Chhunheang.jpg',
    route: '/member/sok_chhhunheangpage'
  },
  {
    name: '李剑',
    bio: '前端开发工程师，Vue.js和React专家，UI/UX爱好者，专注于用户体验设计。',
    image: '李剑.jpg',
    route: '/member/li-jian'
  },
  {
    name: '瓦里斯',
    bio: '算法工程师，机器学习和深度学习专家，专注于自然语言处理和计算机视觉技术研究。',
    image: '瓦里斯.jpg',
    route: '/member/walis'
  },
  {
    name: '赵子彦',
    bio: '产品经理，用户体验设计师，专注于界面设计和交互体验优化，追求简洁美观的设计风格。',
    image: '赵子彦.jpg',
    route: '/member/zhao-ziyan'
  },
  {
    name: '吴威廉',
    bio: 'UI/UX设计师，产品设计专家，擅长用户需求分析和产品规划，具有丰富的项目管理经验。',
    image: '吴威廉.jpg',
    route: '/member/wu-weilian'
  }
]
</script>

<style scoped>
.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.member-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.member-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.member-avatar-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.member-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.member-info {
  padding: 1.5rem;
}

.member-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.member-bio {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.member-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.member-link:hover {
  color: #2563eb;
  text-decoration: underline;
}
</style>