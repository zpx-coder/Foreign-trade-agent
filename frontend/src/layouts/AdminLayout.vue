<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="232px" class="sidebar">
      <!-- Logo -->
      <div class="logo-area">
        <div class="logo-icon">
          <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="36" height="36" rx="8" fill="url(#admllg)" />
            <circle cx="18" cy="18" r="9.5" stroke="rgba(255,255,255,.28)" stroke-width="1" stroke-dasharray="3 2.5" />
            <circle cx="18" cy="18" r="5.5" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.4" />
            <ellipse cx="18" cy="18" rx="5.5" ry="2.8" stroke="rgba(255,255,255,.35)" stroke-width="0.8" transform="rotate(-20 18 18)" />
            <circle cx="18" cy="13" r="2" fill="#fff" opacity=".9" />
            <circle cx="18" cy="13" r="4.5" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="0.6" />
            <line x1="15" y1="15" x2="17" y2="16.8" stroke="#fff" stroke-width="1" stroke-linecap="round" opacity=".55" />
            <line x1="21" y1="15" x2="19" y2="16.8" stroke="#fff" stroke-width="1" stroke-linecap="round" opacity=".55" />
            <defs>
              <linearGradient id="admllg" x1="0" y1="0" x2="36" y2="36">
                <stop stop-color="#6366f1" />
                <stop offset="1" stop-color="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="logo-brand">
          <span class="logo-name">管理后台</span>
          <span class="logo-tag">平台运营</span>
        </div>
      </div>

      <!-- 导航 -->
      <nav class="nav-section">
        <router-link
          to="/admin/dashboard"
          class="nav-item"
          :class="{ 'nav-item--active': route.path === '/admin/dashboard' }"
        >
          <div class="nav-item__inner">
            <el-icon :size="18"><DataAnalysis /></el-icon>
            <span class="nav-item__text">运营仪表盘</span>
          </div>
        </router-link>
        <router-link
          to="/admin/tenants"
          class="nav-item"
          :class="{ 'nav-item--active': route.path.startsWith('/admin/tenants') }"
        >
          <div class="nav-item__inner">
            <el-icon :size="18"><OfficeBuilding /></el-icon>
            <span class="nav-item__text">租户管理</span>
          </div>
        </router-link>
      </nav>

      <!-- 底部 -->
      <div class="sidebar-footer">
        <div class="footer-user">
          <el-avatar :size="30" class="footer-avatar">
            {{ (authStore.admin?.name || "A")[0] }}
          </el-avatar>
          <div class="footer-info">
            <span class="footer-name">{{ authStore.admin?.name || "管理员" }}</span>
            <span class="footer-role">超级管理员</span>
          </div>
        </div>
      </div>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container>
      <el-header class="header" height="56px">
        <span class="header-title">平台管理后台</span>
        <div class="spacer" />
        <el-dropdown trigger="click" placement="bottom-end">
          <div class="user-trigger">
            <el-avatar :size="32" class="user-avatar">
              {{ (authStore.admin?.name || "A")[0] }}
            </el-avatar>
            <div class="user-meta">
              <span class="user-name">{{ authStore.admin?.name || "管理员" }}</span>
            </div>
            <el-icon :size="14" class="user-arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-item @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { ArrowDown, SwitchButton } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.adminLogout();
  router.push("/admin/login");
}
</script>

<style scoped lang="scss">
.admin-layout {
  height: 100vh;
}

// ── 侧边栏 ──
.sidebar {
  background: #0b1a2e;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, .06);
}

.logo-icon {
  width: 34px; height: 34px;
  flex-shrink: 0;
  svg { width: 34px; height: 34px; }
}

.logo-brand {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-name {
  font-size: 15px; font-weight: 700;
  color: #fff;
  letter-spacing: .5px;
  line-height: 1.2;
}

.logo-tag {
  font-size: 11px;
  color: rgba(255, 255, 255, .35);
}

// ── 导航 ──
.nav-section {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  height: 42px;
  padding: 0 12px;
  margin: 2px 0;
  border-radius: 8px;
  color: rgba(255, 255, 255, .55);
  text-decoration: none;
  cursor: pointer;
  transition: all .15s ease;
  border-left: 3px solid transparent;

  &__inner {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  &__text {
    font-size: 13.5px;
    white-space: nowrap;
  }

  &:hover {
    background: rgba(255, 255, 255, .05);
    color: rgba(255, 255, 255, .8);
  }

  &--active {
    background: rgba(99, 102, 241, .15) !important;
    color: #fff !important;
    font-weight: 500;
    border-left-color: #818cf8;
  }
}

// ── 底部用户 ──
.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, .06);
  padding: 14px 16px;
}

.footer-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.footer-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.footer-name {
  font-size: 13px;
  color: rgba(255, 255, 255, .8);
  font-weight: 500;
}

.footer-role {
  font-size: 11px;
  color: rgba(255, 255, 255, .3);
}

// ── 头部 ──
.header {
  background: #fff;
  border-bottom: 1px solid #e8ecf1;
  display: flex;
  align-items: center;
  padding: 0 28px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .03);
  z-index: 10;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.spacer { flex: 1; }

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px 4px 4px;
  border-radius: 10px;
  transition: background .15s;

  &:hover { background: #f1f5f9; }
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: 13px;
  color: #1e293b;
  font-weight: 600;
}

.user-arrow {
  color: #94a3b8;
  flex-shrink: 0;
}

// ── 内容区 ──
.content {
  background: #f5f7fa;
  padding: 28px 32px;
  overflow-y: auto;
}
</style>
