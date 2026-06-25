import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";

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

// ── 用户端路由 (/app/*) ──
const appRoutes: RouteRecordRaw[] = [
  {
    path: "/app/dashboard",
    name: "Dashboard",
    component: () => import("@/views/dashboard/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/enterprise",
    name: "Enterprise",
    component: () => import("@/views/enterprise/EnterpriseEdit.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/products",
    name: "Products",
    component: () => import("@/views/product/ProductListView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/products/create",
    name: "ProductCreate",
    component: () => import("@/views/product/ProductCreate.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/products/:id/edit",
    name: "ProductEdit",
    component: () => import("@/views/product/ProductEdit.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/icps",
    name: "Icps",
    component: () => import("@/views/icp/IcpListView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/icps/create",
    name: "IcpCreate",
    component: () => import("@/views/icp/IcpCreate.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/icps/:id",
    name: "IcpDetail",
    component: () => import("@/views/icp/IcpDetail.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/customers",
    name: "Customers",
    component: () => import("@/views/customer/CustomerListView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/customers/:id",
    name: "CustomerDetail",
    component: () => import("@/views/customer/CustomerDetail.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/email/templates",
    name: "EmailTemplates",
    component: () => import("@/views/email/TemplateListView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/email/templates/create",
    name: "EmailTemplateCreate",
    component: () => import("@/views/email/TemplateCreate.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/email/templates/:id/edit",
    name: "EmailTemplateEdit",
    component: () => import("@/views/email/TemplateEdit.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/email/campaigns",
    name: "EmailCampaigns",
    component: () => import("@/views/email/CampaignListView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/email/campaigns/create",
    name: "EmailCampaignCreate",
    component: () => import("@/views/email/CampaignCreate.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/email/campaigns/:id",
    name: "EmailCampaignDetail",
    component: () => import("@/views/email/CampaignDetail.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/settings",
    name: "Settings",
    component: () => import("@/views/settings/SettingsView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/app/settings/members",
    name: "Members",
    component: () => import("@/views/settings/MemberListView.vue"),
    meta: { requiresAuth: true, roles: ["super_admin", "admin"] },
  },
];

// ── 管理后台路由 (/admin/*) ──
const adminRoutes: RouteRecordRaw[] = [
  {
    path: "/admin/dashboard",
    name: "AdminDashboard",
    component: () => import("@/views/admin/DashboardView.vue"),
    meta: { requiresAdmin: true },
  },
  {
    path: "/admin/tenants",
    name: "AdminTenants",
    component: () => import("@/views/admin/TenantListView.vue"),
    meta: { requiresAdmin: true },
  },
  {
    path: "/admin/tenants/:id",
    name: "AdminTenantDetail",
    component: () => import("@/views/admin/TenantDetailView.vue"),
    meta: { requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [...publicRoutes, ...appRoutes, ...adminRoutes],
});

// ── 全局路由守卫 ──
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

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
