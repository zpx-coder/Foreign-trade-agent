<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapsed ? '64px' : '232px'" class="sidebar">
      <SidebarNav :collapsed="isCollapsed" />
    </el-aside>
    <el-container>
      <el-header class="header" height="56px">
        <HeaderBar v-model:collapsed="isCollapsed" />
      </el-header>
      <el-main class="content">
        <div class="content-inner">
          <router-view />
        </div>
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
  background: #0b1120;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 1px 0 0 rgba(255, 255, 255, 0.04);
}
.header {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
.content {
  background: #f8fafc;
  padding: 24px 28px;
  overflow-y: auto;
}
.content-inner {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
