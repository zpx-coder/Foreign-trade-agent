<template>
  <div class="header-bar">
    <el-icon class="collapse-btn" @click="$emit('update:collapsed', !collapsed)">
      <Fold v-if="!collapsed" />
      <Expand v-else />
    </el-icon>
    <div class="spacer" />
    <el-dropdown trigger="click">
      <span class="user-info">
        {{ authStore.user?.name || "用户" }}
        <el-icon><ArrowDown /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="$router.push('/app/settings')">系统设置</el-dropdown-item>
          <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
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
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}
.spacer {
  flex: 1;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #303133;
}
</style>
