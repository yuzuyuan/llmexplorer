<template>
  <div class="profile-body">
    <div class="container">
      <div class="card">
        <header>
          <div class="header-content">
            <img
              src="@/images/members/waris.jpg"
              alt="Waris"
              class="avatar"
            />
            <div class="info">
              <h1>Waris</h1>
              <h2>Computer Science & Software Engineering Student</h2>
              <p>Beijing Institute of Technology</p>
            </div>
          </div>
        </header>

        <main class="content">
          <section class="about">
            <h3><i class="fas fa-user-circle"></i> 关于我</h3>
            <p>
              Hello everyone, I’m Waris, and it’s a pleasure to share a bit about myself. I’m currently pursuing a degree in Computer Science and Software Engineering at the prestigious Beijing Institute of Technology (BIT)—a university renowned for its strength in engineering and technological innovation, which has deeply shaped my academic foundation and problem-solving mindset.
            </p>
            <p>
              At BIT, my coursework has focused on core areas like data structures, algorithms, object-oriented programming, and software development methodologies, where I’ve consistently aimed to translate theoretical knowledge into practical skills. For instance, last semester, I led a 4-person team to develop a campus event-management app using Java and MySQL. We designed features for event registration, reminder notifications, and feedback collection, which was later adopted by the university’s student union to streamline event organization—this project not only honed my coding and collaborative abilities but also fueled my passion for building software that solves real-life needs.
            </p>
            <p>
              Beyond academics, I’m an active member of BIT’s Software Development Club, where I participate in monthly hackathons and tech workshops to stay updated on emerging technologies like cloud computing and artificial intelligence. I’m also currently learning Python for machine learning in my free time, as I hope to explore how software engineering can intersect with AI to create more intelligent solutions.
            </p>
            <p>
              I’m a detail-oriented, proactive learner who thrives on challenges, whether it’s debugging complex code or brainstorming innovative project ideas. I’m excited to connect with peers and professionals in the field, exchange insights, and continue growing as a software engineer. Thank you!
            </p>
          </section>

          <section class="skills">
            <h3><i class="fas fa-cogs"></i> 技能</h3>
            <div class="skill-grid">
              <div class="skill-item">
                <i class="fab fa-java"></i><span>Java</span>
              </div>
              <div class="skill-item">
                <i class="fas fa-database"></i><span>MySQL</span>
              </div>
              <div class="skill-item">
                <i class="fab fa-python"></i><span>Python</span>
              </div>
               <div class="skill-item">
                <i class="fas fa-brain"></i><span>Machine Learning</span>
              </div>
              <div class="skill-item"><i class="fab fa-git-alt"></i><span>Git</span></div>
            </div>
          </section>

          <section class="contact">
            <h3><i class="fas fa-envelope"></i> 联系方式</h3>
            <div class="contact-grid">
              <a href="mailto:waris@example.com" class="contact-item"
                ><i class="fas fa-envelope-open-text"></i> waris@example.com</a
              >
              <a
                href="#"
                target="_blank"
                class="contact-item"
                ><i class="fab fa-linkedin"></i> LinkedIn</a
              >
              <a href="#" target="_blank" class="contact-item"
                ><i class="fab fa-github"></i> GitHub</a
              >
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
  </div>
</template>

<script setup>
// 此静态页面无需脚本逻辑
</script>

<style scoped>
:root {
  --primary: #2563eb;
  --secondary: #1e40af;
  --accent: #3b82f6;
  --light: #f8fafc;
  --dark: #1e293b;
  --text: #334155;
  --muted: #64748b;
  --border: #e2e8f0;
  --card: #ffffff;
  --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.profile-body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.container {
  max-width: 900px;
  width: 100%;
}

.card {
  background: var(--card);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  transform: translateY(-5px);
}

header {
  background: linear-gradient(120deg, var(--primary), var(--secondary));
  color: white;
  padding: 40px;
  text-align: center;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 5px solid white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
  object-fit: cover;
  margin-bottom: 20px;
}

.info h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
}

.info h2 {
  font-size: 1.25rem;
  font-weight: 400;
  color: var(--light);
  opacity: 0.9;
  margin: 5px 0 0;
}

.info p {
  margin-top: 5px;
  font-style: italic;
  opacity: 0.8;
}

.content {
  padding: 30px 40px;
}

section {
  margin-bottom: 30px;
}

section.about p {
    margin-bottom: 1em; /* 为段落之间增加一些间距 */
}

section h3 {
  font-size: 1.5rem;
  color: var(--primary);
  margin-bottom: 15px;
  padding-bottom: 5px;
  border-bottom: 2px solid var(--border);
  display: flex;
  align-items: center;
}

section h3 i {
  margin-right: 10px;
}

.skill-grid,
.contact-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.skill-item,
.contact-item {
  background: var(--light);
  border-radius: 8px;
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  transition: var(--transition);
  text-decoration: none;
  color: var(--text);
}

.skill-item:hover,
.contact-item:hover {
  background: var(--accent);
  color: white;
  transform: scale(1.05);
}

.skill-item i,
.contact-item i {
  color: var(--accent);
  transition: var(--transition);
}

.skill-item:hover i,
.contact-item:hover i {
  color: white;
}
.navigation-container {
  text-align: center;
  margin: 20px 0 40px; /* 调整了边距 */
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
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>