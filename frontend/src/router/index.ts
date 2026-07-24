import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import MainLayout from "@/layouts/MainLayout.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";

// ── 公开路由 ──
const publicRoutes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/app/dashboard",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/auth/LoginView.vue"),
    meta: { guest: true },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/auth/RegisterView.vue"),
    meta: { guest: true },
  },
  {
    path: "/admin/login",
    name: "AdminLogin",
    component: () => import("@/views/auth/AdminLoginView.vue"),
    meta: { guest: true },
  },
];

// ── 用户端路由 — 嵌套在 MainLayout 下 ──
const appRoutes: RouteRecordRaw = {
  path: "/app",
  component: MainLayout,
  meta: { requiresAuth: true },
  children: [
    { path: "", redirect: "/app/dashboard" },
    {
      path: "dashboard",
      name: "Dashboard",
      component: () => import("@/views/dashboard/DashboardView.vue"),
    },
    {
      path: "enterprise",
      name: "Enterprise",
      component: () => import("@/views/enterprise/EnterpriseEdit.vue"),
    },
    // v1.5: 产品管理已合并至企业资料，旧路由重定向
    {
      path: "products",
      redirect: "/app/enterprise",
    },
    {
      path: "products/create",
      redirect: "/app/enterprise",
    },
    {
      path: "products/:id/edit",
      redirect: "/app/enterprise",
    },
    {
      path: "icps",
      name: "Icps",
      component: () => import("@/views/icp/IcpListView.vue"),
    },
    {
      path: "icps/create",
      name: "IcpCreate",
      component: () => import("@/views/icp/IcpCreate.vue"),
    },
    {
      path: "icps/:id",
      name: "IcpDetail",
      component: () => import("@/views/icp/IcpDetail.vue"),
    },
    {
      path: "customers",
      name: "Customers",
      component: () => import("@/views/customer/CustomerListView.vue"),
    },
    {
      path: "customers/:id",
      name: "CustomerDetail",
      component: () => import("@/views/customer/CustomerDetail.vue"),
    },
    {
      path: "email/templates",
      name: "EmailTemplates",
      component: () => import("@/views/email/TemplateListView.vue"),
    },
    {
      path: "email/templates/create",
      redirect: "/app/email/templates",
    },
    {
      path: "email/templates/:id/edit",
      redirect: "/app/email/templates",
    },
    {
      path: "email/campaigns",
      name: "EmailCampaigns",
      component: () => import("@/views/email/CampaignListView.vue"),
    },
    {
      path: "email/campaigns/create",
      redirect: "/app/email/campaigns",
    },
    {
      path: "email/campaigns/:id",
      name: "EmailCampaignDetail",
      component: () => import("@/views/email/CampaignDetail.vue"),
    },
    {
      path: "settings",
      name: "Settings",
      component: () => import("@/views/settings/SettingsView.vue"),
    },
    {
      path: "settings/members",
      name: "Members",
      component: () => import("@/views/settings/MemberListView.vue"),
      meta: { roles: ["super_admin", "admin"] },
    },
  ],
};

// ── 管理后台路由 — 嵌套在 AdminLayout 下 ──
const adminRoutes: RouteRecordRaw = {
  path: "/admin",
  component: AdminLayout,
  meta: { requiresAdmin: true },
  children: [
    { path: "", redirect: "/admin/dashboard" },
    {
      path: "dashboard",
      name: "AdminDashboard",
      component: () => import("@/views/admin/DashboardView.vue"),
    },
    {
      path: "tenants",
      name: "AdminTenants",
      component: () => import("@/views/admin/TenantListView.vue"),
    },
    {
      path: "tenants/:id",
      name: "AdminTenantDetail",
      component: () => import("@/views/admin/TenantDetailView.vue"),
    },
  ],
};

// ── 404 路由 ──
const notFoundRoute: RouteRecordRaw = {
  path: "/:pathMatch(.*)*",
  name: "NotFound",
  component: () => import("@/views/NotFound.vue"),
};

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...publicRoutes, appRoutes, adminRoutes, notFoundRoute],
});

// ── 全局路由守卫 ──
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();

  // 先恢复会话（页面刷新后），消除与 App.vue 异步初始化的竞态
  if (!authStore.sessionRestored) {
    await authStore.restoreSession()
  }

  // 公开路由（登录/注册页）
  if (to.meta.guest) {
    if (to.path.startsWith("/admin") && authStore.isAdminAuthenticated) {
      return next("/admin/dashboard");
    }
    if (!to.path.startsWith("/admin") && authStore.isAuthenticated) {
      return next("/app/dashboard");
    }
    return next();
  }

  // 管理后台鉴权
  if (to.path.startsWith("/admin")) {
    if (!authStore.isAdminAuthenticated) return next("/admin/login");
    return next();
  }

  // 用户端鉴权
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next("/login");
  }

  // 角色权限检查
  if (to.meta.roles) {
    const requiredRoles = to.meta.roles as string[];
    if (!requiredRoles.includes(authStore.userRole)) {
      return next("/app/dashboard");
    }
  }

  next();
});

export default router;
