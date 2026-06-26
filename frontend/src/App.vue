<template>
  <div v-if="appReady" class="app-root">
    <router-view />
  </div>
  <div v-else class="app-loading">
    <el-icon class="loading-icon" :size="32"><Loading /></el-icon>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Loading } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

const appReady = ref(false);

// 应用初始化：恢复登录态
(async () => {
  const authStore = useAuthStore();

  // 有用户 token → 尝试恢复用户端会话
  const userToken = localStorage.getItem("access_token");
  if (userToken) {
    try {
      await authStore.fetchMe();
    } catch {
      // token 无效，清除残留
      authStore.logout();
    }
  }

  // 有管理员 token → 仅标记（fetchMe 由路由守卫触发时再加载）
  // 管理后台路由守卫会检查 isAdminAuthenticated

  appReady.value = true;
})();
</script>

<style scoped>
.app-root {
  width: 100%;
  height: 100%;
}
.app-loading {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.loading-icon {
  color: #1e6fff;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
