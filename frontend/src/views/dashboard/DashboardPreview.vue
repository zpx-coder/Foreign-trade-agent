<template>
  <div class="dv-page">
    <!-- ═══ KPI 指标卡 ═══ -->
    <div class="kpi-row">
      <div class="kpi-card kpi--blue">
        <div class="kpi-icon"><el-icon :size="18"><UserFilled /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.total_customers || 0 }}</span>
          <span class="kpi-lbl">获取客户</span>
          <span class="kpi-trend up" v-if="stats.customers_reached">{{ stats.customers_reached }} 已触达</span>
        </div>
      </div>
      <div class="kpi-card kpi--green">
        <div class="kpi-icon"><el-icon :size="18"><PictureFilled /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.completed_icps || 0 }}</span>
          <span class="kpi-lbl">客户画像</span>
          <span class="kpi-trend" v-if="stats.total_icps">共 {{ stats.total_icps }} 个</span>
        </div>
      </div>
      <div class="kpi-card kpi--purple">
        <div class="kpi-icon"><el-icon :size="18"><Message /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.total_emails_sent || 0 }}</span>
          <span class="kpi-lbl">已发邮件</span>
          <span class="kpi-trend" v-if="stats.total_emails_sent">回复率 {{ (stats.reply_rate * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <div class="kpi-card kpi--amber">
        <div class="kpi-icon"><el-icon :size="18"><TrendCharts /></el-icon></div>
        <div class="kpi-body">
          <span class="kpi-val">{{ stats.total_customers ? (stats.reach_rate * 100).toFixed(0) + '%' : '—' }}</span>
          <span class="kpi-lbl">触达率</span>
        </div>
      </div>
    </div>

    <!-- ═══ 图表区 ═══ -->
    <div class="chart-row">
      <!-- 邮件发送趋势 — 渐变面积图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">邮件发送趋势</h3>
          <span class="chart-card__sub">近 30 天</span>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><i style="background:#818cf8;"></i>已发送</span>
          <span class="legend-item"><i style="background:#34d399;"></i>已打开</span>
          <span class="legend-item"><i style="background:#fbbf24;"></i>已回复</span>
        </div>
        <div ref="emailRef" class="chart-body"></div>
      </div>

      <!-- 客户来源 — 科技感环形图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">客户来源分布</h3>
        </div>
        <div ref="sourceRef" class="chart-body chart-body--donut"></div>
      </div>
    </div>

    <div class="chart-row">
      <!-- 画像状态 — 渐变柱状图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">画像状态分布</h3>
        </div>
        <div ref="icpRef" class="chart-body chart-body--bar"></div>
      </div>

      <!-- 邮件转化漏斗 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">邮件转化漏斗</h3>
        </div>
        <div ref="funnelRef" class="chart-body chart-body--funnel"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { UserFilled, PictureFilled, Message, TrendCharts } from '@element-plus/icons-vue'
import api from '@/api/client'
import * as echarts from 'echarts/core'
import { LineChart, PieChart, BarChart, FunnelChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, PieChart, BarChart, FunnelChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

interface DashboardStats {
  total_icps: number; completed_icps: number; generating_icps: number
  draft_icps: number; failed_icps: number
  total_customers: number; customers_reached: number; reach_rate: number
  customer_sources: Array<{ name: string; value: number }>
  total_emails_sent: number; total_emails_opened: number; total_emails_replied: number
  reply_rate: number; daily_email_stats: Array<{ day: string; sent: number; opened: number; replied: number }>
}

const stats = ref<DashboardStats>({
  total_icps: 0, completed_icps: 0, generating_icps: 0, draft_icps: 0, failed_icps: 0,
  total_customers: 0, customers_reached: 0, reach_rate: 0, customer_sources: [],
  total_emails_sent: 0, total_emails_opened: 0, total_emails_replied: 0, reply_rate: 0,
  daily_email_stats: [],
})

// ── 图表 refs ──
const emailRef = ref<HTMLDivElement>()
const sourceRef = ref<HTMLDivElement>()
const icpRef = ref<HTMLDivElement>()
const funnelRef = ref<HTMLDivElement>()
let charts: echarts.ECharts[] = []

// ── 通用配置 ──
const TEXT_DIM = '#94a3b8'
const GRID_LINE = '#f1f5f9'

function makeTooltip(): any {
  return {
    backgroundColor: '#fff',
    borderColor: '#e8ecf1',
    borderWidth: 1,
    textStyle: { color: '#334155', fontSize: 12 },
    boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
    extraCssText: 'border-radius:10px;padding:10px 14px;',
  }
}

// ── 1. 渐变面积图（邮件趋势） ──
function renderEmail() {
  if (!emailRef.value) return
  const c = echarts.init(emailRef.value)
  charts.push(c)
  const data = stats.value.daily_email_stats
  const days = data.map(d => d.day.slice(5))
  const sent = data.map(d => d.sent)
  const opened = data.map(d => d.opened)
  const replied = data.map(d => d.replied)

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
        lineStyle: { color: '#818cf8', width: 2.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(129,140,248,0.15)' },
            { offset: 1, color: 'rgba(129,140,248,0.0)' },
          ]),
        },
      },
      {
        name: '已打开', type: 'line', data: opened,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#34d399', width: 2.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(52,211,153,0.12)' },
            { offset: 1, color: 'rgba(52,211,153,0.0)' },
          ]),
        },
      },
      {
        name: '已回复', type: 'line', data: replied,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#fbbf24', width: 2, type: 'dashed' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(251,191,36,0.10)' },
            { offset: 1, color: 'rgba(251,191,36,0.0)' },
          ]),
        },
      },
    ],
  })
}

// ── 2. 科技感环形图（客户来源） ──
function renderSource() {
  if (!sourceRef.value) return
  const c = echarts.init(sourceRef.value)
  charts.push(c)
  const data = stats.value.customer_sources
  const palette = ['#818cf8', '#34d399', '#fbbf24', '#60a5fa', '#f472b6', '#a78bfa', '#94a3b8']

  const total = data.reduce((s, d) => s + d.value, 0)
  const seriesData = data.length > 0
    ? data.map((d, i) => ({
        ...d,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
            { offset: 0, color: palette[i % palette.length] },
            { offset: 1, color: palette[(i + 1) % palette.length] },
          ]),
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 3,
        },
      }))
    : [{ value: 1, name: '暂无', itemStyle: { color: '#e8ecf1' }, tooltip: { show: false } }]

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    graphic: total > 0 ? [{
      type: 'text',
      left: 'center', top: 'center',
      style: {
        text: `${total}\n客户总数`,
        textAlign: 'center',
        fill: '#0f172a',
        fontSize: 16, fontWeight: 700, lineHeight: 20,
      },
    }] : [],
    series: [{
      type: 'pie',
      radius: ['60%', '82%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      label: { show: false },
      emphasis: {
        scaleSize: 6,
        label: { show: true, fontSize: 13, fontWeight: 'bold' },
      },
      data: seriesData,
    }],
  })
}

// ── 3. 渐变横向柱状图（画像状态） ──
function renderIcp() {
  if (!icpRef.value) return
  const c = echarts.init(icpRef.value)
  charts.push(c)
  const s = stats.value
  const items = [
    { label: '已完成',   value: s.completed_icps  || 0, color: ['#34d399', '#6ee7b7'] },
    { label: '生成中',   value: s.generating_icps || 0, color: ['#fbbf24', '#fcd34d'] },
    { label: '草稿',     value: s.draft_icps      || 0, color: ['#94a3b8', '#cbd5e1'] },
    { label: '失败',     value: s.failed_icps     || 0, color: ['#f87171', '#fca5a5'] },
  ]

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 0, right: 20, top: 8, bottom: 0, containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { show: false }, axisTick: { show: false },
      splitLine: { lineStyle: { color: GRID_LINE, type: 'dashed' } },
      axisLabel: { color: TEXT_DIM, fontSize: 10 },
    },
    yAxis: {
      type: 'category', data: items.map(i => i.label),
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#475569', fontSize: 12, fontWeight: 500 },
    },
    series: [{
      type: 'bar',
      barWidth: 16,
      showBackground: true,
      backgroundStyle: { color: '#f8fafc', borderRadius: [0, 8, 8, 0] },
      data: items.map((i, idx) => ({
        value: i.value,
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: i.color[0] },
            { offset: 1, color: i.color[1] },
          ]),
        },
      })),
      label: { show: true, position: 'right', color: '#334155', fontSize: 12, fontWeight: 600 },
    }],
  })
}

// ── 4. 漏斗图（邮件转化） ──
function renderFunnel() {
  if (!funnelRef.value) return
  const c = echarts.init(funnelRef.value)
  charts.push(c)
  const s = stats.value
  const data = [
    { value: s.total_emails_sent   || 0, name: '已发送' },
    { value: s.total_emails_opened || 0, name: '已打开' },
    { value: s.total_emails_replied || 0, name: '已回复' },
  ]

  c.setOption({
    tooltip: { ...makeTooltip(), trigger: 'item', formatter: '{b}: {c}' },
    series: [{
      type: 'funnel',
      left: '10%', right: '10%', top: 20, bottom: 10,
      min: 0,
      max: data[0]?.value || 100,
      sort: 'descending',
      gap: 2,
      label: {
        show: true,
        position: 'inside',
        formatter: '{b}  {c}',
        fontSize: 13, fontWeight: 600, color: '#fff',
      },
      labelLine: { show: false },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 0,
        borderRadius: 4,
      },
      emphasis: { label: { fontSize: 16 } },
      data: data.map((d, i) => ({
        ...d,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: ['#818cf8', '#34d399', '#fbbf24'][i] },
            { offset: 1, color: ['#6366f1', '#10b981', '#f59e0b'][i] },
          ]),
        },
      })),
    }],
  })
}

// ── 渲染所有 ──
function renderAll() {
  nextTick(() => {
    charts.forEach(c => c.dispose()); charts = []
    renderEmail(); renderSource(); renderIcp(); renderFunnel()
  })
}

function handleResize() { charts.forEach(c => c.resize()) }

async function loadStats() {
  try {
    const { data } = await api.get('/dashboard/stats', { silent: true })
    stats.value = { ...stats.value, ...data }
  } catch { /* */ }
  renderAll()
}

onMounted(async () => {
  await loadStats()
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped lang="scss">
$bg:     #f8f9fb;
$card:   #fff;
$border: #eaecef;
$radius: 16px;
$shadow: 0 1px 3px rgba(0,0,0,.04);
$t1: #0f172a;
$t2: #475569;
$t3: #94a3b8;

.dv-page { max-width: 1050px; margin: 0 auto; }

// ── KPI 卡片 ──
.kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px;
}
.kpi-card {
  background: $card; border: 1px solid $border; border-radius: $radius;
  box-shadow: $shadow; padding: 18px 20px;
  display: flex; align-items: center; gap: 14px;
  transition: all .2s;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,.05); transform: translateY(-1px); }
}
.kpi-icon {
  width: 42px; height: 42px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.kpi--blue   .kpi-icon { background: linear-gradient(135deg, #eef2ff, #e0e7ff); color: #6366f1; }
.kpi--green  .kpi-icon { background: linear-gradient(135deg, #ecfdf5, #d1fae5); color: #10b981; }
.kpi--purple .kpi-icon { background: linear-gradient(135deg, #f5f3ff, #ede9fe); color: #7c3aed; }
.kpi--amber  .kpi-icon { background: linear-gradient(135deg, #fffbeb, #fef3c7); color: #f59e0b; }

.kpi-body { flex: 1; display: flex; flex-direction: column; }
.kpi-val  { font-size: 24px; font-weight: 700; color: $t1; line-height: 1.2; letter-spacing: -.5px; }
.kpi-lbl  { font-size: 11px; color: $t3; margin-bottom: 2px; }
.kpi-trend { font-size: 11px; color: #10b981; &.up { color: #10b981; } }

// ── 图表行 ──
.chart-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;
}

// ── 图表卡片 ──
.chart-card {
  background: $card; border: 1px solid $border; border-radius: $radius;
  box-shadow: $shadow; padding: 22px 24px 18px;
  transition: box-shadow .2s;
  &:hover { box-shadow: 0 4px 16px rgba(0,0,0,.05); }

  &__head {
    display: flex; align-items: baseline; justify-content: space-between;
    margin-bottom: 6px;
  }
  &__title { margin: 0; font-size: 14px; font-weight: 700; color: $t1; }
  &__sub  { font-size: 11px; color: $t3; }
}

.chart-legend {
  display: flex; gap: 16px; margin-bottom: 4px;
}
.legend-item {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: $t3;
  i { display: inline-block; width: 8px; height: 3px; border-radius: 2px; }
}

.chart-body { width: 100%; height: 240px; }
.chart-body--donut { height: 280px; }
.chart-body--bar   { height: 200px; }

// ── 漏斗图 ──
.chart-body--funnel { height: 280px; }
</style>
