<template>
  <div class="member-page-body">
    <div class="member-page-container">
      <div class="member-card">
        <div class="member-card-header">
          <img src="/images/members/lijian.jpg" alt="Li Jian" class="member-avatar" />
          <div class="member-info">
            <h1>Li Jian</h1>
            <p>Software Engineering Student | Lifelong Learner</p>
          </div>
        </div>
        <div class="member-card-body">
          <div class="member-section">
            <h2><i class="fas fa-user"></i> About Me</h2>
            <p>
              Hello everyone! I'm Li Jian, a software engineering student from China. Welcome to my personal homepage. It's a pleasure to meet you here. I firmly believe that code has the power to reshape the world and I am passionate about solving practical problems through technology. My academic journey has not only given me a solid foundation in programming, but also cultivated my rigorous logical thinking and ability to learn continuously.
            </p>
            <p>
              Outside the world of code, I also enjoy the diversity and excitement of life. Reading is an important way for me to acquire new knowledge and broaden my horizons. Whether it's technical monographs or literary classics, I can immerse myself in them. Regular physical exercise is the secret to my vitality and focus, and it has shaped my tenacious character. In addition to video games being my entertainment, they are also a window for me to gain insight into interactive design and understand user psychology. I am happy to meet challenges and enjoy the process of continuous growth in learning and exploration.
            </p>
          </div>
          <div class="member-section">
            <h2><i class="fas fa-heart"></i> Interests</h2>
            <div class="interests-grid">
              <div class="interest-item">
                <i class="fas fa-book"></i>
                <span>Reading</span>
              </div>
              <div class="interest-item">
                <i class="fas fa-dumbbell"></i>
                <span>Exercise</span>
              </div>
              <div class="interest-item">
                <i class="fas fa-gamepad"></i>
                <span>Gaming</span>
              </div>
              <div class="interest-item">
                <i class="fas fa-code"></i>
                <span>Programming</span>
              </div>
            </div>
          </div>
        </div>
        <div class="member-card-footer">
          <router-link to="/team" class="back-link-btn">Back to Team Page</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LiJianPage',
};
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.member-page-body {
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Poppins', sans-serif;
  padding: 2rem;
}

.member-page-container {
  max-width: 800px;
  width: 100%;
}

.member-card {
  background-color: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.member-card:hover {
  transform: translateY(-10px);
}

.member-card-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.member-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid white;
  object-fit: cover;
}

.member-info h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.member-info p {
  margin: 0;
  font-size: 1rem;
  opacity: 0.9;
}

.member-card-body {
  padding: 2rem;
}

.member-section {
  margin-bottom: 2rem;
}

.member-section:last-child {
  margin-bottom: 0;
}

.member-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.member-section p {
  line-height: 1.8;
  color: #555;
  text-align: justify;
}

.interests-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center; /* Center items in the grid */
  margin-top: 1.5rem;
}

.interest-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f0f2f5;
  border-radius: 15px;
  padding: 1rem 1.5rem;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.interest-item:hover {
  background: linear-gradient(45deg, #a1c4fd, #c2e9fb);
  color: #333;
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.interest-item i {
  font-size: 2.5rem;
  color: #667eea;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.interest-item:hover i {
  color: #333; /* Darker color on hover */
}

.interest-item span {
  font-weight: 500;
  color: #555;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.interest-item:hover span {
  color: #333;
}


.member-card-footer {
  background-color: #f8f9fa;
  padding: 1.5rem;
  text-align: center;
}

.back-link-btn {
  background: none;
  border: 2px solid #667eea;
  color: #667eea;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  border-radius: 30px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-link-btn:hover {
  background-color: #667eea;
  color: white;
}
</style>