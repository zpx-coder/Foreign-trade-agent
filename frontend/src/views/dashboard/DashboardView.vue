<template>
  <div class="dashboard-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-banner__content">
        <h1>你好，{{ authStore.user?.name || "用户" }}<span class="wave">👋</span></h1>
        <p>AI 外贸助手已就绪，助你高效开拓海外市场</p>
      </div>
      <div class="welcome-banner__decor">
        <svg viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="160" cy="20" r="60" fill="rgba(255,255,255,.06)" />
          <circle cx="140" cy="40" r="40" fill="rgba(255,255,255,.08)" />
          <circle cx="170" cy="90" r="30" fill="rgba(255,255,255,.05)" />
        </svg>
      </div>
    </div>

    <!-- 设置进度 — 页面上方显眼位置 -->
    <el-card class="setup-card">
      <div class="setup-header">
        <h3 class="setup-header__title">系统设置进度</h3>
        <span class="setup-header__hint">完成以下步骤，解锁全部功能</span>
      </div>
      <el-steps :active="setupStep" finish-status="success" align-center class="setup-steps">
        <el-step title="注册账号">
          <template #description><span class="step-desc">已完成</span></template>
        </el-step>
        <el-step title="企业资料 & 产品">
          <template #description>
            <span v-if="enterpriseDone" class="step-desc done">已完成</span>
            <span v-else class="step-desc todo">完善公司信息与产品</span>
          </template>
        </el-step>
        <el-step title="生成客户画像">
          <template #description>
            <span v-if="stats.completed_icps > 0" class="step-desc done">已完成 {{ stats.completed_icps }} 个画像</span>
            <span v-else class="step-desc todo">AI 智能分析目标客户</span>
          </template>
        </el-step>
        <el-step title="搜索客户">
          <template #description>
            <span v-if="stats.total_customers > 0" class="step-desc done">已完成 {{ stats.total_customers }} 个客户</span>
            <span v-else class="step-desc todo">搜索目标客户</span>
          </template>
        </el-step>
      </el-steps>
    </el-card>

    <!-- 快捷入口 -->
    <h3 class="section-title">快速开始</h3>
    <div class="quick-grid">
      <el-card class="quick-card" shadow="hover" @click="$router.push('/app/enterprise')">
        <div class="quick-card__icon" style="background: #eff6ff; color: #3b82f6;">
          <el-icon :size="24"><OfficeBuilding /></el-icon>
        </div>
        <div class="quick-card__body">
          <h4>企业资料 & 产品</h4>
          <p>完善公司信息与出口产品，AI 基于此生成精准画像</p>
        </div>
        <el-icon class="quick-card__arrow" :size="16"><ArrowRight /></el-icon>
      </el-card>
      <el-card class="quick-card" shadow="hover" @click="$router.push('/app/icps')">
        <div class="quick-card__icon" style="background: #f0fdf6; color: #10b981;">
          <el-icon :size="24"><PictureFilled /></el-icon>
        </div>
        <div class="quick-card__body">
          <h4>客户画像<span class="badge-ai">AI</span></h4>
          <p>智能生成理想客户画像，锁定精准目标市场</p>
        </div>
        <el-icon class="quick-card__arrow" :size="16"><ArrowRight /></el-icon>
      </el-card>
      <el-card class="quick-card" shadow="hover" @click="$router.push('/app/customers')">
        <div class="quick-card__icon" style="background: #f0fdf4; color: #10b981;">
          <el-icon :size="24"><Search /></el-icon>
        </div>
        <div class="quick-card__body">
          <h4>客户搜索</h4>
          <p>多渠道路径搜索海外客户，AI 自动聚合与去重</p>
        </div>
      </el-card>
    </div>

    <!-- ── 数据看板 ── -->
    <h3 class="section-title">数据看板</h3>

    <!-- 核心指标卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-card__icon" style="background: #eff6ff; color: #3b82f6;">
          <el-icon :size="20"><PictureFilled /></el-icon>
        </div>
        <div class="stat-card__body">
          <span class="stat-card__value">{{ stats.total_icps }}</span>
          <span class="stat-card__label">客户画像</span>
        </div>
        <div class="stat-card__sub">
          <span class="sub-done">{{ stats.completed_icps }} 已完成</span>
          <span v-if="stats.generating_icps" class="sub-progress">{{ stats.generating_icps }} 生成中</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon" style="background: #f0fdf6; color: #10b981;">
          <el-icon :size="20"><UserFilled /></el-icon>
        </div>
        <div class="stat-card__body">
          <span class="stat-card__value">{{ stats.total_customers || "—" }}</span>
          <span class="stat-card__label">获取客户</span>
        </div>
        <div class="stat-card__sub">
          <span class="sub-done">{{ stats.customers_reached || 0 }} 已触达</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon" style="background: #fff7ed; color: #f59e0b;">
          <el-icon :size="20"><TrendCharts /></el-icon>
        </div>
        <div class="stat-card__body">
          <span class="stat-card__value">{{ stats.total_customers ? (stats.reach_rate * 100).toFixed(0) + '%' : '—' }}</span>
          <span class="stat-card__label">客户触达率</span>
        </div>
        <div class="stat-card__sub">
          <span class="sub-muted">触达客户 / 总客户</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card__icon" style="background: #f5f0ff; color: #6366f1;">
          <el-icon :size="20"><Message /></el-icon>
        </div>
        <div class="stat-card__body">
          <span class="stat-card__value">{{ stats.total_emails_sent ? (stats.reply_rate * 100).toFixed(0) + '%' : '—' }}</span>
          <span class="stat-card__label">邮件回复率</span>
        </div>
        <div class="stat-card__sub">
          <span class="sub-muted">已回复 / 已发送</span>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="chart-grid">
      <!-- 邮件发送趋势 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">邮件发送趋势</span>
            <span class="chart-subtitle">近 6 个月</span>
          </div>
        </template>
        <div ref="emailChartRef" class="chart-body" />
      </el-card>

      <!-- 客户分布 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">客户来源分布</span>
          </div>
        </template>
        <div ref="sourceChartRef" class="chart-body" />
      </el-card>
    </div>

    <div class="chart-grid">
      <!-- 画像状态分布 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">画像状态分布</span>
          </div>
        </template>
        <div ref="icpChartRef" class="chart-body chart-body--sm" />
      </el-card>

      <!-- 邮件漏斗 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">邮件转化漏斗</span>
          </div>
        </template>
        <div ref="funnelChartRef" class="chart-body chart-body--sm" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue";
import { OfficeBuilding, PictureFilled, Search, ArrowRight, UserFilled, TrendCharts, Message } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/api/client";
import * as echarts from "echarts/core";
import { LineChart, BarChart, PieChart, FunnelChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([LineChart, BarChart, PieChart, FunnelChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer]);

const authStore = useAuthStore();

// ── 基础状态 ──
const enterpriseDone = ref(false);
const setupStep = ref(1);

interface DashboardStats {
  total_icps: number;
  completed_icps: number;
  generating_icps: number;
  draft_icps: number;
  failed_icps: number;
  total_products: number;
  has_enterprise_profile: boolean;
  total_customers: number;
  customers_reached: number;
  reach_rate: number;
  customer_sources: Array<{ name: string; value: number }>;
  total_emails_sent: number;
  total_emails_opened: number;
  total_emails_replied: number;
  reply_rate: number;
  monthly_email_stats: Array<{ month: string; sent: number; opened: number; replied: number }>;
}

const stats = ref<DashboardStats>({
  total_icps: 0,
  completed_icps: 0,
  generating_icps: 0,
  draft_icps: 0,
  failed_icps: 0,
  total_products: 0,
  has_enterprise_profile: false,
  total_customers: 0,
  customers_reached: 0,
  reach_rate: 0,
  customer_sources: [],
  total_emails_sent: 0,
  total_emails_opened: 0,
  total_emails_replied: 0,
  reply_rate: 0,
  monthly_email_stats: [],
});

function updateStep() {
  let s = 1;
  if (enterpriseDone.value) s = 2;
  if (stats.value.completed_icps > 0) s = 3;
  if (stats.value.total_customers > 0) s = 4;
  setupStep.value = s;
}

async function loadStats() {
  try {
    const { data } = await api.get("/dashboard/stats", { silent: true });
    stats.value = { ...stats.value, ...data };
  } catch { /* dashboard not critical */ }
  updateStep();
}

async function loadEnterpriseStatus() {
  try {
    await api.get("/enterprise", { silent: true });
    enterpriseDone.value = true;
  } catch { /* 404 — 尚未填写企业资料 */ }
  updateStep();
}

// ── ECharts 实例管理 ──
const emailChartRef = ref<HTMLDivElement>();
const sourceChartRef = ref<HTMLDivElement>();
const icpChartRef = ref<HTMLDivElement>();
const funnelChartRef = ref<HTMLDivElement>();

let emailChart: echarts.ECharts | null = null;
let sourceChart: echarts.ECharts | null = null;
let icpChart: echarts.ECharts | null = null;
let funnelChart: echarts.ECharts | null = null;

// 共用的暗色文字色
const TEXT_COLOR = "#64748b";
const TEXT_COLOR_DIM = "#94a3b8";
const BORDER_COLOR = "#f1f5f9";

function makeTooltip() {
  return {
    backgroundColor: "#fff",
    borderColor: "#e2e8f0",
    borderWidth: 1,
    textStyle: { color: "#1e293b", fontSize: 13 },
    boxShadow: "0 4px 16px rgba(0,0,0,0.06)",
  };
}

function renderEmailChart() {
  if (!emailChartRef.value) return;
  if (!emailChart) emailChart = echarts.init(emailChartRef.value);

  // 如果有真实数据用真实数据，否则用模拟趋势展示图表形态
  const realData = stats.value.monthly_email_stats;
  const months = realData.length > 0
    ? realData.map((d) => d.month)
    : ["1月", "2月", "3月", "4月", "5月", "6月"];
  const sent = realData.length > 0
    ? realData.map((d) => d.sent)
    : [0, 0, 0, 0, 0, 0];
  const opened = realData.length > 0
    ? realData.map((d) => d.opened)
    : [0, 0, 0, 0, 0, 0];
  const replied = realData.length > 0
    ? realData.map((d) => d.replied)
    : [0, 0, 0, 0, 0, 0];

  emailChart.setOption({
    tooltip: { ...makeTooltip(), trigger: "axis" },
    legend: {
      bottom: 0,
      textStyle: { color: TEXT_COLOR, fontSize: 12 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 20,
    },
    grid: { left: 0, right: 0, top: 8, bottom: 36, containLabel: true },
    xAxis: {
      type: "category",
      data: months,
      axisLine: { lineStyle: { color: BORDER_COLOR } },
      axisTick: { show: false },
      axisLabel: { color: TEXT_COLOR_DIM, fontSize: 11 },
    },
    yAxis: {
      type: "value",
      splitLine: { lineStyle: { color: BORDER_COLOR, type: "dashed" } },
      axisLabel: { color: TEXT_COLOR_DIM, fontSize: 11 },
    },
    series: [
      {
        name: "已发送",
        type: "bar",
        data: sent,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#93bbfd" },
            { offset: 1, color: "#dbeafe" },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: 24,
        emphasis: { itemStyle: { color: "#3b82f6" } },
      },
      {
        name: "已打开",
        type: "line",
        data: opened,
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: "#10b981", width: 2 },
        itemStyle: { color: "#10b981" },
      },
      {
        name: "已回复",
        type: "line",
        data: replied,
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        lineStyle: { color: "#6366f1", width: 2 },
        itemStyle: { color: "#6366f1" },
      },
    ],
  });
}

function renderSourceChart() {
  if (!sourceChartRef.value) return;
  if (!sourceChart) sourceChart = echarts.init(sourceChartRef.value);

  const realSources = stats.value.customer_sources;
  const data = realSources.length > 0
    ? realSources
    : [
        { name: "Google 搜索", value: 0 },
        { name: "LinkedIn", value: 0 },
        { name: "展会名录", value: 0 },
        { name: "B2B 平台", value: 0 },
        { name: "其他渠道", value: 0 },
      ];

  // 如果全是 0，显示一个完整空心环提示暂无数据
  const allZero = data.every((d) => d.value === 0);

  sourceChart.setOption({
    tooltip: { ...makeTooltip(), trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: {
      bottom: 0,
      textStyle: { color: TEXT_COLOR, fontSize: 12 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 16,
    },
    series: [
      {
        type: "pie",
        radius: allZero ? ["55%", "70%"] : ["45%", "70%"],
        center: ["50%", "45%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 4, borderColor: "#fff", borderWidth: 2 },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: "bold" },
          scaleSize: 8,
        },
        data: allZero
          ? [{ value: 1, name: "暂无数据", itemStyle: { color: "#e2e8f0" }, tooltip: { show: false }, label: { show: false }, emphasis: { scaleSize: 0 } }]
          : data.map((d, i) => ({
              ...d,
              itemStyle: { color: ["#3b82f6", "#10b981", "#f59e0b", "#6366f1", "#94a3b8"][i % 5] },
            })),
      },
    ],
  });
}

function renderIcpChart() {
  if (!icpChartRef.value) return;
  if (!icpChart) icpChart = echarts.init(icpChartRef.value);

  const s = stats.value;
  icpChart.setOption({
    tooltip: { ...makeTooltip(), trigger: "item" },
    series: [
      {
        type: "pie",
        radius: ["50%", "75%"],
        center: ["50%", "50%"],
        itemStyle: { borderRadius: 3, borderColor: "#fff", borderWidth: 2 },
        label: { show: false },
        emphasis: { scaleSize: 6 },
        data: [
          { value: s.completed_icps || 0, name: "已完成", itemStyle: { color: "#10b981" } },
          { value: s.generating_icps || 0, name: "生成中", itemStyle: { color: "#f59e0b" } },
          { value: s.draft_icps || 0, name: "草稿", itemStyle: { color: "#94a3b8" } },
          { value: s.failed_icps || 0, name: "失败", itemStyle: { color: "#ef4444" } },
        ],
      },
    ],
  });
}

function renderFunnelChart() {
  if (!funnelChartRef.value) return;
  if (!funnelChart) funnelChart = echarts.init(funnelChartRef.value);

  const s = stats.value;
  const sent = s.total_emails_sent || 0;
  const opened = s.total_emails_opened || 0;
  const replied = s.total_emails_replied || 0;

  funnelChart.setOption({
    tooltip: { ...makeTooltip(), trigger: "item", formatter: "{b}: {c}" },
    series: [
      {
        type: "bar",
        data: [
          { value: sent || (replied > 0 ? replied : 0), name: "已发送" },
          { value: opened || (replied > 0 ? Math.round(replied * 1.5) : 0), name: "已打开" },
          { value: replied, name: "已回复" },
        ],
        itemStyle: {
          color: (params: any) => ["#3b82f6", "#6366f1", "#10b981"][params.dataIndex],
          borderRadius: [4, 4, 0, 0],
          borderWidth: 0,
          barWidth: "50%",
        },
        label: {
          show: true,
          position: "inside",
          color: "#fff",
          fontWeight: 600,
          fontSize: 14,
          formatter: "{c}",
        },
      },
    ],
    grid: { left: 0, right: 0, top: 8, bottom: 4, containLabel: true },
    xAxis: {
      type: "value",
      show: false,
    },
    yAxis: {
      type: "category",
      data: ["已回复", "已打开", "已发送"],
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: "#475569", fontSize: 12, fontWeight: 500 },
    },
  });
}

function renderAllCharts() {
  nextTick(() => {
    renderEmailChart();
    renderSourceChart();
    renderIcpChart();
    renderFunnelChart();
  });
}

function handleResize() {
  emailChart?.resize();
  sourceChart?.resize();
  icpChart?.resize();
  funnelChart?.resize();
}

onMounted(async () => {
  await Promise.all([loadStats(), loadEnterpriseStatus()]);
  renderAllCharts();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  emailChart?.dispose();
  sourceChart?.dispose();
  icpChart?.dispose();
  funnelChart?.dispose();
});
</script>

<style scoped lang="scss">
// ── 欢迎横幅 ──
.welcome-banner {
  position: relative;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 30%, #1e3a5f 70%, #1d4ed8 100%);
  border-radius: 20px;
  padding: 40px 44px;
  margin-bottom: 32px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &__content {
    position: relative;
    z-index: 1;

    h1 {
      margin: 0 0 8px 0;
      font-size: 26px;
      font-weight: 700;
      color: #fff;
      letter-spacing: -0.3px;
    }
    .wave {
      display: inline-block;
      animation: wave 2s ease-in-out infinite;
      transform-origin: 70% 70%;
    }
    p {
      margin: 0;
      font-size: 15px;
      color: rgba(255, 255, 255, 0.7);
    }
  }

  &__decor {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 220px;
    overflow: hidden;
    pointer-events: none;

    svg {
      width: 200px;
      height: 120px;
      position: absolute;
      top: -10px;
      right: -20px;
    }
  }
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  75% { transform: rotate(-8deg); }
}

// ── 设置进度卡（页面上方） ──
.setup-card {
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  margin-bottom: 32px;
  background: linear-gradient(180deg, #fff 0%, #fafbfd 100%);

  :deep(.el-card__body) {
    padding: 28px 36px 32px;
  }
}

.setup-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;

  &__title {
    margin: 0;
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.2px;
  }
  &__hint {
    font-size: 13px;
    color: #94a3b8;
  }
}

.setup-steps {
  :deep(.el-step__head.is-success) {
    color: #10b981;
    border-color: #10b981;
  }
  :deep(.el-step__head.is-process) {
    color: #3b82f6;
    border-color: #3b82f6;
  }
  :deep(.el-step__title) {
    font-size: 14px;
    font-weight: 600;
  }
  :deep(.el-step__description) {
    margin-top: 4px;
  }
  :deep(.el-step__line) {
    background: #e2e8f0;
  }
}

.step-desc {
  font-size: 12px;
  font-weight: 400;

  &.done { color: #10b981; }
  &.todo { color: #64748b; }
  &.wait { color: #94a3b8; }
}

// ── 区块标题 ──
.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.2px;
}

// ── 快捷入口 ──
.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 36px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.quick-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  cursor: pointer;

  &:hover:not(.disabled) {
    border-color: #3b82f6;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
    transform: translateY(-1px);

    .quick-card__arrow { opacity: 1; transform: translateX(0); }
  }

  &.disabled {
    cursor: default;
    opacity: 0.55;
    background: #f8fafc;
  }

  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 22px 24px;
  }

  &__icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__body {
    flex: 1;
    min-width: 0;

    h4 {
      margin: 0 0 4px 0;
      font-size: 15px;
      font-weight: 600;
      color: #1e293b;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    p {
      margin: 0;
      font-size: 13px;
      color: #64748b;
      line-height: 1.5;
    }
  }

  &__arrow {
    color: #94a3b8;
    opacity: 0;
    transform: translateX(-6px);
    transition: all 0.2s;
    flex-shrink: 0;
  }
}

.badge-ai {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  padding: 1px 6px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

// ── 核心指标卡片 ──
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;

  @media (max-width: 1024px) { grid-template-columns: repeat(2, 1fr); }
  @media (max-width: 640px) { grid-template-columns: 1fr; }
}

.stat-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 20px 24px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  }

  &__icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__body {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  &__value {
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.5px;
    font-family: "Inter", sans-serif;
  }

  &__label {
    font-size: 13px;
    color: #64748b;
    margin-top: 2px;
  }

  &__sub {
    width: 100%;
    margin-top: 4px;
    display: flex;
    gap: 12px;
    font-size: 12px;

    .sub-done { color: #10b981; }
    .sub-progress { color: #f59e0b; }
    .sub-muted { color: #94a3b8; }
  }
}

// ── 图表区 ──
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;

  @media (max-width: 1024px) { grid-template-columns: 1fr; }
}

.chart-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;

  :deep(.el-card__header) {
    padding: 16px 24px 0 24px;
    border-bottom: none;
  }
  :deep(.el-card__body) {
    padding: 12px 20px 20px 20px;
  }
}

.chart-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.chart-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.chart-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.chart-body {
  width: 100%;
  height: 280px;

  &--sm {
    height: 240px;
  }
}
</style>
