<template>
  <div class="dashboard-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-banner__content">
        <h1>你好，{{ authStore.user?.name || "用户" }}<span class="wave">👋</span></h1>
        <p>AI 外贸助手已就绪，助你高效开拓海外市场</p>
        <div class="welcome-banner__stats">
          <div class="welcome-stat">
            <span class="welcome-stat__num">{{ stats.total_customers || 0 }}</span>
            <span class="welcome-stat__label">获取客户</span>
          </div>
          <div class="welcome-stat">
            <span class="welcome-stat__num">{{ stats.total_icps || 0 }}</span>
            <span class="welcome-stat__label">客户画像</span>
          </div>
          <div class="welcome-stat">
            <span class="welcome-stat__num">{{ stats.total_emails_sent || 0 }}</span>
            <span class="welcome-stat__label">已发邮件</span>
          </div>
        </div>
      </div>
      <div class="welcome-banner__decor">
        <svg viewBox="0 0 240 140" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="200" cy="20" r="80" fill="rgba(255,255,255,.04)" />
          <circle cx="180" cy="50" r="50" fill="rgba(255,255,255,.05)" />
          <circle cx="210" cy="100" r="40" fill="rgba(255,255,255,.03)" />
        </svg>
      </div>
    </div>

    <!-- 设置进度 -->
    <el-card class="section-card setup-card">
      <div class="section-header">
        <h3 class="section-header__title">系统设置进度</h3>
        <span class="section-header__hint">完成以下步骤，解锁全部功能</span>
      </div>
      <el-steps :active="setupStep" finish-status="success" align-center class="setup-steps">
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
        <el-step title="邮件营销">
          <template #description>
            <span v-if="stats.total_emails_sent > 0" class="step-desc done">已发送 {{ stats.total_emails_sent }} 封邮件</span>
            <span v-else class="step-desc todo">创建邮件模板并发送</span>
          </template>
        </el-step>
      </el-steps>
    </el-card>

    <!-- 快捷入口 -->
    <h3 class="page-section-title">快速开始</h3>
    <div class="quick-grid">
      <div class="quick-card" @click="$router.push('/app/enterprise')">
        <div class="quick-card__icon" style="background: #eff6ff; color: #3b82f6;">
          <el-icon :size="22"><OfficeBuilding /></el-icon>
        </div>
        <div class="quick-card__body">
          <h4>企业资料 & 产品</h4>
          <p>完善公司信息与出口产品，AI 基于此生成精准画像</p>
        </div>
        <el-icon class="quick-card__arrow" :size="16"><ArrowRight /></el-icon>
      </div>
      <div class="quick-card" @click="$router.push('/app/icps')">
        <div class="quick-card__icon" style="background: #f0fdf6; color: #10b981;">
          <el-icon :size="22"><PictureFilled /></el-icon>
        </div>
        <div class="quick-card__body">
          <h4>客户画像<span class="badge-ai">AI</span></h4>
          <p>智能生成理想客户画像，锁定精准目标市场</p>
        </div>
        <el-icon class="quick-card__arrow" :size="16"><ArrowRight /></el-icon>
      </div>
      <div class="quick-card" @click="$router.push('/app/customers')">
        <div class="quick-card__icon" style="background: #fef3c7; color: #f59e0b;">
          <el-icon :size="22"><Search /></el-icon>
        </div>
        <div class="quick-card__body">
          <h4>客户搜索</h4>
          <p>多渠道路径搜索海外客户，AI 自动聚合与去重</p>
        </div>
        <el-icon class="quick-card__arrow" :size="16"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- ═══ 数据看板 ═══ -->
    <h3 class="page-section-title">数据看板</h3>

    <!-- KPI 指标卡 -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-icon kpi-icon--teal"><el-icon :size="18"><UserFilled /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.total_customers || 0 }}</span>
          <span class="kpi-lbl">获取客户</span>
          <span class="kpi-trend" v-if="stats.customers_reached">{{ stats.customers_reached }} 已触达</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon kpi-icon--lavender"><el-icon :size="18"><PictureFilled /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.completed_icps || 0 }}</span>
          <span class="kpi-lbl">客户画像</span>
          <span class="kpi-trend" v-if="stats.total_icps">共 {{ stats.total_icps }} 个</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon kpi-icon--rose"><el-icon :size="18"><Message /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.total_emails_sent || 0 }}</span>
          <span class="kpi-lbl">已发邮件</span>
          <span class="kpi-trend" v-if="stats.total_emails_sent">回复率 {{ (stats.reply_rate * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon kpi-icon--peach"><el-icon :size="18"><TrendCharts /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.total_customers ? (stats.reach_rate * 100).toFixed(0) + '%' : '—' }}</span>
          <span class="kpi-lbl">触达率</span>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="chart-row">
      <!-- 邮件发送趋势 — 渐变面积图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">邮件发送趋势</h3>
          <span class="chart-card__sub">近 30 天</span>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><i style="background:#2ec7c9;"></i>已发送</span>
          <span class="legend-item"><i style="background:#b6a2de;"></i>已打开</span>
          <span class="legend-item"><i style="background:#d87a80;"></i>已回复</span>
        </div>
        <div ref="emailChartRef" class="chart-body"></div>
      </div>

      <!-- 客户来源 — 环形图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">客户来源分布</h3>
        </div>
        <div ref="sourceChartRef" class="chart-body chart-body--donut"></div>
      </div>
    </div>

    <div class="chart-row">
      <!-- 画像状态 — 环形图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">画像状态分布</h3>
        </div>
        <div ref="icpChartRef" class="chart-body chart-body--donut"></div>
      </div>

      <!-- 邮件转化漏斗 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">邮件转化漏斗</h3>
        </div>
        <div ref="funnelChartRef" class="chart-body chart-body--funnel"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { OfficeBuilding, PictureFilled, Search, ArrowRight, UserFilled, TrendCharts, Message } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/api/client";
import * as echarts from "echarts/core";
import { LineChart, PieChart, FunnelChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([LineChart, PieChart, FunnelChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const authStore = useAuthStore();

// ── Macarons 主题 ──
const R = [
  '#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80',
  '#8d98b3', '#e5cf0d', '#97b552', '#95706d', '#dc69aa',
  '#07a2a4', '#9a7fd1', '#588dd5', '#f5994e', '#c05050',
  '#59678c', '#c9ab00', '#7eb00a', '#6f5553', '#c14089',
]

echarts.registerTheme('macarons', {
  color: R,
  title: { textStyle: { fontWeight: 'normal', color: '#008acd' } },
  visualMap: { itemWidth: 15, color: ['#5ab1ef', '#e0ffff'] },
  toolbox: { iconStyle: { borderColor: R[0] } },
  tooltip: { borderWidth: 0, backgroundColor: 'rgba(50,50,50,0.5)', textStyle: { color: '#FFF' }, axisPointer: { type: 'line', lineStyle: { color: '#008acd' }, crossStyle: { color: '#008acd' }, shadowStyle: { color: 'rgba(200,200,200,0.2)' } } },
  dataZoom: { dataBackgroundColor: '#efefff', fillerColor: 'rgba(182,162,222,0.2)', handleColor: '#008acd' },
  grid: { borderColor: '#eee' },
  categoryAxis: { axisLine: { lineStyle: { color: '#008acd' } }, splitLine: { lineStyle: { color: ['#eee'] } } },
  valueAxis: { axisLine: { lineStyle: { color: '#008acd' } }, splitArea: { show: true, areaStyle: { color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)'] } }, splitLine: { lineStyle: { color: ['#eee'] } } },
  line: { smooth: true, symbol: 'emptyCircle', symbolSize: 3 },
  candlestick: { itemStyle: { color: '#d87a80', color0: '#2ec7c9' }, lineStyle: { width: 1, color: '#d87a80', color0: '#2ec7c9' }, areaStyle: { color: '#2ec7c9', color0: '#b6a2de' } },
  graph: { itemStyle: { color: '#d87a80' }, linkStyle: { color: '#2ec7c9' } },
  gauge: { axisLine: { lineStyle: { color: [[0.2, '#2ec7c9'], [0.8, '#5ab1ef'], [1, '#d87a80']], width: 10 } }, axisTick: { splitNumber: 10, length: 15, lineStyle: { color: 'auto' } }, splitLine: { length: 22, lineStyle: { color: 'auto' } }, pointer: { width: 5 } },
})

// ── 基础状态 ──
const enterpriseDone = ref(false);
const setupStep = ref(1);

interface DashboardStats {
  total_icps: number; completed_icps: number; generating_icps: number;
  draft_icps: number; failed_icps: number; total_products: number;
  has_enterprise_profile: boolean; total_customers: number;
  customers_reached: number; reach_rate: number;
  customer_sources: Array<{ name: string; value: number }>;
  total_emails_sent: number; total_emails_opened: number;
  total_emails_replied: number; reply_rate: number;
  daily_email_stats: Array<{ day: string; sent: number; opened: number; replied: number }>;
}

const stats = ref<DashboardStats>({
  total_icps: 0, completed_icps: 0, generating_icps: 0, draft_icps: 0, failed_icps: 0,
  total_products: 0, has_enterprise_profile: false,
  total_customers: 0, customers_reached: 0, reach_rate: 0, customer_sources: [],
  total_emails_sent: 0, total_emails_opened: 0, total_emails_replied: 0, reply_rate: 0,
  daily_email_stats: [],
});

function updateStep() {
  let s = 1;
  if (enterpriseDone.value) s = 2;
  if (stats.value.completed_icps > 0) s = 3;
  if (stats.value.total_customers > 0) s = 4;
  if (stats.value.total_emails_sent > 0) s = 5;
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

// ── ECharts 实例 ──
const emailChartRef = ref<HTMLDivElement>();
const sourceChartRef = ref<HTMLDivElement>();
const icpChartRef = ref<HTMLDivElement>();
const funnelChartRef = ref<HTMLDivElement>();

let charts: echarts.ECharts[] = [];

const TEXT_DIM = "#8c8c8c";
const GRID_LINE = "#ececec";

function makeTooltip(): any {
  return {
    backgroundColor: "#fff",
    borderColor: "#e0e0e0",
    borderWidth: 1,
    textStyle: { color: "#333", fontSize: 12 },
    boxShadow: "0 8px 24px rgba(0,0,0,0.06)",
    extraCssText: "border-radius:10px;padding:10px 14px;",
  };
}

// ── 1. 渐变面积图（邮件趋势） ──
function renderEmailChart() {
  if (!emailChartRef.value) return;
  const c = echarts.init(emailChartRef.value, 'macarons');
  charts.push(c);
  const data = stats.value.daily_email_stats;
  const days = data.map(d => d.day.slice(5));
  const sent = data.map(d => d.sent);
  const opened = data.map(d => d.opened);
  const replied = data.map(d => d.replied);

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'axis' },
    legend: { show: false },
    grid: { left: 0, right: 6, top: 8, bottom: 0, containLabel: true },
    xAxis: {
      type: 'category', data: days,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: TEXT_DIM, fontSize: 10 },
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: GRID_LINE, type: 'dashed' } },
      axisLabel: { color: TEXT_DIM, fontSize: 10 },
    },
    series: [
      {
        name: '已发送', type: 'line', data: sent,
        smooth: true, symbol: 'none',
        lineStyle: { color: R[0], width: 2.5 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(46,199,201,0.15)' },
          { offset: 1, color: 'rgba(46,199,201,0.0)' },
        ])},
      },
      {
        name: '已打开', type: 'line', data: opened,
        smooth: true, symbol: 'none',
        lineStyle: { color: R[1], width: 2.5 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(182,162,222,0.18)' },
          { offset: 1, color: 'rgba(182,162,222,0.0)' },
        ])},
      },
      {
        name: '已回复', type: 'line', data: replied,
        smooth: true, symbol: 'none',
        lineStyle: { color: R[4], width: 2, type: 'dashed' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(216,122,128,0.12)' },
          { offset: 1, color: 'rgba(216,122,128,0.0)' },
        ])},
      },
    ],
  });
}

// ── 2. 环形图（客户来源） ──
function renderSourceChart() {
  if (!sourceChartRef.value) return;
  const c = echarts.init(sourceChartRef.value, 'macarons');
  charts.push(c);
  const data = stats.value.customer_sources;
  const total = data.length > 0 ? data.reduce((s: number, d: any) => s + d.value, 0) : 0;
  const seriesData = data.length > 0
    ? data.map(d => ({ ...d, itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 } }))
    : [{ value: 1, name: '暂无', itemStyle: { color: '#eee' }, tooltip: { show: false } }];

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    graphic: total > 0 ? [{
      type: 'text', left: 'center', top: 'center',
      style: { text: `${total}\n客户总数`, textAlign: 'center', fill: '#008acd', fontSize: 16, fontWeight: 700, lineHeight: 20 },
    }] : [],
    series: [{
      type: 'pie', radius: ['60%', '82%'], center: ['50%', '50%'],
      avoidLabelOverlap: false, label: { show: false },
      emphasis: { scaleSize: 6, label: { show: true, fontSize: 13, fontWeight: 'bold' } },
      data: seriesData,
    }],
  });
}

// ── 3. 环形图（画像状态） ──
function renderIcpChart() {
  if (!icpChartRef.value) return;
  const c = echarts.init(icpChartRef.value, 'macarons');
  charts.push(c);
  const s = stats.value;
  const total = s.total_icps || 0;
  const data = [
    { value: s.completed_icps || 0, name: '已完成' },
    { value: s.generating_icps || 0, name: '生成中' },
    { value: s.draft_icps || 0, name: '草稿' },
    { value: s.failed_icps || 0, name: '失败' },
  ];

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical', right: 10, top: 'center',
      icon: 'circle', itemWidth: 8, itemHeight: 8, itemGap: 12,
      textStyle: { color: '#555', fontSize: 12 },
    },
    graphic: total > 0 ? [{
      type: 'text', left: 'center', top: '42%',
      style: { text: `${total}\n画像总数`, textAlign: 'center', fill: '#008acd', fontSize: 15, fontWeight: 700, lineHeight: 20 },
    }] : [],
    series: [{
      type: 'pie',
      radius: ['50%', '72%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false, label: { show: false },
      emphasis: { scaleSize: 6, label: { show: true, fontSize: 13, fontWeight: 'bold' } },
      data: total > 0
        ? data.map((d, i) => {
            const cols: [string, string][] = [
              [R[7], R[17]], [R[3], R[13]], [R[5], R[15]], [R[4], R[14]],
            ]
            return {
              ...d,
              itemStyle: {
                borderRadius: 6, borderColor: '#fff', borderWidth: 3,
                color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                  { offset: 0, color: cols[i][0] }, { offset: 1, color: cols[i][1] },
                ]),
              },
            }
          })
        : [{ value: 1, name: '暂无', itemStyle: { color: '#eee' }, tooltip: { show: false } }],
    }],
  });
}

// ── 4. 漏斗图（邮件转化） ──
function renderFunnelChart() {
  if (!funnelChartRef.value) return;
  const c = echarts.init(funnelChartRef.value, 'macarons');
  charts.push(c);
  const s = stats.value;
  const sent = s.total_emails_sent || 0;
  const opened = s.total_emails_opened || 0;
  const replied = s.total_emails_replied || 0;

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'item', formatter: '{b}: {c}' },
    series: [{
      type: 'funnel',
      left: '15%', right: '15%', top: 60, bottom: 60,
      width: '70%',
      max: sent || 100, min: 0,
      sort: 'descending', gap: 4,
      funnelAlign: 'center',
      label: {
        show: true, position: 'inside',
        formatter: (p: any) => `${p.name}  ${p.value}`,
        fontSize: 13, fontWeight: 600, color: '#fff',
      },
      labelLine: { show: false },
      itemStyle: { borderColor: '#fff', borderWidth: 0 },
      emphasis: { label: { fontSize: 16 } },
      data: [
        { value: sent, name: '已发送', itemStyle: { borderRadius: [8, 8, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[0] }, { offset: 1, color: R[10] }]) } },
        { value: opened, name: '已打开', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[1] }, { offset: 1, color: R[11] }]) } },
        { value: replied, name: '已回复', itemStyle: { borderRadius: [0, 0, 8, 8], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[4] }, { offset: 1, color: R[14] }]) } },
      ],
    }],
  });
}

function renderAllCharts() {
  nextTick(() => {
    charts.forEach(c => c.dispose()); charts = [];
    renderEmailChart(); renderSourceChart(); renderIcpChart(); renderFunnelChart();
  });
}

function handleResize() { charts.forEach(c => c.resize()); }

onMounted(async () => {
  await Promise.all([loadStats(), loadEnterpriseStatus()]);
  renderAllCharts();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  charts.forEach(c => c.dispose());
});
</script>

<style scoped lang="scss">
// ── 欢迎横幅 ──
.welcome-banner {
  position: relative;
  background: linear-gradient(135deg, #0c1929 0%, #152238 30%, #1a3350 65%, #1d4ed8 100%);
  border-radius: 18px;
  padding: 36px 44px;
  margin-bottom: 28px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &__content {
    position: relative; z-index: 1;
    h1 { margin: 0 0 6px; font-size: 24px; font-weight: 700; color: #fff; letter-spacing: -0.3px; }
    .wave { display: inline-block; animation: wave 2s ease-in-out infinite; transform-origin: 70% 70%; }
    p { margin: 0 0 20px; font-size: 14px; color: rgba(255,255,255,.6); }
  }
  &__stats { display: flex; gap: 32px; }
  &__decor {
    position: absolute; right: 0; top: 0; bottom: 0; width: 240px; overflow: hidden; pointer-events: none;
    svg { width: 240px; height: 140px; position: absolute; top: -10px; right: -10px; }
  }
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  75% { transform: rotate(-8deg); }
}

.welcome-stat {
  display: flex; flex-direction: column; gap: 2px;
  &__num { font-size: 22px; font-weight: 800; color: #fff; }
  &__label { font-size: 12px; color: rgba(255,255,255,.5); }
}

// ── 通用区块标题 ──
.page-section-title { margin: 0 0 14px; font-size: 16px; font-weight: 700; color: #0f172a; letter-spacing: -.2px; }

// ── 步骤卡片 ──
.section-card {
  border-radius: 14px; border: 1px solid #e8ecf1; margin-bottom: 28px; box-shadow: 0 1px 3px rgba(0,0,0,.03);
  :deep(.el-card__body) { padding: 24px 32px 28px; }
}
.section-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 22px;
  &__title { margin: 0; font-size: 15px; font-weight: 700; color: #0f172a; }
  &__hint { font-size: 12px; color: #94a3b8; }
}
.setup-steps {
  :deep(.el-step__head.is-success) { color: #10b981; border-color: #10b981; }
  :deep(.el-step__head.is-process) { color: #3b82f6; border-color: #3b82f6; }
  :deep(.el-step__title) { font-size: 13px; font-weight: 600; }
  :deep(.el-step__description) { margin-top: 2px; }
  :deep(.el-step__line) { background: #e8ecf1; }
}
.step-desc { font-size: 11px; &.done { color: #10b981; } &.todo { color: #64748b; } }

// ── 快捷入口 ──
.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 32px; }
.quick-card {
  background: #fff; border: 1px solid #e8ecf1; border-radius: 14px;
  padding: 20px 22px; display: flex; align-items: center; gap: 16px;
  cursor: pointer; transition: all .2s; box-shadow: 0 1px 3px rgba(0,0,0,.03);
  &:hover { border-color: #3b82f6; box-shadow: 0 4px 16px rgba(59,130,246,.08); transform: translateY(-1px);
    .quick-card__arrow { opacity: 1; transform: translateX(0); }
  }
  &__icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  &__body {
    flex: 1; min-width: 0;
    h4 { margin: 0 0 3px; font-size: 14px; font-weight: 600; color: #1e293b; display: flex; align-items: center; gap: 8px; }
    p { margin: 0; font-size: 12px; color: #64748b; line-height: 1.4; }
  }
  &__arrow { color: #94a3b8; opacity: 0; transform: translateX(-6px); transition: all .2s; flex-shrink: 0; }
}
.badge-ai { display: inline-block; font-size: 10px; font-weight: 700; color: #fff; background: linear-gradient(135deg, #3b82f6, #6366f1); padding: 1px 6px; border-radius: 4px; }

// ── KPI 指标卡 ──
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
.kpi-card {
  background: #fff; border: 1px solid #e8ecf1; border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,.03); padding: 18px 20px;
  display: flex; align-items: center; gap: 14px;
  transition: all .2s;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,.05); transform: translateY(-1px); }
}
.kpi-icon {
  width: 42px; height: 42px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  &--teal     { background: #e6fafb; color: #2ec7c9; }
  &--lavender { background: #f4f1fb; color: #9a7fd1; }
  &--rose     { background: #fce8ec; color: #dc69aa; }
  &--peach    { background: #fff5ed; color: #ffb980; }
}
.kpi-body { flex: 1; display: flex; flex-direction: column; }
.kpi-val  { font-size: 24px; font-weight: 700; color: #0f172a; line-height: 1.2; letter-spacing: -.5px; }
.kpi-lbl  { font-size: 11px; color: #94a3b8; margin-bottom: 2px; }
.kpi-trend { font-size: 11px; color: #07a2a4; }

// ── 图表行 ──
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }

// ── 图表卡片 ──
.chart-card {
  background: #fff; border: 1px solid #e8ecf1; border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,.03); padding: 22px 24px 18px;
  transition: box-shadow .2s;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,.05); }
  &__head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 6px; }
  &__title { margin: 0; font-size: 14px; font-weight: 700; color: #0f172a; }
  &__sub  { font-size: 11px; color: #94a3b8; }
}
.chart-legend { display: flex; gap: 16px; margin-bottom: 4px; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #94a3b8;
  i { display: inline-block; width: 8px; height: 3px; border-radius: 2px; }
}
.chart-body { width: 100%; height: 240px; }
.chart-body--donut  { height: 280px; }
.chart-body--funnel { height: 320px; }
</style>
