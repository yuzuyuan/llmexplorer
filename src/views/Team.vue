<template>
  <div class="container" style="padding: 2rem 0">
    <h1 style="text-align: center; margin-bottom: 2rem; font-weight: 600">Our Team</h1>
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
      We are a professional team dedicated to science popularization, focusing on transforming complex scientific knowledge into easily understandable content for everyone to enjoy.
    </p>

    <div class="team-grid">
      <div class="member-card" v-for="member in members" :key="member.name">
        <div class="member-avatar-container">
          <img :src="`/src/images/members/${member.image}`" :alt="member.name" class="member-avatar" />
        </div>
        <div class="member-info">
          <h3 class="member-name">{{ member.name }}</h3>
          <p class="member-bio">{{ member.bio }}</p>
          <router-link :to="member.route" class="member-link">View Details</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const members = [
  {
    name: 'Yu Zuyuan',
    bio: 'Leads the project\'s technical direction, responsible for full-stack architecture design and back-end development to ensure a robust and scalable platform.',
    image: 'yuzuyuan.jpg',
    route: '/member/yu-zuyuan'
  },
  {
    name: 'Waris',
    bio: 'Serves as the Chief Information Officer (CIO), overseeing the project\'s information strategy and ensuring all technical content is accurate and effectively organized.',
    image: 'waris.jpg',
    route: '/member/walis'
  },
    {
    name: 'Song Chuncheng',
    bio: 'Acts as the primary Quality Assurance Engineer, responsible for comprehensive testing to guarantee the platform\'s stability, functionality, and user experience.',
    image: 'Sok_Chhunheang.jpg',
    route: '/member/song-chuncheng'
  },
  {
    name: 'Li Jian',
    bio: 'Specializes in UI/UX design and front-end aesthetics, focusing on enhancing the visual appeal and ensuring an intuitive, polished user interface.',
    image: 'lijian.jpg',
    route: '/member/li-jian'
  },
  {
    name: 'Kyaw Kyaw Tun',
    bio: 'Drives the user interface enhancement efforts, concentrating on refining visual elements and overall user experience to create a compelling and engaging platform.',
    image: 'KyawKyawTun.jpg',
    route: '/member/kyaw-kyaw-tun'
  },
  {
    name: 'Wu Weilian',
    bio: 'Manages content research and documentation, responsible for gathering essential information and structuring it into clear, well-organized markdown files.',
    image: 'wuliam.jpg',
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
  min-height: 80px; /* 确保卡片高度大致一致 */
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