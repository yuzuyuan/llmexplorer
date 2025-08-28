<template>
  <div class="card h-100 shadow-sm" :class="{ 'disabled-chat': disabled }">
    <div class="card-header bg-light">
      <h5 class="mb-0">{{ title }}</h5>
    </div>
    <div class="card-body d-flex flex-column" style="height: 400px;">
      <div class="chat-messages flex-grow-1" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message mb-2"
          :class="msg.from === 'user' ? 'user-message' : 'bot-message'"
        >
          <div class="message-bubble">{{ msg.text }}</div>
        </div>
      </div>
      <div class="input-group mt-3">
        <input
          type="text"
          class="form-control"
          placeholder="输入消息..."
          v-model="newMessage"
          @keyup.enter="sendMessage"
          :disabled="disabled"
        />
        <button class="btn btn-outline-primary" @click="sendMessage" :disabled="disabled">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  title: String,
  messages: Array,
  disabled: Boolean,
});

const emit = defineEmits(['send']);

const newMessage = ref('');
const messagesContainer = ref(null);

const sendMessage = () => {
  if (newMessage.value.trim() && !props.disabled) {
    emit('send', newMessage.value.trim());
    newMessage.value = '';
  }
};

watch(
  () => props.messages,
  async () => {
    await nextTick();
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  },
  { deep: true }
);
</script>

<style scoped>
.chat-messages {
  overflow-y: auto;
  padding: 10px;
}

.message {
  display: flex;
  max-width: 80%;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 20px;
}

.bot-message {
  justify-content: flex-start;
}
.bot-message .message-bubble {
  background-color: #f1f0f0;
  color: #333;
}

.user-message {
  justify-content: flex-end;
  margin-left: auto;
}
.user-message .message-bubble {
  background-color: #007bff;
  color: white;
}

.disabled-chat {
  background-color: #f8f9fa;
  opacity: 0.7;
}
</style>