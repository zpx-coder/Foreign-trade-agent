import axios from "axios";
import { ElMessage } from "element-plus";
import { getErrorMessage } from "@/utils/errors";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 30000,
});

// ── 请求拦截器 ──
api.interceptors.request.use((config) => {
  // 用户端 token
  const userToken = localStorage.getItem("access_token");
  // 管理后台 token（如果当前在 /admin 路径下，优先使用 admin token）
  if (window.location.pathname.startsWith("/admin")) {
    const adminToken = localStorage.getItem("admin_access_token");
    if (adminToken) {
      config.headers.Authorization = `Bearer ${adminToken}`;
      return config;
    }
  }
  if (userToken) {
    config.headers.Authorization = `Bearer ${userToken}`;
  }
  return config;
});

// ── 响应拦截器 ──
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;
    const msg = getErrorMessage(error, "请求失败");
    const isAuthEndpoint = error.config?.url?.includes("/auth/");
    const hasUserToken = !!localStorage.getItem("access_token");
    const hasAdminToken = !!localStorage.getItem("admin_access_token");
    const isAdminPath = window.location.pathname.startsWith("/admin");

    // 登录/注册等认证接口：由页面自行处理错误展示，拦截器不弹 toast
    if (isAuthEndpoint) {
      return Promise.reject(error);
    }

    // 已登录用户的 401：token 过期，清除状态并跳转登录页
    if (status === 401) {
      if (isAdminPath && hasAdminToken) {
        localStorage.removeItem("admin_access_token");
        localStorage.removeItem("admin_refresh_token");
        localStorage.removeItem("admin_info");
        window.location.href = "/admin/login";
        return Promise.reject(error);
      }
      if (hasUserToken) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default api;
