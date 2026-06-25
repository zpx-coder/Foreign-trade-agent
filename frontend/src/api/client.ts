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
    const msg = error.response?.data?.detail || error.message || "请求失败";
    // 401 不弹窗（由路由守卫处理跳转）
    if (error.response?.status !== 401) {
      ElMessage.error(msg);
    }
    return Promise.reject(error);
  }
);

export default api;
