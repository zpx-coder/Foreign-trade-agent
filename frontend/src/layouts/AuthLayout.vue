<template>
  <div class="auth-layout">
    <!-- 左侧：品牌面板 -->
    <div class="auth-left">
      <div class="auth-left__bg">
        <div class="auth-left__grid" />
        <div class="auth-left__orb orb--top" />
        <div class="auth-left__orb orb--bottom" />
      </div>
      <div class="auth-left__content">
        <!-- Logo & 品牌 -->
        <div class="auth-brand">
          <div class="auth-logo">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="11" fill="url(#logoGrad)" />
              <circle cx="24" cy="24" r="13" stroke="rgba(255,255,255,.28)" stroke-width="1.2" stroke-dasharray="4 3" />
              <circle cx="24" cy="24" r="8" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.8" />
              <ellipse cx="24" cy="24" rx="8" ry="4" stroke="rgba(255,255,255,.35)" stroke-width="1" transform="rotate(-20 24 24)" />
              <circle cx="24" cy="17" r="2.5" fill="#fff" opacity=".9" />
              <circle cx="24" cy="17" r="6" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="0.8" />
              <line x1="20" y1="19.5" x2="22.5" y2="22" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity=".55" />
              <line x1="28" y1="19.5" x2="25.5" y2="22" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity=".55" />
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop stop-color="#2563eb" />
                  <stop offset="1" stop-color="#4f46e5" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="auth-brand__name">AI 外贸助手</h1>
          <p class="auth-brand__tagline">智能获客 · 高效管理 · 全球贸易</p>
        </div>

        <!-- 地球插画 -->
        <div class="globe-illustration">
          <svg viewBox="0 0 280 280" fill="none" xmlns="http://www.w3.org/2000/svg" class="globe-svg">
            <!-- 外圈轨道 -->
            <ellipse cx="140" cy="140" rx="120" ry="120" stroke="rgba(255,255,255,.08)" stroke-width="1" />
            <ellipse cx="140" cy="140" rx="90" ry="120" stroke="rgba(255,255,255,.06)" stroke-width="1" />
            <ellipse cx="140" cy="140" rx="120" ry="90" stroke="rgba(255,255,255,.06)" stroke-width="1" />
            <!-- 经纬线 -->
            <ellipse cx="140" cy="140" rx="100" ry="100" stroke="rgba(255,255,255,.12)" stroke-width="1.5" stroke-dasharray="8 6" />
            <ellipse cx="140" cy="140" rx="70" ry="100" stroke="rgba(255,255,255,.1)" stroke-width="1" stroke-dasharray="6 8" />
            <ellipse cx="140" cy="140" rx="100" ry="70" stroke="rgba(255,255,255,.1)" stroke-width="1" stroke-dasharray="6 8" />
            <!-- 赤道 -->
            <line x1="40" y1="140" x2="240" y2="140" stroke="rgba(255,255,255,.15)" stroke-width="1.5" stroke-dasharray="4 6" />
            <!-- 核心球体光晕 -->
            <circle cx="140" cy="140" r="45" fill="url(#globeGlow)" />
            <circle cx="140" cy="140" r="35" fill="rgba(96,165,250,.15)" stroke="rgba(255,255,255,.2)" stroke-width="1" />
            <!-- 节点 -->
            <circle cx="140" cy="105" r="3" fill="#60a5fa" opacity="0.8">
              <animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite" />
            </circle>
            <circle cx="170" cy="130" r="2.5" fill="#818cf8" opacity="0.7">
              <animate attributeName="opacity" values="0.7;0.3;0.7" dur="2.5s" repeatCount="indefinite" />
            </circle>
            <circle cx="110" cy="120" r="2" fill="#a78bfa" opacity="0.7">
              <animate attributeName="opacity" values="0.3;0.8;0.3" dur="3.5s" repeatCount="indefinite" />
            </circle>
            <circle cx="155" cy="165" r="2.5" fill="#60a5fa" opacity="0.6">
              <animate attributeName="opacity" values="0.6;0.2;0.6" dur="4s" repeatCount="indefinite" />
            </circle>
            <circle cx="125" cy="170" r="2" fill="#818cf8" opacity="0.8">
              <animate attributeName="opacity" values="0.8;0.3;0.8" dur="2.8s" repeatCount="indefinite" />
            </circle>
            <circle cx="160" cy="100" r="2" fill="#c084fc" opacity="0.5">
              <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3.2s" repeatCount="indefinite" />
            </circle>
            <!-- 连接线 -->
            <line x1="140" y1="105" x2="170" y2="130" stroke="rgba(255,255,255,.1)" stroke-width="0.8" />
            <line x1="170" y1="130" x2="155" y2="165" stroke="rgba(255,255,255,.08)" stroke-width="0.8" />
            <line x1="110" y1="120" x2="140" y2="105" stroke="rgba(255,255,255,.08)" stroke-width="0.8" />
            <line x1="110" y1="120" x2="125" y2="170" stroke="rgba(255,255,255,.1)" stroke-width="0.8" />
            <defs>
              <radialGradient id="globeGlow" cx="0.5" cy="0.5" r="0.5">
                <stop stop-color="#60a5fa" stop-opacity="0.25" />
                <stop offset="1" stop-color="#60a5fa" stop-opacity="0" />
              </radialGradient>
            </defs>
          </svg>
        </div>

        <!-- 底部特性列表 -->
        <div class="auth-features">
          <div class="auth-feature">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.7)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <span>AI 智能获客</span>
          </div>
          <div class="auth-feature">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.7)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            <span>全球客户开发</span>
          </div>
          <div class="auth-feature">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.7)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <span>智能客户画像</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：表单面板 -->
    <div class="auth-right">
      <div class="auth-form-card">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ subtitle?: string }>();
</script>

<style scoped lang="scss">
.auth-layout {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
}

// ═══════════════════════════════════════════
// 左侧品牌面板
// ═══════════════════════════════════════════
.auth-left {
  position: relative;
  flex: 0 0 44%;
  background: linear-gradient(160deg, #0f172a 0%, #1e293b 40%, #1a1f3a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-width: 380px;

  &__bg {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }

  &__grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255, 255, 255, .025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, .025) 1px, transparent 1px);
    background-size: 50px 50px;
  }

  &__orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.15;
  }
  .orb--top {
    width: 350px;
    height: 350px;
    background: #3b82f6;
    top: -100px;
    right: -80px;
  }
  .orb--bottom {
    width: 300px;
    height: 300px;
    background: #6366f1;
    bottom: -80px;
    left: -60px;
  }

  &__content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 40px;
    max-width: 440px;
    width: 100%;
  }
}

// 品牌标识
.auth-brand {
  text-align: center;
  margin-bottom: 40px;

  &__name {
    font-size: 28px;
    font-weight: 700;
    color: #fff;
    margin: 16px 0 8px;
    letter-spacing: 1px;
  }

  &__tagline {
    font-size: 14px;
    color: rgba(255, 255, 255, .55);
    margin: 0;
    letter-spacing: 0.5px;
  }
}

.auth-logo {
  width: 56px;
  height: 56px;
  margin: 0 auto;

  svg {
    width: 56px;
    height: 56px;
  }
}

// 地球插画
.globe-illustration {
  width: 240px;
  height: 240px;
  margin: 0 auto 40px;

  .globe-svg {
    width: 100%;
    height: 100%;
  }
}

// 特性列表
.auth-features {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.auth-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255, 255, 255, .7);
  font-size: 14px;
  letter-spacing: 0.3px;

  svg {
    flex-shrink: 0;
  }
}

// ═══════════════════════════════════════════
// 右侧表单面板
// ═══════════════════════════════════════════
.auth-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 40px;
}

.auth-form-card {
  width: 420px;
  max-width: 100%;
  background: #fff;
  border-radius: 16px;
  padding: 48px 44px 40px;
  box-shadow:
    0 4px 24px rgba(0, 0, 0, .06),
    0 1px 4px rgba(0, 0, 0, .04);

  // 让 slot 内的表单元素继承卡片样式
  :deep(.auth-tabs) {
    display: flex;
    gap: 32px;
    margin-bottom: 32px;
    border-bottom: 1px solid #e8ecf1;
    padding-bottom: 14px;

    .auth-tab {
      font-size: 16px;
      font-weight: 500;
      color: #94a3b8;
      cursor: pointer;
      padding-bottom: 14px;
      margin-bottom: -15px;
      border-bottom: 2px solid transparent;
      transition: all .2s;
      background: none;
      border-top: none;
      border-left: none;
      border-right: none;

      &:hover { color: #475569; }

      &--active {
        color: #1e293b;
        border-bottom-color: #3b82f6;
      }
    }
  }

  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-input__wrapper) {
    border-radius: 10px;
    box-shadow: 0 0 0 1px #e2e8f0 inset;
    padding: 4px 14px;
    transition: box-shadow .2s;

    &:hover {
      box-shadow: 0 0 0 1px #cbd5e1 inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 2px rgba(59, 130, 246, .25) inset;
    }
  }

  :deep(.el-input__prefix) {
    color: #94a3b8;
  }

  // 按钮
  :deep(.auth-submit-btn) {
    width: 100%;
    height: 46px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 2px;
    border-radius: 10px;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    border: none;
    box-shadow: 0 4px 14px rgba(59, 130, 246, .35);
    transition: all .25s;

    &:hover {
      background: linear-gradient(135deg, #2563eb, #4f46e5);
      box-shadow: 0 6px 20px rgba(59, 130, 246, .45);
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(0);
    }
  }

  // 忘记密码
  :deep(.auth-forgot) {
    display: block;
    text-align: right;
    font-size: 13px;
    color: #64748b;
    margin-top: -10px;
    margin-bottom: 24px;

    &:hover { color: #3b82f6; }
  }

  // 底部链接
  :deep(.auth-footer) {
    text-align: center;
    font-size: 13px;
    color: #94a3b8;
    margin-top: 24px;

    a {
      color: #3b82f6;
      font-weight: 500;
      margin-left: 4px;

      &:hover { color: #2563eb; }
    }
  }

  // 第三方登录分隔线
  :deep(.auth-divider) {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 28px 0 20px;
    color: #c0c8d4;
    font-size: 12px;

    &::before,
    &::after {
      content: "";
      flex: 1;
      height: 1px;
      background: #e8ecf1;
    }
  }

  // 第三方登录图标
  :deep(.auth-social) {
    display: flex;
    justify-content: center;
    gap: 20px;

    .auth-social__icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all .2s;
      background: #fff;

      &:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, .15);
      }

      svg {
        width: 20px;
        height: 20px;
      }
    }
  }
}

// ═══════════════════════════════════════════
// 响应式
// ═══════════════════════════════════════════
@media (max-width: 768px) {
  .auth-layout {
    flex-direction: column;
  }

  .auth-left {
    flex: 0 0 auto;
    min-width: unset;
    padding: 40px 24px;

    &__content {
      padding: 20px 0;
      max-width: 100%;
    }
  }

  .globe-illustration {
    width: 160px;
    height: 160px;
    margin-bottom: 24px;
  }

  .auth-brand {
    margin-bottom: 24px;

    &__name { font-size: 22px; }
  }

  .auth-features {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
  }

  .auth-right {
    padding: 24px 16px 40px;
  }

  .auth-form-card {
    padding: 32px 24px 28px;
    border-radius: 12px;
  }
}
</style>
