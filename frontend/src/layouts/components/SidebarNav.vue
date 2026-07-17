<template>
  <div class="sidebar-nav">
    <!-- Logo -->
    <div class="logo" :class="{ collapsed }">
      <div class="logo-icon">
        <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="32" height="32" rx="8" fill="url(#lg)" />
          <path d="M9 22V10l7 6-7 6Z" fill="#fff" />
          <path d="M23 10v12l-7-6 7-6Z" fill="rgba(255,255,255,.7)" />
          <defs>
            <linearGradient id="lg" x1="0" y1="0" x2="32" y2="32">
              <stop stop-color="#3b82f6" />
              <stop offset="1" stop-color="#6366f1" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <transition name="fade">
        <span v-if="!collapsed" class="logo-text">AI 外贸助手</span>
      </transition>
    </div>

    <!-- 导航菜单 -->
    <el-menu
      :default-active="route.path"
      :collapse="collapsed"
      background-color="#0b1120"
      text-color="rgba(255,255,255,.55)"
      active-text-color="#fff"
      router
      class="nav-menu"
    >
      <template v-for="item in appNavItems" :key="item.path">
        <el-sub-menu v-if="item.children" :index="item.path">
          <template #title>
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </template>
          <el-menu-item v-for="child in item.children" :key="child.path" :index="child.path">
            {{ child.title }}
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </template>
    </el-menu>

    <!-- 底部版本 -->
    <div v-if="!collapsed" class="sidebar-footer">
      <span class="version">v0.1.0</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";

defineProps<{ collapsed: boolean }>();
const route = useRoute();

const appNavItems = [
  { path: "/app/dashboard", title: "工作台", icon: "Monitor" },
  { path: "/app/icps", title: "客户画像", icon: "PictureFilled" },
  { path: "/app/customers", title: "客户管理", icon: "UserFilled" },
  {
    path: "/email",
    title: "邮件营销",
    icon: "Message",
    children: [
      { path: "/app/email/templates", title: "邮件模板" },
      { path: "/app/email/campaigns", title: "发送任务" },
    ],
  },
  { path: "/app/enterprise", title: "企业资料", icon: "OfficeBuilding" },
  { path: "/app/products", title: "产品管理", icon: "Goods" },
  { path: "/app/settings", title: "系统设置", icon: "Setting" },
];
</script>

<style scoped lang="scss">
.sidebar-nav {
  display: flex;
  flex-direction: column;
  height: 100%;
}

// ── Logo ──
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);

  &.collapsed {
    justify-content: center;
    padding: 0;
  }
}
.logo-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 28px;
    height: 28px;
  }
}
.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

// ── 导航菜单 ──
.nav-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none !important;
  padding-top: 8px;

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
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
  }

  :deep(.el-menu-item.is-active) {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.35), rgba(99, 102, 241, 0.25)) !important;
    color: #fff !important;
    font-weight: 500;
  }

  :deep(.el-sub-menu .el-menu) {
    background: rgba(0, 0, 0, 0.15) !important;
    border-radius: 0 0 8px 8px;
    margin: 0 8px;

    .el-menu-item {
      padding-left: 52px !important;
      height: 38px;
      line-height: 38px;
      font-size: 13px;
    }
  }
}

// ── 底部 ──
.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.version {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
}

// ── 过渡 ──
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
