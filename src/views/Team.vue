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
        <img :src="member.avatar" :alt="member.name" class="member-avatar" />
        <div class="member-info">
          <h3 class="member-name">{{ member.name }}</h3>
          <p class="member-bio">{{ member.bio }}</p>
          <a href="#" class="member-link">查看详情</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const members = [
  {
    name: '张明',
    bio: 'AI研究员，擅长大模型架构设计与优化，拥有丰富的科研经验。',
    avatar:
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80',
  },
  {
    name: '李华',
    bio: '前端开发工程师，专注于用户体验设计，致力于打造简洁美观的界面。',
    avatar:
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80',
  },
  {
    name: '王强',
    bio: '内容策划专家，负责科普内容的创作与编辑，确保内容的准确性和趣味性。',
    avatar:
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80',
  },
  {
    name: '陈丽',
    bio: '产品经理，统筹项目规划与执行，确保平台功能满足用户需求。',
    avatar:
      'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80',
  },
]
</script>
