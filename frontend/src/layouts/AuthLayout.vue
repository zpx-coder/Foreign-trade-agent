<template>
  <div class="auth-layout">
    <!-- 背景装饰 -->
    <div class="auth-bg">
      <div class="auth-bg__orb orb-1" />
      <div class="auth-bg__orb orb-2" />
      <div class="auth-bg__grid" />
    </div>

    <!-- 卡片 -->
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="40" rx="10" fill="url(#authlg)" />
            <path d="M11 27V13l9 7-9 7Z" fill="#fff" />
            <path d="M29 13v14l-9-7 9-7Z" fill="rgba(255,255,255,.7)" />
            <defs>
              <linearGradient id="authlg" x1="0" y1="0" x2="40" y2="40">
                <stop stop-color="#3b82f6" />
                <stop offset="1" stop-color="#6366f1" />
              </linearGradient>
            </defs>
          </svg>
        </div>
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
  position: relative;
  overflow: hidden;
  background: #0f172a;
}

// ── 背景装饰 ──
.auth-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;

  &__orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.3;
  }
  .orb-1 {
    width: 500px;
    height: 500px;
    background: #3b82f6;
    top: -150px;
    right: -100px;
  }
  .orb-2 {
    width: 400px;
    height: 400px;
    background: #6366f1;
    bottom: -120px;
    left: -80px;
  }

  &__grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
    background-size: 60px 60px;
  }
}

// ── 卡片 ──
.auth-card {
  position: relative;
  z-index: 1;
  width: 420px;
  max-width: 90vw;
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 48px 40px 40px;
  box-shadow:
    0 24px 80px rgba(0, 0, 0, 0.3),
    0 0 1px rgba(255, 255, 255, 0.2);
}

.auth-header {
  text-align: center;
  margin-bottom: 36px;
}

.auth-logo {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;

  svg {
    width: 48px;
    height: 48px;
  }
}

.auth-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.auth-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}
</style>
