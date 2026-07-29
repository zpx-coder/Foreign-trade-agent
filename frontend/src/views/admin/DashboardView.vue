<template>
  <div class="page-admin-dashboard">
    <div class="page-header">
      <h2>运营仪表盘</h2>
      <p class="page-desc">平台整体运营数据概览</p>
    </div>

    <!-- ── KPI 卡片行 1 ── -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-primary">
          <div class="kpi-value">{{ stats.total_tenants }}</div>
          <div class="kpi-label">总租户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-success">
          <div class="kpi-value">{{ stats.active_tenants }}</div>
          <div class="kpi-label">活跃租户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-warning">
          <div class="kpi-value">{{ stats.total_users }}</div>
          <div class="kpi-label">总用户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-info">
          <div class="kpi-value">{{ stats.total_icps }}</div>
          <div class="kpi-label">总 ICP 画像</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ── KPI 卡片行 2 ── -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-primary">
          <div class="kpi-value">{{ stats.total_customers }}</div>
          <div class="kpi-label">总客户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-success">
          <div class="kpi-value">{{ stats.customers_reached }}</div>
          <div class="kpi-label">已触达客户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-warning">
          <div class="kpi-value">{{ stats.total_emails_sent }}</div>
          <div class="kpi-label">已发邮件</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card kpi-info">
          <div class="kpi-value">{{ stats.total_emails_replied }}</div>
          <div class="kpi-label">已回复邮件</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ── 图表行：租户分布 ── -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="section-card">
          <template #header><span>租户套餐分布</span></template>
          <div ref="planChartRef" class="chart-box"></div>
          <el-empty v-if="!hasPlanData" description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="section-card">
          <template #header><span>租户状态分布</span></template>
          <div ref="statusChartRef" class="chart-box"></div>
          <el-empty v-if="!hasStatusData" description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- ── Top 榜单 ── -->
    <el-row :gutter="16" class="top-row">
      <el-col :span="12">
        <el-card shadow="never" class="section-card">
          <template #header><span>🏆 客户数 Top 5 租户</span></template>
          <el-table :data="stats.top_tenants_by_customers" stripe size="small">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="name" label="租户名称" min-width="140" />
            <el-table-column prop="value" label="客户数" width="100" align="right">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.value }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="stats.top_tenants_by_customers.length === 0" description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="section-card">
          <template #header><span>🏆 发邮件 Top 5 租户</span></template>
          <el-table :data="stats.top_tenants_by_emails" stripe size="small">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="name" label="租户名称" min-width="140" />
            <el-table-column prop="value" label="已发邮件" width="100" align="right">
              <template #default="{ row }">
                <el-tag type="warning" size="small">{{ row.value }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="stats.top_tenants_by_emails.length === 0" description="暂无数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- ── 最近入驻租户 ── -->
    <el-card shadow="never" class="section-card" style="margin-top:16px">
      <template #header>
        <div class="card-header">
          <span>最近入驻租户</span>
          <el-button text type="primary" @click="$router.push('/admin/tenants')">
            查看全部 →
          </el-button>
        </div>
      </template>
      <el-table v-if="recentTenants.length > 0" :data="recentTenants" v-loading="tableLoading" stripe>
        <el-table-column prop="name" label="租户名称" min-width="160" />
        <el-table-column prop="plan_type" label="套餐" width="100">
          <template #default="{ row }">
            <el-tag :type="planTag(row.plan_type)" size="small">{{ planLabel(row.plan_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statTag(row.status)" size="small">{{ statLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="80" />
        <el-table-column prop="icp_count" label="画像数" width="80" />
        <el-table-column prop="customer_count" label="客户数" width="80" />
        <el-table-column prop="email_sent_count" label="已发邮件" width="90" />
        <el-table-column prop="created_at" label="入驻时间" width="180">
          <template #default="{ row }">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="$router.push(`/admin/tenants/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else-if="!tableLoading" description="暂无租户数据" :image-size="60" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import * as echarts from "echarts";
import api from "@/api/client";

interface TopTenant {
  name: string;
  value: number;
}

interface AdminStats {
  total_tenants: number;
  active_tenants: number;
  total_users: number;
  total_icps: number;
  completed_icps: number;
  generating_icps: number;
  draft_icps: number;
  failed_icps: number;
  total_customers: number;
  customers_reached: number;
  reach_rate: number;
  total_emails_sent: number;
  total_emails_opened: number;
  total_emails_replied: number;
  open_rate: number;
  reply_rate: number;
  tenants_by_plan: Record<string, number>;
  tenants_by_status: Record<string, number>;
  top_tenants_by_customers: TopTenant[];
  top_tenants_by_emails: TopTenant[];
}

interface TenantRow {
  id: string;
  name: string;
  plan_type: string;
  status: string;
  user_count: number;
  icp_count: number;
  customer_count: number;
  email_sent_count: number;
  created_at: string;
}

const stats = ref<AdminStats>({
  total_tenants: 0, active_tenants: 0, total_users: 0,
  total_icps: 0, completed_icps: 0, generating_icps: 0, draft_icps: 0, failed_icps: 0,
  total_customers: 0, customers_reached: 0, reach_rate: 0,
  total_emails_sent: 0, total_emails_opened: 0, total_emails_replied: 0,
  open_rate: 0, reply_rate: 0,
  tenants_by_plan: {}, tenants_by_status: {},
  top_tenants_by_customers: [], top_tenants_by_emails: [],
});
const recentTenants = ref<TenantRow[]>([]);
const tableLoading = ref(false);

const planChartRef = ref<HTMLDivElement | null>(null);
const statusChartRef = ref<HTMLDivElement | null>(null);
let planChart: echarts.ECharts | null = null;
let statusChart: echarts.ECharts | null = null;

// ── 标签映射 ──
const planMap: Record<string, string> = { free: "免费版", pro: "专业版", enterprise: "企业版" };
const planTagMap: Record<string, string> = { free: "info", pro: "warning", enterprise: "success" };
const statMap: Record<string, string> = { active: "正常", suspended: "已停用", cancelled: "已注销" };
const statTagMap: Record<string, string> = { active: "success", suspended: "warning", cancelled: "danger" };
function planLabel(v: string) { return planMap[v] || v; }
function planTag(v: string) { return planTagMap[v] || "info"; }
function statLabel(v: string) { return statMap[v] || v; }
function statTag(v: string) { return statTagMap[v] || "info"; }
function fmt(d: string) { return d ? new Date(d).toLocaleDateString("zh-CN") : "-"; }

const hasPlanData = computed(() => Object.keys(stats.value.tenants_by_plan).length > 0);
const hasStatusData = computed(() => Object.keys(stats.value.tenants_by_status).length > 0);

// ── 环形图配置 ──
const DONUT_COLORS: Record<string, string> = {
  free: "#909399", pro: "#409eff", enterprise: "#67c23a",
  active: "#67c23a", suspended: "#e6a23c", cancelled: "#f56c6c",
};

function makeDonutOption(data: Record<string, number>) {
  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
    itemStyle: { color: DONUT_COLORS[name] || undefined },
  }));
  return {
    tooltip: { trigger: "item" as const, formatter: "{b}: {c} ({d}%)" },
    series: [{
      type: "pie",
      radius: ["50%", "75%"],
      center: ["50%", "55%"],
      avoidLabelOverlap: false,
      label: { show: true, formatter: "{b}\n{d}%" },
      data: chartData,
    }],
  };
}

function renderCharts() {
  if (planChartRef.value && hasPlanData.value) {
    planChart = echarts.init(planChartRef.value);
    planChart.setOption(makeDonutOption(stats.value.tenants_by_plan));
  }
  if (statusChartRef.value && hasStatusData.value) {
    statusChart = echarts.init(statusChartRef.value);
    statusChart.setOption(makeDonutOption(stats.value.tenants_by_status));
  }
}

function handleResize() {
  planChart?.resize();
  statusChart?.resize();
}

onMounted(async () => {
  // 并行加载 stats 和租户列表
  const [statsRes, tenantsRes] = await Promise.allSettled([
    api.get("/admin/stats"),
    api.get("/admin/tenants", { params: { page: 1, page_size: 10 } }),
  ]);
  if (statsRes.status === "fulfilled") {
    stats.value = statsRes.value.data;
  }
  if (tenantsRes.status === "fulfilled") {
    recentTenants.value = tenantsRes.value.data.items;
    tableLoading.value = false;
  }
  await nextTick();
  renderCharts();
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  planChart?.dispose();
  statusChart?.dispose();
  window.removeEventListener("resize", handleResize);
});
</script>

<style scoped>
.page-admin-dashboard { padding: 0; }
.page-header { margin-bottom: 24px; }
.page-header h2 { margin: 0 0 4px; font-size: 22px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 14px; }

/* KPI 卡片 */
.kpi-row { margin-bottom: 16px; }
.kpi-card { text-align: center; border-radius: 8px; }
.kpi-card.kpi-primary { border-left: 4px solid var(--el-color-primary); }
.kpi-card.kpi-success { border-left: 4px solid var(--el-color-success); }
.kpi-card.kpi-warning { border-left: 4px solid var(--el-color-warning); }
.kpi-card.kpi-info   { border-left: 4px solid var(--el-color-info); }
.kpi-value { font-size: 32px; font-weight: 700; color: var(--el-text-color-primary); }
.kpi-label { margin-top: 4px; font-size: 14px; color: var(--el-text-color-secondary); }

/* 图表 */
.chart-row { margin-bottom: 16px; }
.chart-box { width: 100%; height: 280px; }
.section-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

/* Top 榜单 */
.top-row { margin-bottom: 16px; }
</style>
