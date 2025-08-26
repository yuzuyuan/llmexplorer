<template>
  <div class="d-flex flex-column min-vh-100">
    <AppHeader />
    <main>
      <router-view />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
</script>
