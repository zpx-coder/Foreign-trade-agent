import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

// 路由表 — Phase 1 开始逐步添加
const routes: RouteRecordRaw[] = [
  // 暂时空置，Phase 1 添加登录/注册/Dashboard
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
