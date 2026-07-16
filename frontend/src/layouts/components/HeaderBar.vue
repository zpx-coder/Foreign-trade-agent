<template>
  <div class="header-bar">
    <button class="collapse-btn" @click="$emit('update:collapsed', !collapsed)" :title="collapsed ? '展开侧栏' : '收起侧栏'">
      <el-icon :size="18"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
    </button>

    <div class="spacer" />

    <el-dropdown trigger="click" placement="bottom-end">
      <div class="user-trigger">
        <el-avatar :size="32" class="user-avatar">
          {{ (authStore.user?.name || "U")[0] }}
        </el-avatar>
        <span class="user-name">{{ authStore.user?.name || "用户" }}</span>
        <el-icon class="arrow"><ArrowDown /></el-icon>
      </div>
      <template #dropdown>
        <el-dropdown-menu>
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
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

defineProps<{ collapsed: boolean }>();
defineEmits<{ "update:collapsed": [value: boolean] }>();

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<style scoped lang="scss">
.header-bar {
  width: 100%;
  display: flex;
  align-items: center;
  height: 100%;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all 0.15s;

  &:hover {
    background: #f1f5f9;
    color: #334155;
  }
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

  &:hover {
    background: #f1f5f9;
  }
}

.user-avatar {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
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
</style>
