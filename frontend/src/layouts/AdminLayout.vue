<template>
  <el-container class="admin-layout">
    <el-aside width="232px" class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="url(#admlg)" />
            <path fill-rule="evenodd" clip-rule="evenodd" d="M16 8a4 4 0 0 0-4 4H8v14h16V12h-4a4 4 0 0 0-4-4Zm2 4a2 2 0 1 0-4 0h4ZM10 14h12v10H10V14Z" fill="#fff" />
            <defs>
              <linearGradient id="admlg" x1="0" y1="0" x2="32" y2="32">
                <stop stop-color="#6366f1" />
                <stop offset="1" stop-color="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="logo-text">管理后台</span>
      </div>

      <el-menu :default-active="route.path" background-color="#1e293b" text-color="rgba(255,255,255,.55)" active-text-color="#fff" router class="nav-menu">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon><span>运营仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/admin/tenants">
          <el-icon><OfficeBuilding /></el-icon><span>租户管理</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <span class="version">Admin v0.1.0</span>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header" height="56px">
        <span class="title">平台管理后台</span>
        <div class="spacer" />
        <el-dropdown trigger="click" placement="bottom-end">
          <div class="user-trigger">
            <el-avatar :size="32" class="user-avatar">
              {{ (authStore.admin?.name || "A")[0] }}
            </el-avatar>
            <span class="user-name">{{ authStore.admin?.name || "管理员" }}</span>
            <el-icon class="arrow"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
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
import { useAuthStore } from "@/stores/auth";
const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
function handleLogout() { authStore.adminLogout(); router.push("/admin/login"); }
</script>

<style scoped lang="scss">
.admin-layout {
  height: 100vh;
}

.sidebar {
  background: var(--sidebar-bg, #1e293b);
  display: flex;
  flex-direction: column;
  box-shadow: 1px 0 0 rgba(255, 255, 255, 0.04);
}

.logo {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.logo-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  svg { width: 28px; height: 28px; }
}
.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none !important;
  padding-top: 8px;

  :deep(.el-menu-item) {
    height: 44px;
    line-height: 44px;
    margin: 2px 8px;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.15s;

    &:hover {
      background: rgba(255, 255, 255, 0.06) !important;
      color: rgba(255, 255, 255, 0.85) !important;
    }

    &.is-active {
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.35), rgba(139, 92, 246, 0.25)) !important;
      color: #fff !important;
      font-weight: 500;
    }
  }
}

.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.version {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
}

.header {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.title {
  font-size: 15px;
  font-weight: 600;
  color: #334155;
}
.spacer {
  flex: 1;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px 4px 4px;
  border-radius: 8px;
  transition: background 0.15s;
  &:hover { background: #f1f5f9; }
}
.user-avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}
.user-name {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}
.arrow {
  font-size: 12px;
  color: #94a3b8;
}

.content {
  background: #f8fafc;
  padding: 24px 28px;
  overflow-y: auto;
}
</style>
