import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/api/client";

interface UserInfo {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
}

interface TenantInfo {
  id: string;
  name: string;
  plan_type: string;
  status: string;
}

interface AdminInfo {
  id: string;
  email: string;
  name: string;
  role: string;
}

export const useAuthStore = defineStore("auth", () => {
  // ── 用户端状态 ──
  const user = ref<UserInfo | null>(null);
  const tenant = ref<TenantInfo | null>(null);
  const permissions = ref<string[]>([]);

  // ── 管理后台状态 ──
  const admin = ref<AdminInfo | null>(null);

  // ── Token 管理 ──
  function setTokens(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  }
  function setAdminTokens(access: string, refresh: string) {
    localStorage.setItem("admin_access_token", access);
    localStorage.setItem("admin_refresh_token", refresh);
  }
  function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("admin_access_token");
    localStorage.removeItem("admin_refresh_token");
  }

  // ── Computed ──
  const isAuthenticated = computed(() => !!user.value);
  const isAdminAuthenticated = computed(() => !!admin.value);
  const userRole = computed(() => user.value?.role ?? "");
  const canManageMembers = computed(
    () => user.value?.role === "super_admin" || user.value?.role === "admin"
  );

  // ── 用户端登录 ──
  async function login(email: string, password: string) {
    const { data } = await api.post("/auth/login", { email, password });
    user.value = data.user;
    tenant.value = data.tenant;
    permissions.value = [];
    setTokens(data.token.access_token, data.token.refresh_token);
  }

  // ── 用户端注册 ──
  async function register(form: {
    name: string;
    company_name: string;
    email: string;
    password: string;
  }) {
    const { data } = await api.post("/auth/register", form);
    user.value = data.user;
    tenant.value = data.tenant;
    setTokens(data.token.access_token, data.token.refresh_token);
  }

  // ── 管理后台登录 ──
  async function adminLogin(email: string, password: string) {
    const { data } = await api.post("/auth/admin/login", { email, password });
    admin.value = data.admin;
    setAdminTokens(data.token.access_token, data.token.refresh_token);
  }

  // ── 获取当前用户 ──
  async function fetchMe() {
    try {
      const { data } = await api.get("/auth/me");
      user.value = data.user;
      tenant.value = data.tenant;
      permissions.value = data.permissions;
    } catch {
      logout();
    }
  }

  // ── 退出 ──
  function logout() {
    user.value = null;
    tenant.value = null;
    permissions.value = [];
    clearTokens();
  }
  function adminLogout() {
    admin.value = null;
    localStorage.removeItem("admin_access_token");
    localStorage.removeItem("admin_refresh_token");
  }

  return {
    user, tenant, permissions, admin,
    isAuthenticated, isAdminAuthenticated, userRole, canManageMembers,
    login, register, adminLogin, fetchMe, logout, adminLogout,
  };
});
