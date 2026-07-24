<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '232px'" class="sidebar">
      <SidebarNav :collapsed="isCollapsed" />
    </el-aside>

    <!-- 右侧主体 -->
    <el-container>
      <el-header class="header" height="56px">
        <HeaderBar v-model:collapsed="isCollapsed" />
      </el-header>
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from "vue";
import SidebarNav from "./components/SidebarNav.vue";
import HeaderBar from "./components/HeaderBar.vue";

const isCollapsed = ref(false);
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
}

.sidebar {
  background: #0b1a2e;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
}

.header {
  background: #fff;
  border-bottom: 1px solid #e8ecf1;
  display: flex;
  align-items: center;
  padding: 0 28px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  z-index: 10;
}

.content {
  background: #f5f7fa;
  padding: 28px 32px;
  overflow-y: auto;

  @media (max-width: 768px) {
    padding: 20px 16px;
  }
}
</style>
