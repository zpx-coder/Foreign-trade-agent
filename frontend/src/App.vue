<template>
  <div v-if="authStore.sessionRestored" class="app-root">
    <router-view />
  </div>
  <div v-else class="app-loading">
    <div class="loading-content">
      <svg class="loading-logo" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="48" height="48" rx="12" fill="url(#applg)" />
        <path d="M14 33V15l10 9-10 9Z" fill="#fff" />
        <path d="M34 15v18l-10-9 10-9Z" fill="rgba(255,255,255,.7)" />
        <defs>
          <linearGradient id="applg" x1="0" y1="0" x2="48" y2="48">
            <stop stop-color="#3b82f6" />
            <stop offset="1" stop-color="#6366f1" />
          </linearGradient>
        </defs>
      </svg>
      <p class="loading-text">AI 外贸助手</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
</script>

<style scoped>
.app-root {
  width: 100%;
  height: 100%;
}

.app-loading {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0b1120;
}

.loading-content {
  text-align: center;
}

.loading-logo {
  width: 48px;
  height: 48px;
  animation: logo-pulse 2s ease-in-out infinite;
}

.loading-text {
  margin-top: 16px;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 2px;
}

@keyframes logo-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
}
</style>
