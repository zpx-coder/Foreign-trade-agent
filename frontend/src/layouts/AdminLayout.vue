<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">管理后台</div>
      <el-menu :default-active="route.path" background-color="#001529" text-color="#ffffffb3" active-text-color="#fff" router>
        <el-menu-item index="/admin/dashboard"><el-icon><DataAnalysis /></el-icon><span>运营仪表盘</span></el-menu-item>
        <el-menu-item index="/admin/tenants"><el-icon><OfficeBuilding /></el-icon><span>租户管理</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header" height="56px">
        <span class="title">平台管理后台</span>
        <div class="spacer" />
        <el-dropdown trigger="click">
          <span class="user-info">{{ authStore.admin?.name || "管理员" }}<el-icon><ArrowDown /></el-icon></span>
          <template #dropdown>
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </template>
        </el-dropdown>
      </el-header>
      <el-main class="content"><router-view /></el-main>
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
.admin-layout { height: 100vh; }
.sidebar { background: #001529; }
.logo { height: 56px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: 700; border-bottom: 1px solid rgba(255,255,255,.1); }
.header { background: #fff; border-bottom: 1px solid #ebeef5; display: flex; align-items: center; padding: 0 20px; }
.content { background: #f5f7fa; padding: 20px; }
.spacer { flex: 1; }
.user-info { display: flex; align-items: center; gap: 4px; cursor: pointer; }
.el-menu { border-right: none; }
</style>
