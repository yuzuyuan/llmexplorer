<template>
  <div class="card h-100 shadow-sm chat-card">
    <div class="card-header bg-light">
      <h5 class="mb-0">{{ title }}</h5>
    </div>
    <div class="card-body d-flex flex-column chat-body">
      <div class="chat-messages flex-grow-1" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-row d-flex"
          :class="msg.from === 'user' ? 'user-message' : 'bot-message'"
        >
          <img v-if="msg.from === 'bot'" src="@/assets/images/bot-avatar.png" class="avatar" alt="bot">
          <div class="message-bubble">
            <div class="message-text">{{ msg.text }}</div>
          </div>
          <img v-if="msg.from === 'user'" src="@/assets/images/user-avatar.png" class="avatar" alt="user">
        </div>
      </div>
      <div class="input-group mt-3 chat-input-group">
        <input
          type="text"
          class="form-control"
          placeholder="输入消息..."
          v-model="newMessage"
          @keyup.enter="sendMessage"
          :disabled="disabled"
        />
        <button class="btn btn-primary" @click="sendMessage" :disabled="disabled">
          <i class="bi bi-send-fill"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// script部分保持不变
import { ref, watch, nextTick } from 'vue';
const props = defineProps({ title: String, messages: Array, disabled: Boolean });
const emit = defineEmits(['send']);
const newMessage = ref('');
const messagesContainer = ref(null);
const sendMessage = () => {
  if (newMessage.value.trim() && !props.disabled) {
    emit('send', newMessage.value.trim());
    newMessage.value = '';
  }
};
watch(() => props.messages, async () => {
    await nextTick();
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  }, { deep: true }
);
</script>

<style scoped>
.chat-card {
  border: none;
}

.chat-body {
  background-color: #f4f7f9;
  padding: 1rem;
}

.chat-messages {
  overflow-y: auto;
  padding: 0 10px;
}

.message-row {
  margin-bottom: 1.25rem;
  align-items: flex-end;
  gap: 10px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.message-bubble {
  padding: 12px 18px;
  border-radius: 18px;
  max-width: 80%;
  box-shadow: 0 2px 5px rgba(0,0,0,0.08);
  transition: all 0.2s ease-in-out;
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
}

/* Bot 消息样式 */
.bot-message {
  justify-content: flex-start;
}
.bot-message .message-bubble {
  background-color: #ffffff;
  color: #333;
  border-bottom-left-radius: 4px;
}

/* User 消息样式 */
.user-message {
  justify-content: flex-end;
  flex-direction: row-reverse;
}
.user-message .message-bubble {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-input-group .form-control {
  border-radius: 20px 0 0 20px;
  border-right: none;
  box-shadow: none;
}
.chat-input-group .btn {
  border-radius: 0 20px 20px 0;
  box-shadow: none;
}

/* 禁用状态 */
.disabled-chat {
  opacity: 0.7;
  pointer-events: none;
}
</style>