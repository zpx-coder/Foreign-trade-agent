import axios from "axios";
import { ElMessage } from "element-plus";

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
    const msg = error.response?.data?.detail || error.message || "请求失败";
    const isAuthEndpoint = error.config?.url?.includes("/auth/");
    const hasExistingToken = !!localStorage.getItem("access_token");

    // 登录/注册等认证接口：由页面自行处理错误展示，拦截器不弹 toast
    if (isAuthEndpoint) {
      return Promise.reject(error);
    }

    // 已登录用户的 401：token 过期，路由守卫 fetchMe 会静默处理跳转
    if (status === 401 && hasExistingToken) {
      return Promise.reject(error);
    }

    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default api;
