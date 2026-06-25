<template>
  <div class="auth-layout">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">AI 外贸助手</h1>
        <p class="auth-subtitle">{{ subtitle }}</p>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ subtitle: string }>();
</script>

<style scoped lang="scss">
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e6fff 0%, #6366f1 100%);
}
.auth-card {
  width: 420px;
  max-width: 90vw;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.auth-header {
  text-align: center;
  margin-bottom: 32px;
}
.auth-title {
  font-size: 24px;
  color: #1e6fff;
  margin-bottom: 8px;
}
.auth-subtitle {
  font-size: 14px;
  color: #909399;
}
</style>
