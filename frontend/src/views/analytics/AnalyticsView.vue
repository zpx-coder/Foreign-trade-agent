<template>
  <div class="analytics-page">
    <!-- 页面标题 -->
    <div class="page-hero">
      <div class="page-hero__icon">
        <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="2" width="36" height="36" rx="10" stroke="rgba(59,130,246,0.25)" stroke-width="1.5" stroke-dasharray="4 3"/>
          <circle cx="20" cy="20" r="8" stroke="rgba(59,130,246,0.4)" stroke-width="1.2"/>
          <circle cx="20" cy="20" r="2.5" fill="#3b82f6" opacity="0.8"/>
          <line x1="20" y1="12" x2="20" y2="2" stroke="rgba(59,130,246,0.18)" stroke-width="1"/>
          <line x1="28" y1="20" x2="38" y2="20" stroke="rgba(59,130,246,0.12)" stroke-width="1"/>
          <line x1="12" y1="20" x2="2" y2="20" stroke="rgba(59,130,246,0.12)" stroke-width="1"/>
          <line x1="20" y1="28" x2="20" y2="38" stroke="rgba(59,130,246,0.08)" stroke-width="1"/>
        </svg>
      </div>
      <div class="page-hero__text">
        <h1>数据统计</h1>
        <p>全链路数据可视化，AI 驱动外贸增长决策</p>
      </div>
    </div>

    <!-- ═══════════ 企业档案完整度 ═══════════ -->
    <section class="analytics-section" v-if="stats.enterprise_completion !== undefined">
      <div class="section-title">
        <span class="section-title__dot" style="background:#3b82f6;"></span>
        <h2>企业档案完整度</h2>
        <span class="section-title__line"></span>
      </div>
      <div class="ent-completion-card">
        <div class="ent-completion__overall">
          <div class="ent-completion__ring">
            <svg viewBox="0 0 100 100" class="ent-ring-svg">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#e8ecf1" stroke-width="8"/>
              <circle cx="50" cy="50" r="42" fill="none" stroke="url(#entGrad)" stroke-width="8"
                stroke-linecap="round" transform="rotate(-90 50 50)"
                :stroke-dasharray="Math.round(stats.enterprise_completion * 264) + ' 264'"/>
              <defs>
                <linearGradient id="entGrad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#3b82f6"/>
                  <stop offset="100%" stop-color="#6366f1"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="ent-ring-text">
              <span class="ent-ring-val">{{ Math.round((stats.enterprise_completion || 0) * 100) }}%</span>
            </div>
          </div>
        </div>
        <div class="ent-completion__detail">
          <div v-for="(det, key) in entSectionLabels" :key="key" class="ent-bar-row">
            <span class="ent-bar-label">{{ det.label }}</span>
            <div class="ent-bar-track">
              <div class="ent-bar-fill" :style="{ width: Math.round((det.rate || 0) * 100) + '%', background: det.color }"></div>
            </div>
            <span class="ent-bar-num">{{ det.filled || 0 }} / {{ det.total || 0 }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ 区块一：客户画像数据 ═══════════ -->
    <section class="analytics-section">
      <div class="section-title">
        <span class="section-title__dot" style="background:#2ec7c9;"></span>
        <h2>客户画像数据</h2>
        <span class="section-title__line"></span>
      </div>

      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#e6fafb;color:#2ec7c9;">
            <el-icon :size="18"><PictureFilled /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_icps || 0 }}</span>
            <span class="kpi-card__lbl">画像总数</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#ecfdf5;color:#10b981;">
            <el-icon :size="18"><CircleCheckFilled /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.completed_icps || 0 }}</span>
            <span class="kpi-card__lbl">已完成</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#fef3c7;color:#f59e0b;">
            <el-icon :size="18"><Loading /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.generating_icps || 0 }}</span>
            <span class="kpi-card__lbl">生成中</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#f1f5f9;color:#64748b;">
            <el-icon :size="18"><Document /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ (stats.draft_icps || 0) + (stats.failed_icps || 0) }}</span>
            <span class="kpi-card__lbl">草稿 / 失败</span>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__head">
            <h3>画像状态分布</h3>
            <span class="chart-card__badge">环形图</span>
          </div>
          <div ref="icpChartRef" class="chart-body chart-body--donut"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card__head">
            <h3>画像完成率</h3>
            <span class="chart-card__badge">进度</span>
          </div>
          <div class="chart-body chart-body--donut chart-body--center">
            <div class="big-stat">
              <span class="big-stat__num">{{ stats.total_icps ? Math.round(stats.completed_icps / stats.total_icps * 100) : 0 }}%</span>
              <span class="big-stat__sub">画像完成率</span>
              <span class="big-stat__hint">{{ stats.completed_icps }} / {{ stats.total_icps }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════ 区块二：客户数据 ═══════════ -->
    <section class="analytics-section">
      <div class="section-title">
        <span class="section-title__dot" style="background:#5ab1ef;"></span>
        <h2>客户数据</h2>
        <span class="section-title__line"></span>
      </div>

      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#eff6ff;color:#3b82f6;">
            <el-icon :size="18"><UserFilled /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_customers || 0 }}</span>
            <span class="kpi-card__lbl">客户总数</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#f4f1fb;color:#9a7fd1;">
            <el-icon :size="18"><Connection /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.customers_reached || 0 }}</span>
            <span class="kpi-card__lbl">已触达</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#ecfdf5;color:#10b981;">
            <el-icon :size="18"><TrendCharts /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_customers ? (stats.reach_rate * 100).toFixed(1) + '%' : '—' }}</span>
            <span class="kpi-card__lbl">触达率</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#fef3c7;color:#f59e0b;">
            <el-icon :size="18"><Share /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ (stats.customer_sources || []).length }}</span>
            <span class="kpi-card__lbl">来源渠道</span>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__head">
            <h3>客户来源分布</h3>
            <span class="chart-card__badge">环形图</span>
          </div>
          <div ref="sourceChartRef" class="chart-body chart-body--donut"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card__head">
            <h3>客户状态分布</h3>
            <span class="chart-card__badge">饼图</span>
          </div>
          <div ref="custStatusChartRef" class="chart-body chart-body--donut"></div>
        </div>
      </div>

      <div class="chart-row chart-row--full">
        <div class="chart-card chart-card--wide">
          <div class="chart-card__head">
            <h3>各画像客户分布</h3>
            <span class="chart-card__badge">柱状图</span>
          </div>
          <div ref="icpBarChartRef" class="chart-body chart-body--bar"></div>
        </div>
      </div>
    </section>

    <!-- ═══════════ 区块三：邮件数据 ═══════════ -->
    <section class="analytics-section">
      <div class="section-title">
        <span class="section-title__dot" style="background:#b6a2de;"></span>
        <h2>邮件数据</h2>
        <span class="section-title__line"></span>
      </div>

      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#eff6ff;color:#3b82f6;">
            <el-icon :size="18"><Message /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_emails_sent || 0 }}</span>
            <span class="kpi-card__lbl">已发送</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#e6fafb;color:#2ec7c9;">
            <el-icon :size="18"><View /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_emails_opened || 0 }}</span>
            <span class="kpi-card__lbl">已打开</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#f4f1fb;color:#9a7fd1;">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_emails_replied || 0 }}</span>
            <span class="kpi-card__lbl">已回复</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-card__icon" style="background:#fef3c7;color:#f59e0b;">
            <el-icon :size="18"><DataLine /></el-icon>
          </div>
          <div class="kpi-card__body">
            <span class="kpi-card__val">{{ stats.total_emails_sent ? (stats.reply_rate * 100).toFixed(0) + '%' : '—' }}</span>
            <span class="kpi-card__lbl">回复率</span>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__head">
            <h3>邮件发送趋势</h3>
            <span class="chart-card__badge">面积图 · 近 30 天</span>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><i style="background:#2ec7c9;"></i>已发送</span>
            <span class="legend-item"><i style="background:#b6a2de;"></i>已打开</span>
            <span class="legend-item"><i style="background:#d87a80;"></i>已回复</span>
          </div>
          <div ref="emailChartRef" class="chart-body chart-body--mail"></div>
        </div>
        <div class="chart-card">
          <div class="chart-card__head">
            <h3>邮件转化漏斗</h3>
            <span class="chart-card__badge">漏斗图</span>
          </div>
          <div ref="funnelChartRef" class="chart-body chart-body--mail"></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";
import {
  PictureFilled, CircleCheckFilled, Loading, Document,
  UserFilled, Connection, TrendCharts, Share,
  Message, View, ChatDotRound, DataLine,
} from "@element-plus/icons-vue";
import api from "@/api/client";
import * as echarts from "echarts/core";
import { LineChart, PieChart, FunnelChart, BarChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  LineChart, PieChart, FunnelChart, BarChart,
  GridComponent, TooltipComponent, LegendComponent, CanvasRenderer,
]);

// ── Macarons 浅色主题 ──
const R = [
  "#2ec7c9", "#b6a2de", "#5ab1ef", "#ffb980", "#d87a80",
  "#8d98b3", "#e5cf0d", "#97b552", "#95706d", "#dc69aa",
  "#07a2a4", "#9a7fd1", "#588dd5", "#f5994e", "#c05050",
  "#59678c", "#c9ab00", "#7eb00a", "#6f5553", "#c14089",
];

echarts.registerTheme("macarons", {
  color: R,
  title: { textStyle: { fontWeight: "normal", color: "#008acd" } },
  tooltip: {
    borderWidth: 0,
    backgroundColor: "rgba(50,50,50,0.5)",
    textStyle: { color: "#FFF" },
    axisPointer: {
      type: "line",
      lineStyle: { color: "#008acd" },
      crossStyle: { color: "#008acd" },
      shadowStyle: { color: "rgba(200,200,200,0.2)" },
    },
  },
  grid: { borderColor: "#eee" },
  categoryAxis: {
    axisLine: { lineStyle: { color: "#008acd" } },
    splitLine: { lineStyle: { color: ["#eee"] } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: "#008acd" } },
    splitArea: { show: true, areaStyle: { color: ["rgba(250,250,250,0.1)", "rgba(200,200,200,0.1)"] } },
    splitLine: { lineStyle: { color: ["#eee"] } },
  },
  line: { smooth: true, symbol: "emptyCircle", symbolSize: 3 },
});

// ── 数据 ──
interface EnterpriseSectionDetail {
  filled: number; total: number; rate: number;
}

interface DashboardStats {
  total_icps: number; completed_icps: number; generating_icps: number;
  draft_icps: number; failed_icps: number;
  total_customers: number; customers_reached: number; reach_rate: number;
  customer_sources: Array<{ name: string; value: number }>;
  customer_status_counts: Record<string, number>;
  customer_icp_stats: Array<{ icp_id: string | null; icp_name: string; total: number; statuses: Record<string, number> }>;
  total_emails_sent: number; total_emails_opened: number; total_emails_replied: number;
  open_rate: number; reply_rate: number;
  daily_email_stats: Array<{ day: string; sent: number; opened: number; replied: number }>;
  enterprise_completion?: number;
  enterprise_completion_detail?: Record<string, EnterpriseSectionDetail>;
}

const stats = ref<DashboardStats>({
  total_icps: 0, completed_icps: 0, generating_icps: 0, draft_icps: 0, failed_icps: 0,
  total_customers: 0, customers_reached: 0, reach_rate: 0, customer_sources: [],
  customer_status_counts: {}, customer_icp_stats: [],
  total_emails_sent: 0, total_emails_opened: 0, total_emails_replied: 0,
  open_rate: 0, reply_rate: 0, daily_email_stats: [],
});

// v1.6: 企业档案各区块的展示标签与颜色
const entSectionLabels = computed(() => {
  const detail = stats.value.enterprise_completion_detail || {};
  const config: Record<string, { label: string; color: string }> = {
    basic: { label: "基本信息", color: "#3b82f6" },
    trade: { label: "外贸实力", color: "#10b981" },
    contact: { label: "联系信息", color: "#f59e0b" },
    media: { label: "视觉素材", color: "#8b5cf6" },
  };
  return Object.fromEntries(
    Object.entries(config).map(([key, cfg]) => [
      key,
      { ...cfg, ...(detail[key] || { filled: 0, total: 0, rate: 0 }) },
    ])
  );
});

async function loadStats() {
  try {
    const { data } = await api.get("/dashboard/stats", { silent: true });
    stats.value = { ...stats.value, ...data };
  } catch { /* non-critical */ }
}

// ── ECharts refs ──
const icpChartRef = ref<HTMLDivElement>();
const sourceChartRef = ref<HTMLDivElement>();
const custStatusChartRef = ref<HTMLDivElement>();
const icpBarChartRef = ref<HTMLDivElement>();
const emailChartRef = ref<HTMLDivElement>();
const funnelChartRef = ref<HTMLDivElement>();

let charts: echarts.ECharts[] = [];
const GRID_LINE = "#ececec";
const TEXT_DIM = "#8c8c8c";

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

// ── 1. 画像状态环形图 ──
function renderIcpChart() {
  if (!icpChartRef.value) return;
  const c = echarts.init(icpChartRef.value, "macarons");
  charts.push(c);
  const s = stats.value;
  const total = s.total_icps || 0;
  const data = [
    { value: s.completed_icps || 0, name: "已完成" },
    { value: s.generating_icps || 0, name: "生成中" },
    { value: s.draft_icps || 0, name: "草稿" },
    { value: s.failed_icps || 0, name: "失败" },
  ];

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: "item", formatter: "{b}: {c} ({d}%)" },
    graphic: total > 0
      ? [{ type: "text", left: "center", top: "42%", style: { text: `${total}\n画像总数`, textAlign: "center", fill: "#008acd", fontSize: 15, fontWeight: 700, lineHeight: 20 } }]
      : [],
    series: [{
      type: "pie", radius: ["55%", "80%"], center: ["38%", "50%"],
      avoidLabelOverlap: false, label: { show: false },
      emphasis: { scaleSize: 6, label: { show: true, fontSize: 13, fontWeight: "bold" } },
      data: total > 0
        ? data.map((d, i) => {
            const cols: [string, string][] = [[R[7], R[17]], [R[3], R[13]], [R[5], R[15]], [R[4], R[14]]];
            return { ...d, itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 3,
              color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [{ offset: 0, color: cols[i][0] }, { offset: 1, color: cols[i][1] }]) } };
          })
        : [{ value: 1, name: "暂无数据", itemStyle: { color: "#eee" }, tooltip: { show: false }, label: { show: false } }],
    }],
    legend: { orient: "vertical", right: 8, top: "center", icon: "circle", itemWidth: 8, itemHeight: 8, itemGap: 12, textStyle: { color: "#555", fontSize: 12 } },
  });
}

// ── 2. 客户来源环形图 ──
function renderSourceChart() {
  if (!sourceChartRef.value) return;
  const c = echarts.init(sourceChartRef.value, "macarons");
  charts.push(c);
  const data = stats.value.customer_sources;
  const total = data.length > 0 ? data.reduce((s: number, d: any) => s + d.value, 0) : 0;

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: "item", formatter: "{b}: {c} ({d}%)" },
    graphic: total > 0
      ? [{ type: "text", left: "center", top: "center", style: { text: `${total}\n客户总数`, textAlign: "center", fill: "#008acd", fontSize: 16, fontWeight: 700, lineHeight: 20 } }]
      : [],
    series: [{
      type: "pie", radius: ["60%", "82%"], center: ["50%", "50%"],
      avoidLabelOverlap: false, label: { show: false },
      emphasis: { scaleSize: 6, label: { show: true, fontSize: 13, fontWeight: "bold" } },
      data: data.length > 0
        ? data.map((d, i) => ({ ...d, itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 3, color: R[i % R.length] } }))
        : [{ value: 1, name: "暂无数据", itemStyle: { color: "#eee" }, tooltip: { show: false } }],
    }],
  });
}

// ── 3. 客户状态分布饼图 ──
function renderCustStatusChart() {
  if (!custStatusChartRef.value) return;
  const c = echarts.init(custStatusChartRef.value, "macarons");
  charts.push(c);
  const statusMap: Record<string, string> = {
    new: "新客户", contacted: "已联系", qualified: "已筛选",
    negotiating: "洽谈中", closed: "已成交",
  };
  const raw = stats.value.customer_status_counts || {};
  const data = Object.entries(raw).map(([k, v]) => ({ name: statusMap[k] || k, value: v }));
  const total = data.reduce((s, d) => s + d.value, 0);

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: "item", formatter: "{b}: {c} ({d}%)" },
    graphic: total > 0
      ? [{ type: "text", left: "center", top: "42%", style: { text: `${total}\n客户总数`, textAlign: "center", fill: "#008acd", fontSize: 15, fontWeight: 700, lineHeight: 20 } }]
      : [],
    series: [{
      type: "pie", radius: ["50%", "75%"], center: ["40%", "50%"],
      avoidLabelOverlap: false, label: { show: false },
      emphasis: { scaleSize: 6, label: { show: true, fontSize: 13, fontWeight: "bold" } },
      data: data.length > 0
        ? data.map((d, i) => ({
            ...d,
            itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 3,
              color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                { offset: 0, color: R[i * 3 % R.length] }, { offset: 1, color: R[(i * 3 + 5) % R.length] },
              ]),
            },
          }))
        : [{ value: 1, name: "暂无数据", itemStyle: { color: "#eee" }, tooltip: { show: false } }],
    }],
    legend: { orient: "vertical", right: 4, top: "center", icon: "circle", itemWidth: 8, itemHeight: 8, itemGap: 12, textStyle: { color: "#555", fontSize: 12 } },
  });
}

// ── 4. 各画像客户分布横向柱图 ──
function renderIcpBarChart() {
  if (!icpBarChartRef.value) return;
  const c = echarts.init(icpBarChartRef.value, "macarons");
  charts.push(c);
  const data = stats.value.customer_icp_stats || [];
  if (data.length === 0) {
    c.setOption({
      title: { text: "暂无数据", left: "center", top: "center", textStyle: { color: "#999", fontSize: 14, fontWeight: "normal" } },
    });
    return;
  }
  const display = data.slice(0, 10);
  const names = display.map((d) => d.icp_name).reverse();
  const totals = display.map((d) => d.total).reverse();

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 4, right: 20, top: 4, bottom: 0, containLabel: true },
    xAxis: { type: "value", splitLine: { lineStyle: { color: GRID_LINE } }, axisLabel: { color: TEXT_DIM, fontSize: 10 } },
    yAxis: { type: "category", data: names, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: "#555", fontSize: 11, width: 100, overflow: "truncate" } },
    series: [{
      type: "bar",
      data: totals.map((v) => ({
        value: v,
        itemStyle: { borderRadius: [0, 6, 6, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[1] }, { offset: 1, color: R[0] }]) },
      })),
      barWidth: 16,
      label: { show: true, position: "right", color: TEXT_DIM, fontSize: 11 },
    }],
  });
}

// ── 5. 邮件趋势面积图 ──
function renderEmailChart() {
  if (!emailChartRef.value) return;
  const c = echarts.init(emailChartRef.value, "macarons");
  charts.push(c);
  const data = stats.value.daily_email_stats;
  if (data.length === 0) {
    c.setOption({
      title: { text: "暂无数据", left: "center", top: "center", textStyle: { color: "#999", fontSize: 14, fontWeight: "normal" } },
    });
    return;
  }
  const days = data.map((d) => d.day.slice(5));

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: "axis" },
    legend: { show: false },
    grid: { left: 0, right: 6, top: 8, bottom: 0, containLabel: true },
    xAxis: { type: "category", data: days, axisLabel: { color: TEXT_DIM, fontSize: 10 }, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: GRID_LINE, type: "dashed" } }, axisLabel: { color: TEXT_DIM, fontSize: 10 } },
    series: [
      {
        name: "已发送", type: "line", data: data.map((d) => d.sent),
        smooth: true, symbol: "none", lineStyle: { color: R[0], width: 2.5 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(46,199,201,0.15)" }, { offset: 1, color: "rgba(46,199,201,0.0)" }]) },
      },
      {
        name: "已打开", type: "line", data: data.map((d) => d.opened),
        smooth: true, symbol: "none", lineStyle: { color: R[1], width: 2.5 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(182,162,222,0.18)" }, { offset: 1, color: "rgba(182,162,222,0.0)" }]) },
      },
      {
        name: "已回复", type: "line", data: data.map((d) => d.replied),
        smooth: true, symbol: "none", lineStyle: { color: R[4], width: 2, type: "dashed" },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: "rgba(216,122,128,0.12)" }, { offset: 1, color: "rgba(216,122,128,0.0)" }]) },
      },
    ],
  });
}

// ── 6. 邮件转化漏斗 ──
function renderFunnelChart() {
  if (!funnelChartRef.value) return;
  const c = echarts.init(funnelChartRef.value, "macarons");
  charts.push(c);
  const s = stats.value;
  const sent = s.total_emails_sent || 0;
  const opened = s.total_emails_opened || 0;
  const replied = s.total_emails_replied || 0;

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: "item", formatter: "{b}: {c}" },
    series: [{
      type: "funnel",
      left: "15%", right: "15%", top: 60, bottom: 60,
      width: "70%",
      max: sent || 100, min: 0,
      sort: "descending", gap: 4, funnelAlign: "center",
      label: { show: true, position: "inside", formatter: (p: any) => `${p.name}  ${p.value}`, fontSize: 13, fontWeight: 600, color: "#fff" },
      labelLine: { show: false },
      itemStyle: { borderColor: "#fff", borderWidth: 0 },
      emphasis: { label: { fontSize: 16 } },
      data: [
        { value: sent, name: "已发送", itemStyle: { borderRadius: [8, 8, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[0] }, { offset: 1, color: R[10] }]) } },
        { value: opened, name: "已打开", itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[1] }, { offset: 1, color: R[11] }]) } },
        { value: replied, name: "已回复", itemStyle: { borderRadius: [0, 0, 8, 8], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: R[4] }, { offset: 1, color: R[14] }]) } },
      ],
    }],
  });
}

function renderAllCharts() {
  nextTick(() => {
    charts.forEach((c) => c.dispose());
    charts = [];
    renderIcpChart(); renderSourceChart(); renderCustStatusChart();
    renderIcpBarChart(); renderEmailChart(); renderFunnelChart();
  });
}

function handleResize() { charts.forEach((c) => c.resize()); }

onMounted(async () => {
  await loadStats();
  renderAllCharts();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  charts.forEach((c) => c.dispose());
});
</script>

<style scoped lang="scss">
// ═══════════════════════════════════════════
// 页面容器 — 浅色高级风格
// ═══════════════════════════════════════════
.analytics-page {
  min-height: 100%;
  padding: 28px 32px 40px;
  background: #f8fafc;
}

// ── 页面标题 ──
.page-hero {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 36px;

  &__icon { width: 44px; height: 44px; flex-shrink: 0; svg { width: 44px; height: 44px; } }

  &__text {
    h1 { margin: 0; font-size: 26px; font-weight: 800; color: #0f172a; letter-spacing: -0.5px; }
    p { margin: 3px 0 0; font-size: 13px; color: #94a3b8; }
  }
}

// ── 区块 ──
.analytics-section { margin-bottom: 40px; }

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;

  &__dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  h2 { margin: 0; font-size: 16px; font-weight: 700; color: #0f172a; }
  &__line { flex: 1; height: 1px; background: #e8ecf1; }
}

// ── KPI 卡片 ──
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.kpi-card {
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);

  &:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05); transform: translateY(-1px); }

  &__icon {
    width: 42px; height: 42px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }
  &__body { flex: 1; display: flex; flex-direction: column; }
  &__val { font-size: 24px; font-weight: 700; color: #0f172a; line-height: 1.2; letter-spacing: -0.5px; }
  &__lbl { font-size: 11px; color: #94a3b8; }
}

// ── 企业档案完整度卡片 ──
.ent-completion-card {
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 14px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 40px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.ent-completion__overall {
  flex-shrink: 0;
}

.ent-completion__ring {
  width: 100px;
  height: 100px;
  position: relative;
}

.ent-ring-svg {
  width: 100px;
  height: 100px;
}

.ent-ring-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ent-ring-val {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.ent-completion__detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ent-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ent-bar-label {
  width: 72px;
  font-size: 12px;
  font-weight: 500;
  color: #475569;
  text-align: right;
  flex-shrink: 0;
}

.ent-bar-track {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.ent-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.ent-bar-num {
  width: 44px;
  font-size: 11px;
  color: #94a3b8;
  text-align: left;
  flex-shrink: 0;
}

// ── 图表行 ──
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 14px;
  &--full { grid-template-columns: 1fr; }
}

// ── 图表卡片 ──
.chart-card {
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 14px;
  padding: 22px 24px 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: box-shadow 0.2s;

  &:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05); }

  &__head {
    display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;
    h3 { margin: 0; font-size: 14px; font-weight: 700; color: #0f172a; }
  }

  &__badge {
    font-size: 10px; color: #94a3b8;
    background: #f1f5f9; padding: 2px 8px; border-radius: 4px; border: 1px solid #e8ecf1;
  }
}

.chart-legend { display: flex; gap: 16px; margin-bottom: 4px; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #94a3b8;
  i { display: inline-block; width: 8px; height: 3px; border-radius: 2px; }
}

// ── 图表容器 ──
.chart-body {
  width: 100%; height: 240px;
  &--donut  { height: 280px; }
  &--bar    { height: 340px; }
  &--mail   { height: 310px; }
  &--center { display: flex; align-items: center; justify-content: center; }
}

// ── 大数字统计（画像完成率） ──
.big-stat {
  display: flex; flex-direction: column; align-items: center; gap: 6px;

  &__num {
    font-size: 48px; font-weight: 900; letter-spacing: -2px;
    background: linear-gradient(135deg, #2ec7c9 0%, #5ab1ef 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  }
  &__sub { font-size: 14px; color: #64748b; }
  &__hint { font-size: 12px; color: #94a3b8; }
}
</style>
