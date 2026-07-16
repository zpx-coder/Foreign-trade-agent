<template>
  <div class="page-admin-dashboard">
    <div class="page-header">
      <h2>运营仪表盘</h2>
      <p class="page-desc">平台整体运营数据概览</p>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.total_tenants }}</div>
          <div class="stat-label">总租户数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-active">
          <div class="stat-value">{{ stats.active_tenants }}</div>
          <div class="stat-label">活跃租户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-users">
          <div class="stat-value">{{ stats.total_users }}</div>
          <div class="stat-label">总用户数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-emails">
          <div class="stat-value">{{ stats.total_emails_sent }}</div>
          <div class="stat-label">已发邮件数</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>最近入驻租户</span>
          <el-button text type="primary" @click="$router.push('/admin/tenants')">
            查看全部 →
          </el-button>
        </div>
      </template>
      <el-empty v-if="!loading && recentTenants.length === 0" description="暂无租户数据" />
      <el-table v-else :data="recentTenants" v-loading="loading" stripe>
        <el-table-column prop="name" label="租户名称" min-width="180" />
        <el-table-column prop="plan_type" label="套餐" width="120">
          <template #default="{ row }">
            <el-tag :type="planTypeTag(row.plan_type)" size="small">{{ planTypeLabel(row.plan_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="80" />
        <el-table-column prop="created_at" label="入驻时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="$router.push(`/admin/tenants/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "@/api/client";

interface AdminStats {
  total_tenants: number;
  active_tenants: number;
  total_users: number;
  total_emails_sent: number;
}
interface TenantRow {
  id: string;
  name: string;
  plan_type: string;
  status: string;
  user_count: number;
  created_at: string;
}

const stats = ref<AdminStats>({ total_tenants: 0, active_tenants: 0, total_users: 0, total_emails_sent: 0 });
const recentTenants = ref<TenantRow[]>([]);
const loading = ref(false);

const planTypeMap: Record<string, string> = { free: "免费版", pro: "专业版", enterprise: "企业版" };
const planTagMap: Record<string, string> = { free: "info", pro: "warning", enterprise: "success" };
const statusMap: Record<string, string> = { active: "正常", suspended: "已停用", cancelled: "已注销" };
const statusTagMap: Record<string, string> = { active: "success", suspended: "warning", cancelled: "danger" };

function planTypeLabel(v: string) { return planTypeMap[v] || v; }
function planTypeTag(v: string) { return planTagMap[v] || "info"; }
function statusLabel(v: string) { return statusMap[v] || v; }
function statusTag(v: string) { return statusTagMap[v] || "info"; }
function formatDate(d: string) { return d ? new Date(d).toLocaleDateString("zh-CN") : "-"; }

onMounted(async () => {
  loading.value = true;
  try {
    const statsRes = await api.get("/admin/stats");
    stats.value = statsRes.data;
  } catch {
    // 统计加载失败时保留默认 0 值
  }
  try {
    const tenantsRes = await api.get("/admin/tenants", { params: { page: 1, page_size: 10 } });
    recentTenants.value = tenantsRes.data.items;
  } catch {
    // 列表加载失败保留空数组
  }
  loading.value = false;
});
</script>

<style scoped>
.page-admin-dashboard { padding: 0; }
.page-header { margin-bottom: 24px; }
.page-header h2 { margin: 0 0 4px; font-size: 22px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 14px; }
.stats-row { margin-bottom: 24px; }
.stat-card { text-align: center; border-left: 4px solid var(--el-color-primary); }
.stat-card.stat-active { border-left-color: var(--el-color-success); }
.stat-card.stat-users { border-left-color: var(--el-color-warning); }
.stat-card.stat-emails { border-left-color: var(--el-color-danger); }
.stat-value { font-size: 32px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-label { margin-top: 4px; font-size: 14px; color: var(--el-text-color-secondary); }
.section-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
