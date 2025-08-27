<template>
  <div>
    <div class="container">
      <div class="card">
        <header>
          <div class="avatar">
            <!-- Fixed image name -->
            <img src="@/images/members/Sok_Chhunheang.jpg" alt="Sok Chhunheang" />
          </div>
          <div class="header-info">
            <h1>Hi — I'm Sok Chhunheang</h1>
          </div>
        </header>

        <section class="about">
          <p>
            I am a dedicated and curious student who thrives on learning, exploring new ideas, and
            applying knowledge in practical ways. Throughout my academic journey I have developed a
            strong foundation in critical thinking, effective communication, and collaborative
            problem-solving. I am passionate about both the process of learning and the outcomes it
            enables: turning concepts into projects, questions into experiments, and curiosity into
            concrete skills. My studies have given me exposure to a range of subjects, and I enjoy
            connecting knowledge across disciplines to create well-rounded solutions. In and outside
            of the classroom I pursue activities that help me grow intellectually and personally —
            from hands-on group projects and coding exercises to reading widely and taking part in
            community initiatives. These experiences have shaped my ability to manage time, set
            priorities, and adapt to new challenges.
          </p>
          <p>
            I value teamwork and the energy that comes from working with classmates and mentors.
            Group assignments taught me how to listen actively, divide responsibilities, and bring
            different perspectives together to reach a common goal. I also appreciate independent
            study because it builds discipline and depth of understanding; I enjoy researching
            topics of interest and turning that research into presentations or practical outcomes.
            Over time I have sharpened several technical and soft skills: note-taking and study
            strategies, basic-to-intermediate coding or technical literacy (depending on your
            major), data interpretation, and clear written and verbal expression. I strive to be
            organized and to approach tasks methodically, while leaving room for creativity and
            experimentation.
          </p>
          <p>
            Outside academics, I pursue hobbies that keep me balanced and curious. Whether it is
            creative writing, sketching, playing a sport, or volunteering locally, these activities
            broaden my perspective and help me develop empathy and resilience. I am interested in
            real-world applications of classroom learning, so I seek out project opportunities,
            internships, and competitions where I can apply theory to tangible problems. My
            short-term goals include deepening my understanding in my primary area of study,
            contributing to meaningful projects, and building a portfolio of work that showcases my
            growth. Long-term, I want to pursue a career that combines my passion and skills in a
            way that makes a positive impact — whether through innovation, education, or community
            service.
          </p>
          <p>
            I am excited about continuing to learn, collaborate, and take on challenges that stretch
            my abilities. I believe that consistent effort, curiosity, and openness to feedback are
            keys to long-term growth. If you want to reach out, collaborate on a project, or learn
            more about my experiences, please use the contact section below. Thank you for visiting
            my profile — I look forward to what comes next and the chance to build, learn, and grow
            alongside others.
          </p>
        </section>

        <div class="grid">
          <aside class="side">
            <h3>Quick info</h3>
            <p><strong>School:</strong> Beijing Institute of Technology</p>
            <p><strong>Major:</strong> Software Engineering</p>
            <p><strong>Year:</strong> Sophomore</p>
          </aside>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>

<style scoped>
:root {
  --bg: #f4f7fb;
  --card: #ffffff;
  --accent: #3b82f6;
  --muted: #6b7280;
}
body {
  font-family:
    Inter,
    system-ui,
    -apple-system,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial;
  background: var(--bg);
  margin: 0;
  color: #111;
}
.container {
  max-width: 900px;
  margin: 36px auto;
  padding: 24px;
}
.card {
  background: var(--card);
  border-radius: 14px;
  padding: 28px;
  box-shadow: 0 6px 20px rgba(16, 24, 40, 0.06);
}
header {
  display: flex;
  gap: 20px;
  align-items: center;
}
.avatar {
  width: 160px;
  height: 160px;
  border-radius: 12px;
  overflow: hidden;
  flex: 0 0 160px;
  border: 4px solid #fff;
  box-shadow: 0 6px 18px rgba(59, 130, 246, 0.12);
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.header-info h1 {
  margin: 0;
  font-size: 24px;
}
.header-info p {
  margin: 6px 0 0;
  color: var(--muted);
}
.about {
  margin-top: 20px;
  line-height: 1.68;
  font-size: 15px;
  color: #111;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 20px;
  margin-top: 22px;
}
.side {
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.03), transparent);
  padding: 16px;
  border-radius: 10px;
}
.side h3 {
  margin-top: 0;
}
footer {
  margin-top: 18px;
  color: var(--muted);
  font-size: 13px;
}
@media (max-width: 820px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .avatar {
    width: 120px;
    height: 120px;
    flex: 0 0 120px;
  }
}
</style>