<template>
  <div class="profile-body">
    <div class="profile-card">
      <header class="profile-header">
        <img src="@/images/members/lijian.jpg" alt="李剑" class="profile-avatar" />
        <h1 class="profile-name">李剑</h1>
        <p class="profile-subtitle">软件工程专业学生 | 终身学习者</p>
      </header>

      <main class="profile-content">
        <section class="about-section">
          <h2 class="section-title">关于我</h2>
          <p class="about-text">
            大家好！我是李剑，一名来自中国的软件工程专业在读学生。欢迎来到我的个人主页，很高兴能在这里与你相遇。我深信代码具有重塑世界的力量，并对通过技术解决实际问题充满热情。我的学术之旅不仅让我掌握了坚实的编程基础，更培养了我严谨的逻辑思维和持续学习的能力。
          </p>
          <p class="about-text">
            在代码的世界之外，我同样享受生活的多元与精彩。阅读是我获取新知、拓宽视野的重要途径，无论是技术专著还是文学经典，都能让我沉浸其中。规律的体育锻炼则是我保持活力和专注的秘诀，它塑造了我坚韧不拔的品格。此外，电子游戏不仅是我的娱乐方式，更是我洞察交互设计、理解用户心理的窗口。我乐于迎接挑战，并享受在学习与探索中不断成长的过程。
          </p>
        </section>

        <section class="interests-section">
          <h2 class="section-title">兴趣爱好</h2>
          <div class="interests-grid">
            <div class="interest-item">
              <i class="fas fa-book-open"></i>
              <span>阅读</span>
            </div>
            <div class="interest-item">
              <i class="fas fa-dumbbell"></i>
              <span>锻炼</span>
            </div>
            <div class="interest-item">
              <i class="fas fa-gamepad"></i>
              <span>游戏</span>
            </div>
            <div class="interest-item">
              <i class="fas fa-code"></i>
              <span>编程</span>
            </div>
          </div>
        </section>
      </main>

      <div class="navigation-container">
        <router-link to="/team" class="nav-button">
          ← 返回小组页面
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Font Awesome 图标库的 CDN 链接已在 index.html 中全局引入，这里无需额外处理
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.profile-body {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
  padding: 2rem;
  font-family: 'Inter', sans-serif;
}

.profile-card {
  width: 100%;
  max-width: 800px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.profile-header {
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.profile-avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 5px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  object-fit: cover;
  margin-bottom: 1rem;
}

.profile-name {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 1px;
}

.profile-subtitle {
  font-size: 1.1rem;
  font-weight: 300;
  opacity: 0.9;
  margin-top: 0.5rem;
}

.profile-content {
  padding: 2.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #764ba2;
  display: inline-block;
}

.about-text {
  font-size: 1rem;
  line-height: 1.8;
  color: #555;
  margin-bottom: 1rem;
}

.interests-section {
  margin-top: 2rem;
}

.interests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.interest-item {
  background: #f0f0f0;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  color: #555;
  transition: all 0.3s ease;
}

.interest-item:hover {
  background: #764ba2;
  color: white;
  transform: translateY(-5px);
}

.interest-item i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.navigation-container {
  text-align: center;
  padding: 0 2.5rem 2.5rem;
}

.nav-button {
  display: inline-block;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-button:hover {
  background: #764ba2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 响应式设计 */
@media (max-width: 600px) {
  .profile-body {
    padding: 1rem;
  }
  .profile-content {
    padding: 1.5rem;
  }
  .profile-avatar {
    width: 120px;
    height: 120px;
  }
  .profile-name {
    font-size: 2rem;
  }
}
</style>
