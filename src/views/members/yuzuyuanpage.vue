<template>
  <div class="member-profile-page">
    <!-- Profile Section -->
    <div class="profile-container">
      <div class="profile-pic-wrapper">
        <img src="@/images/members/yuzuyuan.jpg" alt="Yu Zuyuan" class="profile-pic" />
      </div>
      <h1 class="headline">Hi, I'm Yu Zuyuan! 💻</h1>
      <p class="bio">
        🎓 Software Engineering undergraduate / 🐍 "One-year Python practitioner" / 🎮 Anime &
        gaming dual-wielder
      </p>
    </div>

    <!-- Skills Section -->
    <div class="skills-container">
      <div class="skill">
        <div class="skill-label">Python</div>
        <div class="skill-bar-bg">
          <div class="skill-bar-fill" style="--width: 70%"></div>
        </div>
      </div>
      <div class="skill">
        <div class="skill-label">Web Dev</div>
        <div class="skill-bar-bg">
          <div class="skill-bar-fill" style="--width: 60%"></div>
        </div>
      </div>
      <div class="skill">
        <div class="skill-label">Game Design</div>
        <div class="skill-bar-bg">
          <div class="skill-bar-fill" style="--width: 65%"></div>
        </div>
      </div>
      <div class="skill">
        <div class="skill-label">Anime Analysis</div>
        <div class="skill-bar-bg">
          <div class="skill-bar-fill" style="--width: 95%"></div>
        </div>
      </div>
    </div>

    <!-- Gallery -->
    <div class="gallery-container">
      <div class="gallery-item">
        <img
          src="https://images.pexels.com/photos/207691/pexels-photo-207691.jpeg?auto=compress&cs=tinysrgb&w=600"
          alt="Code Doodles"
        />
      </div>
      <div class="gallery-item">
        <img
          src="https://images.pexels.com/photos/1674751/pexels-photo-1674751.jpeg?auto=compress&cs=tinysrgb&w=600"
          alt="Anime Sketch"
        />
      </div>
      <div class="gallery-item">
        <img
          src="https://images.pexels.com/photos/2872747/pexels-photo-2872747.jpeg?auto=compress&cs=tinysrgb&w=600"
          alt="Gaming UI"
        />
      </div>
      <div class="gallery-item">
        <img
          src="https://images.pexels.com/photos/5989130/pexels-photo-5989130.jpeg?auto=compress&cs=tinysrgb&w=600"
          alt="Pixel Art"
        />
      </div>
    </div>

    <!-- Navigation -->
    <div class="navigation-container">
      <router-link to="/group" class="nav-button">
        ← 返回小组页面
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
/* ========================
 BASE STYLES & RESET
 ======================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.member-profile-page {
  font-family: 'Quicksand', sans-serif;
  background-color: #f9f7f4;
  color: #555;
  line-height: 1.6;
  background-image:
    linear-gradient(
      0deg,
      transparent 24%,
      rgba(255, 255, 255, 0.8) 25%,
      rgba(255, 255, 255, 0.8) 26%,
      transparent 27%,
      transparent 74%,
      rgba(255, 255, 255, 0.8) 75%,
      rgba(255, 255, 255, 0.8) 76%,
      transparent 77%
    ),
    linear-gradient(
      90deg,
      transparent 24%,
      rgba(255, 255, 255, 0.8) 25%,
      rgba(255, 255, 255, 0.8) 26%,
      transparent 27%,
      transparent 74%,
      rgba(255, 255, 255, 0.8) 75%,
      rgba(255, 255, 255, 0.8) 76%,
      transparent 77%
    );
  background-size: 20px 20px;
  background-color: #fef8f0;
  position: relative;
  min-height: 100vh;
  padding: 20px;
}

/* Subtle pencil shading overlay */
.member-profile-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://www.transparenttextures.com/patterns/pencil-lines.png');
  opacity: 0.05;
  pointer-events: none;
  z-index: -1;
}

h1,
h2,
h3 {
  font-family: 'Fredoka One', cursive;
  color: #e75480;
}

p {
  font-family: 'Caveat', cursive;
  font-size: 1.1rem;
}

/* ========================
 SKETCHY BORDER UTILITY
 ======================== */
.sketch-border {
  border: 3px solid transparent;
  border-image: url('https://www.svgrepo.com/show/356584/sketch-border.svg') 30 stretch;
  border-image-slice: 30;
}

/* ========================
 PROFILE SECTION
 ======================== */
.profile-container {
  text-align: center;
  max-width: 900px;
  margin: 40px auto 20px;
  padding: 20px;
  position: relative;
}

.profile-pic {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  object-fit: cover;
  border: 6px solid #b2f2bb;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  background: white;
  transition: transform 0.3s ease;
}

.profile-pic:hover {
  transform: scale(1.05);
}

.profile-pic-wrapper {
  display: inline-block;
  padding: 8px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.profile-pic-wrapper::before {
  content: '';
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-image: url('https://www.svgrepo.com/show/356584/sketch-border.svg') 30 round;
  border-image-slice: 30;
  z-index: -1;
}

.headline {
  font-size: 2.5rem;
  margin: 20px 0 10px;
  color: #4a90e2;
  text-shadow: 2px 2px 0px #fff8dc;
}

.bio {
  max-width: 600px;
  margin: 0 auto 30px;
  font-size: 1.2rem;
  color: #666;
}

/* ========================
 SKILL BARS
 ======================== */
.skills-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin: 40px 0;
}

.skill {
  flex: 1 1 200px;
  min-width: 200px;
  background: #fff;
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  text-align: center;
  opacity: 0;
  transform: translateY(20px);
  animation: slideIn 0.6s forwards;
}

.skill:nth-child(1) {
  animation-delay: 0.2s;
}
.skill:nth-child(2) {
  animation-delay: 0.4s;
}
.skill:nth-child(3) {
  animation-delay: 0.6s;
}
.skill:nth-child(4) {
  animation-delay: 0.8s;
}

.skill-label {
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.skill-bar-bg {
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.skill-bar-fill {
  height: 100%;
  width: 0;
  background: linear-gradient(90deg, #4ecdc4, #ff6b6b);
  border-radius: 6px;
  animation: fillBar 1.5s ease-out forwards;
}

@keyframes fillBar {
  from {
    width: 0;
  }
  to {
    width: var(--width);
  }
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========================
 GALLERY
 ======================== */
.gallery-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-width: 800px;
  margin: 40px auto;
}

.gallery-item {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  transform: translateY(20px);
  animation: slideIn 0.6s forwards;
  position: relative;
}

.gallery-item:nth-child(1) {
  animation-delay: 0.3s;
}
.gallery-item:nth-child(2) {
  animation-delay: 0.5s;
}
.gallery-item:nth-child(3) {
  animation-delay: 0.7s;
}
.gallery-item:nth-child(4) {
  animation-delay: 0.9s;
}

.gallery-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

/* Pen-trace hover effect */
.gallery-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 0;
  border: 2px solid #e75480;
  opacity: 0;
  transition:
    width 0.4s ease,
    height 0.4s ease;
}

.gallery-item:hover::before {
  width: 100%;
  height: 100%;
  opacity: 1;
}

/* ========================
 NAVIGATION
 ======================== */
.navigation-container {
  text-align: center;
  margin: 40px 0 20px;
}

.nav-button {
  display: inline-block;
  padding: 12px 24px;
  background: #4a90e2;
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-button:hover {
  background: #3a7bc8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* ========================
 RESPONSIVE DESIGN
 ======================== */
@media (max-width: 768px) {
  .profile-container {
    padding: 10px;
  }

  .headline {
    font-size: 2rem;
  }

  .bio {
    font-size: 1.1rem;
    padding: 0 10px;
  }

  .skills-container {
    flex-direction: column;
    align-items: center;
  }

  .gallery-container {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>