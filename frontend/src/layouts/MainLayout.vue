<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar">
      <SidebarNav :collapsed="isCollapsed" />
    </el-aside>
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
  background: #001529;
  transition: width 0.3s;
  overflow: hidden;
}
.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
.content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
