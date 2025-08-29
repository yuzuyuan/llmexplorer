<template>
  <div class="profile-page-wrapper">
    <nav class="nav" aria-label="Primary">
      <div class="container nav-inner">
        <a class="brand" href="#home" aria-label="Go to top">
          <span class="brand-badge" aria-hidden="true">WG</span>
          <span>Wulliam&nbsp;Gosandra <span lang="zh-Hans">（吴威廉）</span></span>
        </a>
        <div class="nav-controls" style="display: flex; align-items: center; gap: 8px">
          <button
            class="theme-toggle"
            id="themeToggle"
            aria-label="Toggle color theme"
            title="Toggle theme"
            @click="toggleTheme"
          >
            <span aria-hidden="true">🌓</span>
          </button>
          <button class="menu-toggle" id="menuToggle" aria-label="Toggle menu" @click="toggleMenu">
            ☰
          </button>
        </div>
        <div class="nav-links" id="navLinks" role="navigation">
          <a href="#about">About</a>
          <a href="#skills">Skills</a>
        </div>
      </div>
    </nav>

    <header id="home" class="section">
      <div class="container hero">
        <div>
          <div class="kicker">Hello, I'm</div>
          <h1>Wulliam Gosandra <span lang="zh-Hans">（吴威廉）</span></h1>
          <p class="lead">
            Fifth‑year <strong>Software Engineering</strong> student who loves crafting clean,
            accessible interfaces. I'm skilled in <strong>CSS</strong>, <strong>JavaScript</strong>,
            and <strong>HTML</strong> — with a keen eye for detail and performance.
          </p>
        </div>
        <div class="card" aria-label="Profile preview">
          <div class="portrait">
            <picture>
              <source type="image/avif" src="@/images/members/wuliam.jpg" />
              <source type="image/webp" src="@/images/members/wuliam.jpg" />
              <img
                src="@/images/members/wuliam.jpg"
                alt="Portrait of Wulliam Gosandra（吴威廉）"
                loading="lazy"
                width="600"
                height="600"
              />
            </picture>
          </div>
          <div class="spacer"></div>
          <div class="muted" style="font-size: 0.95rem">
            Open to internships and junior roles. Passionate about front‑end architecture and design
            systems.
          </div>
        </div>
      </div>
    </header>

    <section id="about" class="section">
      <div class="container grid-2">
        <div class="card">
          <h2>About me</h2>
          <p>
            I'm a fifth‑year Software Engineering major focused on the front‑end. My strengths are
            semantic HTML, modern CSS (Grid, Flexbox, custom properties), and JavaScript for
            interactive UI. I value accessibility, maintainability, and great developer experience.
          </p>
          <p>
            When I'm not polishing pixels, I'm exploring performance profiling, writing small UI
            libraries, or studying code readability and design systems.
          </p>
        </div>
        <div class="card">
          <h2>At a glance</h2>
          <ul>
            <li><strong>Major:</strong> Software Engineering</li>
            <li><strong>Course:</strong> 软件工程基础训练</li>
            <li><strong>Core skills:</strong> CSS, JavaScript, HTML</li>
            <li><strong>Interests:</strong> UI/UX, design systems, web performance</li>
            <li><strong>Looking for:</strong> Front‑end internships or junior roles</li>
          </ul>
        </div>
      </div>
    </section>

    <section id="skills" class="section">
      <div class="container">
        <h2>Skills</h2>
        <div class="chips" aria-label="Skill tags">
          <span class="chip">CSS</span>
          <span class="chip">JavaScript</span>
          <span class="chip">HTML</span>
          <span class="chip">Responsive Design</span>
          <span class="chip">Accessibility (a11y)</span>
          <span class="chip">Git</span>
        </div>
        <div class="grid-2" style="margin-top: 14px">
          <div class="card">
            <strong>CSS</strong>
            <div class="meter" aria-hidden="true"><span style="width: 92%"></span></div>
            <p class="muted">Grid/Flexbox, custom properties, animations, theming, BEM/CUBE conventions.</p>
          </div>
          <div class="card">
            <strong>JavaScript</strong>
            <div class="meter" aria-hidden="true"><span style="width: 84%"></span></div>
            <p class="muted">ES202x, modular patterns, fetch/async, IntersectionObserver, accessible widgets.</p>
          </div>
          <div class="card">
            <strong>HTML</strong>
            <div class="meter" aria-hidden="true"><span style="width: 90%"></span></div>
            <p class="muted">Semantic structure, landmarks, metadata/SEO, forms, microdata/JSON‑LD.</p>
          </div>
          <div class="card">
            <strong>Collaboration</strong>
            <div class="meter" aria-hidden="true"><span style="width: 78%"></span></div>
            <p class="muted">Git & code reviews, docs, agile teamwork, attention to detail.</p>
          </div>
        </div>
      </div>
    </section>

    <footer>
      <div
        class="container"
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        "
      >
        <span class="muted">© {{ new Date().getFullYear() }} Wulliam Gosandra</span>
        <router-link to="/team" class="nav-button"> ← 返回小组页面 </router-link>
        <span class="muted">Built with semantic HTML, modern CSS, and vanilla JS</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

// --- 主题切换 ---
const toggleTheme = () => {
  const root = document.documentElement;
  const current = root.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
};

// --- 移动端菜单 ---
const toggleMenu = () => {
  const navLinks = document.getElementById('navLinks');
  if (navLinks) {
    navLinks.classList.toggle('open');
  }
};

// --- 滚动监听 ---
let observer;
onMounted(() => {
  // 设置初始主题
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
  }

  // 设置滚动高亮
  const navLinksContainer = document.getElementById('navLinks');
  if (navLinksContainer) {
    const links = [...navLinksContainer.querySelectorAll('a')];
    const sections = links.map(a => document.querySelector(a.getAttribute('href')));
    
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const idx = sections.indexOf(entry.target);
        if (idx !== -1) {
          const link = links[idx];
          if (entry.isIntersecting) {
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
          }
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px', threshold: 0 });
    
    sections.forEach(sec => sec && observer.observe(sec));
  }
});

// --- 组件卸载时清理 ---
onUnmounted(() => {
  if (observer) {
    observer.disconnect();
  }
  // 恢复默认主题以避免影响其他页面
  document.documentElement.removeAttribute('data-theme');
});
</script>

<style scoped>
/* 复制 wuweilian.html 中 <style> 标签内的所有 CSS 规则 */
:root {
  --bg: #0b0d10; /* dark background */
  --surface: #11151a; /* cards, nav */
  --muted: #9aa4af; /* subtle text */
  --text: #e6e8eb; /* primary text */
  --brand: #7c5cff; /* accent */
  --brand-2: #24c1e0; /* secondary accent */
  --ring: #2b3a55; /* focus ring */
  --ok: #1dd1a1;
  --warn: #feca57;
  --shadow: 0 10px 30px rgba(0, 0, 0, 0.35), 0 2px 10px rgba(0, 0, 0, 0.25);
}

.profile-page-wrapper:global([data-theme='light']) {
  --bg: #f7f8fb;
  --surface: #ffffff;
  --muted: #667085;
  --text: #0b0d10;
  --brand: #5a3cff;
  --brand-2: #1099bb;
  --ring: #c7d2fe;
  --shadow: 0 12px 30px rgba(16, 24, 40, 0.08), 0 4px 10px rgba(16, 24, 40, 0.06);
}

* {
  box-sizing: border-box;
}
html {
  scroll-behavior: smooth;
}
.profile-page-wrapper {
  background: radial-gradient(1200px 600px at 10% -10%, rgba(124, 92, 255, 0.15), transparent 60%),
    radial-gradient(800px 600px at 100% 10%, rgba(36, 193, 224, 0.12), transparent 60%),
    var(--bg);
  color: var(--text);
  font: 16px/1.6 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial,
    'Apple Color Emoji', 'Segoe UI Emoji';
}
a {
  color: var(--brand-2);
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

/* Layout */
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}
.section {
  padding: 80px 0;
}
@media (max-width: 720px) {
  .section {
    padding: 64px 0;
  }
}

/* Navbar */
.nav {
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: saturate(180%) blur(12px);
  background: color-mix(in oklab, var(--surface) 70%, transparent);
  border-bottom: 1px solid color-mix(in oklab, var(--surface) 85%, white 15%);
}
.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  letter-spacing: 0.2px;
}
.brand-badge {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  box-shadow: var(--shadow);
  color: white;
  font-weight: 800;
}
.nav-links {
  display: flex;
  gap: 18px;
  align-items: center;
}
.nav-links a {
  padding: 8px 10px;
  border-radius: 10px;
  font-weight: 600;
  color: var(--muted);
}
.nav-links a.active,
.nav-links a:hover {
  color: var(--text);
  background: color-mix(in oklab, var(--surface) 70%, white 5%);
}

.theme-toggle,
.menu-toggle {
  border: 1px solid color-mix(in oklab, var(--surface) 80%, white 10%);
  background: color-mix(in oklab, var(--surface) 60%, white 5%);
  color: var(--text);
  border-radius: 12px;
  padding: 8px 10px;
  cursor: pointer;
}
.menu-toggle {
  display: none;
}

@media (max-width: 900px) {
  .nav-links {
    display: none;
    position: absolute;
    top: 64px;
    left: 0;
    right: 0;
    padding: 10px 20px;
    background: var(--surface);
    border-bottom: 1px solid color-mix(in oklab, var(--surface) 85%, white 15%);
  }
  .nav-links.open {
    display: grid;
    gap: 8px;
  }
  .menu-toggle {
    display: inline-flex;
  }
}

/* Hero */
.hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 36px;
  align-items: center;
}
@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
  }
}
.kicker {
  color: var(--brand-2);
  font-weight: 700;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  font-size: 0.8rem;
}
h1 {
  font-size: clamp(2rem, 5vw, 3.25rem);
  line-height: 1.1;
  margin: 10px 0 16px;
}
.lead {
  font-size: clamp(1rem, 2.2vw, 1.2rem);
  color: var(--muted);
  max-width: 60ch;
}
.card {
  background: var(--surface);
  border: 1px solid color-mix(in oklab, var(--surface) 85%, white 15%);
  border-radius: 18px;
  padding: 22px;
  box-shadow: var(--shadow);
}
.portrait {
  aspect-ratio: 1 / 1;
  width: 100%;
  border-radius: 16px;
  overflow: hidden; /* 新增，确保图片在容器内 */
}

/* 新增 */
.portrait img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* About */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}
@media (max-width: 900px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}

/* Skills */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0 6px;
}
.chip {
  padding: 8px 12px;
  border-radius: 999px;
  background: color-mix(in oklab, var(--surface) 70%, white 6%);
  border: 1px solid color-mix(in oklab, var(--surface) 80%, white 10%);
  font-weight: 700;
}
.meter {
  height: 10px;
  background: color-mix(in oklab, var(--surface) 70%, white 3%);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid color-mix(in oklab, var(--surface) 80%, white 12%);
}
.meter > span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--brand), var(--brand-2));
}

/* Footer */
footer {
  padding: 40px 0;
  color: var(--muted);
}
.nav-button {
  display: inline-block;
  padding: 8px 16px;
  background: var(--brand);
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.nav-button:hover {
  background: var(--brand-2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  text-decoration: none;
}

/* Utilities */
.muted {
  color: var(--muted);
}
.spacer {
  height: 16px;
}
</style>