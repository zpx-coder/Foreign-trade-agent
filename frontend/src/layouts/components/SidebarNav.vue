<template>
  <div class="sidebar-nav">
    <!-- Logo 区域 -->
    <div class="logo-area" :class="{ collapsed }">
      <div class="logo-icon">
        <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="36" height="36" rx="8" fill="url(#slogo)" />
          <circle cx="18" cy="18" r="9.5" stroke="rgba(255,255,255,.28)" stroke-width="1" stroke-dasharray="3 2.5" />
          <circle cx="18" cy="18" r="5.5" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.4" />
          <ellipse cx="18" cy="18" rx="5.5" ry="2.8" stroke="rgba(255,255,255,.35)" stroke-width="0.8" transform="rotate(-20 18 18)" />
          <circle cx="18" cy="13" r="2" fill="#fff" opacity=".9" />
          <circle cx="18" cy="13" r="4.5" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="0.6" />
          <line x1="15" y1="15" x2="17" y2="16.8" stroke="#fff" stroke-width="1" stroke-linecap="round" opacity=".55" />
          <line x1="21" y1="15" x2="19" y2="16.8" stroke="#fff" stroke-width="1" stroke-linecap="round" opacity=".55" />
          <defs>
            <linearGradient id="slogo" x1="0" y1="0" x2="36" y2="36">
              <stop stop-color="#2563eb" />
              <stop offset="1" stop-color="#4f46e5" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      <transition name="fade-text">
        <div v-if="!collapsed" class="logo-brand">
          <span class="logo-name">AI 外贸助手</span>
          <span class="logo-tag">智能获客平台</span>
        </div>
      </transition>
    </div>

    <!-- 导航菜单 -->
    <nav class="nav-section">
      <div v-for="item in appNavItems" :key="item.path" class="nav-item-wrapper">
        <!-- 分组标题 -->
        <div v-if="item.groupLabel && !collapsed" class="nav-group-label">{{ item.groupLabel }}</div>

        <!-- 带子菜单 -->
        <template v-if="item.children">
          <div
            class="nav-item nav-item--parent"
            :class="{ 'nav-item--expanded': expandedMenus[item.path] }"
            @click="toggleSubMenu(item.path)"
          >
            <div class="nav-item__inner">
              <el-icon :size="18"><component :is="item.icon" /></el-icon>
              <span v-if="!collapsed" class="nav-item__text">{{ item.title }}</span>
              <el-icon v-if="!collapsed" :size="12" class="nav-item__chevron" :class="{ rotated: expandedMenus[item.path] }">
                <ArrowDown />
              </el-icon>
            </div>
          </div>
          <div v-show="expandedMenus[item.path] && !collapsed" class="nav-submenu">
            <router-link
              v-for="child in item.children"
              :key="child.path"
              :to="child.path"
              class="nav-item nav-item--child"
              :class="{ 'nav-item--active': route.path === child.path }"
            >
              <span class="nav-item__text">{{ child.title }}</span>
            </router-link>
          </div>
        </template>

        <!-- 普通菜单项 -->
        <router-link
          v-else
          :to="item.path"
          class="nav-item"
          :class="{ 'nav-item--active': isActive(item) }"
        >
          <div class="nav-item__inner">
            <el-icon :size="18"><component :is="item.icon" /></el-icon>
            <span v-if="!collapsed" class="nav-item__text">{{ item.title }}</span>
          </div>
          <span v-if="!collapsed && item.badge" class="nav-item__badge">{{ item.badge }}</span>
        </router-link>
      </div>
    </nav>

    <!-- 底部用户区域 -->
    <div class="sidebar-footer" :class="{ collapsed }">
      <div class="footer-user">
        <el-avatar :size="collapsed ? 28 : 32" class="footer-avatar">
          {{ (authStore.user?.name || "U")[0] }}
        </el-avatar>
        <div v-if="!collapsed" class="footer-info">
          <span class="footer-name">{{ authStore.user?.name || "用户" }}</span>
          <span class="footer-role">{{ authStore.tenant?.name || "企业用户" }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRoute } from "vue-router";
import { ArrowDown } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

defineProps<{ collapsed: boolean }>();
const route = useRoute();
const authStore = useAuthStore();

const expandedMenus = reactive<Record<string, boolean>>({});

function toggleSubMenu(path: string) {
  expandedMenus[path] = !expandedMenus[path];
}

function isActive(item: any) {
  if (item.path === route.path) return true;
  // 子路由匹配（如 /app/customers 激活时 /app/customers/* 也算）
  if (route.path.startsWith(item.path + "/")) return true;
  return false;
}

interface NavItem {
  path: string;
  title: string;
  icon: string;
  groupLabel?: string;
  children?: { path: string; title: string }[];
  badge?: string;
}

const appNavItems: NavItem[] = [
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
  { path: "/app/analytics", title: "数据统计", icon: "TrendCharts" },
  { path: "/app/enterprise", title: "企业资料", icon: "OfficeBuilding" },
  { path: "/app/settings", title: "系统设置", icon: "Setting" },
];
</script>

<style scoped lang="scss">
.sidebar-nav {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #0b1a2e;
}

// ═══════════════════════════
// Logo
// ═══════════════════════════
.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, .06);

  &.collapsed {
    justify-content: center;
    padding: 20px 0;
  }
}

.logo-icon {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  svg { width: 34px; height: 34px; }
}

.logo-brand {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo-name {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: .5px;
  line-height: 1.2;
}

.logo-tag {
  font-size: 11px;
  color: rgba(255, 255, 255, .35);
  white-space: nowrap;
}

// ═══════════════════════════
// 导航
// ═══════════════════════════
.nav-section {
  flex: 1;
  overflow-y: auto;
  padding: 10px 10px 0;
}

.nav-group-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, .25);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 16px 12px 6px;
}

.nav-item-wrapper {
  margin-bottom: 2px;
}

// ── 菜单项 ──
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
  position: relative;
  border-left: 3px solid transparent;

  &__inner {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
  }

  &__text {
    font-size: 13.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__badge {
    font-size: 10px;
    font-weight: 600;
    background: #ef4444;
    color: #fff;
    padding: 1px 6px;
    border-radius: 10px;
    line-height: 16px;
    margin-left: auto;
  }

  &__chevron {
    color: rgba(255, 255, 255, .3);
    flex-shrink: 0;
    transition: transform .2s;
    &.rotated { transform: rotate(180deg); }
  }

  &:hover {
    background: rgba(255, 255, 255, .05);
    color: rgba(255, 255, 255, .8);
  }

  // 激活态：左侧蓝色指示条 + 蓝色背景
  &--active {
    background: rgba(59, 130, 246, .12) !important;
    color: #fff !important;
    font-weight: 500;
    border-left-color: #3b82f6;
  }

  // 父级菜单
  &--parent {
    .nav-item__text {
      font-weight: 500;
      flex: 1;
    }
  }

  // 子菜单
  &--child {
    height: 36px;
    padding-left: 52px;
    font-size: 13px;
    margin: 1px 0;
    border-radius: 6px;

    .nav-item__text {
      font-size: 13px;
      color: rgba(255, 255, 255, .45);
      transition: color .15s;
    }

    &:hover .nav-item__text {
      color: rgba(255, 255, 255, .75);
    }

    &.nav-item--active .nav-item__text {
      color: #fff;
    }
  }
}

.nav-submenu {
  overflow: hidden;
}

// ═══════════════════════════
// 底部用户
// ═══════════════════════════
.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, .06);
  padding: 14px 16px;

  &.collapsed {
    display: flex;
    justify-content: center;
    padding: 14px 0;
  }
}

.footer-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-avatar {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.footer-role {
  font-size: 11px;
  color: rgba(255, 255, 255, .3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// ═══════════════════════════
// 过渡
// ═══════════════════════════
.fade-text-enter-active,
.fade-text-leave-active {
  transition: opacity .15s;
}
.fade-text-enter-from,
.fade-text-leave-to {
  opacity: 0;
}
</style>
