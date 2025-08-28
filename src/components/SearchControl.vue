<template>
  <div v-if="visible" class="search-control-wrapper">
    <div class="search-info">
      <span class="search-term">{{ searchTerm }}</span>
      <span v-if="total > 0" class="search-count">{{ currentIndex + 1 }} / {{ total }}</span>
      <span v-else class="search-count">未找到</span>
    </div>
    <div class="search-actions">
      <button @click="$emit('previous')" :disabled="total === 0" class="btn btn-sm btn-light me-2">
        <i class="bi bi-arrow-up"></i>
      </button>
      <button @click="$emit('next')" :disabled="total === 0" class="btn btn-sm btn-light me-2">
        <i class="bi bi-arrow-down"></i>
      </button>
      <button @click="$emit('close')" class="btn btn-sm btn-light">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  searchTerm: String,
  currentIndex: Number,
  total: Number,
});

defineEmits(['next', 'previous', 'close']);
</script>

<style scoped>
.search-control-wrapper {
  position: fixed;
  top: 80px; /* 避免与顶部导航栏重叠 */
  right: 20px;
  z-index: 1050;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  padding: 10px 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.3s ease-in-out;
}
.search-term {
  font-weight: bold;
  margin-right: 8px;
}
.search-count {
  background-color: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
.search-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}
</style>