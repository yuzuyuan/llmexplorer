<template>
  <div class="card h-100">
    <img :src="avatar" class="card-img-top" alt="Avatar" style="height: 150px; object-fit: cover" />
    <div class="card-body">
      <h5 class="card-title">{{ name }}</h5>
      <p class="card-text">{{ bio }}</p>
      <a href="#" class="btn btn-outline-primary">查看详情</a>
    </div>
  </div>
</template>

<script setup>
defineProps({
  name: String,
  bio: String,
  avatar: String,
})
</script>
