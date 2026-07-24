<template>
  <div class="header-bar">
    <!-- 左侧：折叠按钮 + 面包屑 -->
    <div class="header-left">
      <button
        class="collapse-btn"
        @click="$emit('update:collapsed', !collapsed)"
        :title="collapsed ? '展开侧栏' : '收起侧栏'"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="15" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <div class="breadcrumb">
        <el-icon :size="14" class="breadcrumb__sep"><ArrowRight /></el-icon>
        <span class="breadcrumb__current">{{ pageTitle }}</span>
      </div>
    </div>

    <!-- 右侧：操作区 -->
    <div class="header-right">
      <!-- 通知 -->
      <el-badge :value="3" :max="99" class="header-notify">
        <button class="icon-btn" title="通知">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        </button>
      </el-badge>

      <!-- 用户下拉 -->
      <el-dropdown trigger="click" placement="bottom-end">
        <div class="user-trigger">
          <el-avatar :size="32" class="user-avatar">
            {{ (authStore.user?.name || "U")[0] }}
          </el-avatar>
          <div class="user-meta">
            <span class="user-name">{{ authStore.user?.name || "用户" }}</span>
            <span class="user-tenant">{{ authStore.tenant?.name || "" }}</span>
          </div>
          <el-icon :size="14" class="user-arrow"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="$router.push('/app/enterprise')">
              <el-icon><OfficeBuilding /></el-icon>企业资料
            </el-dropdown-item>
            <el-dropdown-item @click="$router.push('/app/settings')">
              <el-icon><Setting /></el-icon>系统设置
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { ArrowDown, ArrowRight, OfficeBuilding, Setting, SwitchButton } from "@element-plus/icons-vue";

defineProps<{ collapsed: boolean }>();
defineEmits<{ "update:collapsed": [value: boolean] }>();

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const titleMap: Record<string, string> = {
  "/app/dashboard": "工作台",
  "/app/icps": "客户画像",
  "/app/customers": "客户管理",
  "/app/email/templates": "邮件模板",
  "/app/email/campaigns": "发送任务",
  "/app/enterprise": "企业资料",
  "/app/products": "产品管理",
  "/app/settings": "系统设置",
};

const pageTitle = computed(() => {
  // 先精确匹配
  if (titleMap[route.path]) return titleMap[route.path];
  // 再前缀匹配
  for (const [key, val] of Object.entries(titleMap)) {
    if (route.path.startsWith(key + "/")) return val;
  }
  return "";
});

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped lang="scss">
.header-bar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

// ── 左侧 ──
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.collapse-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all .15s;

  &:hover {
    background: #f1f5f9;
    color: #1e293b;
  }
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;

  &__sep {
    color: #c0c8d4;
  }

  &__current {
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
  }
}

// ── 右侧 ──
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all .15s;

  &:hover {
    background: #f1f5f9;
    color: #1e293b;
  }
}

.header-notify {
  :deep(.el-badge__content) {
    font-size: 10px;
    height: 16px;
    line-height: 16px;
    padding: 0 4px;
    right: 4px;
    top: 4px;
  }
}

// ── 用户 ──
.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px 4px 4px;
  border-radius: 10px;
  transition: background .15s;

  &:hover {
    background: #f1f5f9;
  }
}

.user-avatar {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
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

.user-tenant {
  font-size: 11px;
  color: #94a3b8;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-arrow {
  color: #94a3b8;
  flex-shrink: 0;
}
</style>
