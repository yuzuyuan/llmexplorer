<template>
  <footer class="app-footer">
    <div class="container footer-content">
      <div class="footer-info">
        <p>&copy; {{ new Date().getFullYear() }} LLM Explorer. All Rights Reserved.</p>
        <p>An interactive educational project designed to demystify Large Language Models.</p>
      </div>
      <div class="footer-links">
        <router-link to="/" class="footer-link">Home</router-link>
        <router-link to="/team" class="footer-link">Our Team</router-link>
        </div>
    </div>
  </footer>
</template>

<script setup>
// No script changes needed
</script>

<style scoped>
/* Styles remain the same */
.app-footer {
  background-color: #f9fafb;
  border-top: 1px solid #e5e7eb;
  padding: 2rem 0;
  color: #6b7280;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-info p {
  margin: 0;
  font-size: 0.9rem;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-link {
  text-decoration: none;
  color: #6b7280;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #3b82f6;
}
</style>