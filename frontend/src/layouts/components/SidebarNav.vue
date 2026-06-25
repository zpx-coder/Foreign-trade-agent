<template>
  <div class="sidebar-nav">
    <div class="logo">{{ collapsed ? "AI" : "AI 外贸助手" }}</div>
    <el-menu
      :default-active="route.path"
      :collapse="collapsed"
      background-color="#001529"
      text-color="#ffffffb3"
      active-text-color="#fff"
      router
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
  { path: "/app/products", title: "产品管理", icon: "Goods" },
  { path: "/app/enterprise", title: "企业资料", icon: "OfficeBuilding" },
  { path: "/app/settings", title: "系统设置", icon: "Setting" },
];
</script>

<style scoped lang="scss">
.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.el-menu {
  border-right: none;
}
</style>
