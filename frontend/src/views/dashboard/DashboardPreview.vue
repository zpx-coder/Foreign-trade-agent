<template>
  <div class="dv-page">
    <!-- ═══ 指标卡片（高级简约） ═══ -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%); color: #4f6ef7;">
          <el-icon :size="18"><UserFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats.total_customers || 0 }}</span>
          <span class="kpi-lbl">获取客户</span>
        </div>
        <span class="kpi-sub" v-if="stats.customers_reached">{{ stats.customers_reached }} 已触达</span>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); color: #22c55e;">
          <el-icon :size="18"><PictureFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats.completed_icps || 0 }}<span class="kpi-total">/{{ stats.total_icps || 0 }}</span></span>
          <span class="kpi-lbl">客户画像</span>
        </div>
        <span class="kpi-sub" v-if="stats.completed_icps">已完成</span>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); color: #7c3aed;">
          <el-icon :size="18"><Message /></el-icon>
        </div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats.total_emails_sent || 0 }}</span>
          <span class="kpi-lbl">已发邮件</span>
        </div>
        <span class="kpi-sub" v-if="stats.total_emails_sent">回复率 {{ (stats.reply_rate * 100).toFixed(0) }}%</span>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%); color: #f59e0b;">
          <el-icon :size="18"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <span class="kpi-val">{{ stats.total_customers ? (stats.reach_rate * 100).toFixed(0) + '%' : '—' }}</span>
          <span class="kpi-lbl">客户触达率</span>
        </div>
        <span class="kpi-sub">触达 / 总客户</span>
      </div>
    </div>

    <!-- ═══ 图表区 ═══ -->
    <div class="chart-row">
      <!-- 邮件发送趋势 — 渐变面积图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <div>
            <h3 class="chart-card__title">邮件发送趋势</h3>
            <span class="chart-card__sub">近 30 天</span>
          </div>
          <div class="chart-legend">
            <span class="legend-dot" style="background:#6366f1;"></span>已发送
            <span class="legend-dot" style="background:#22c55e;"></span>已打开
            <span class="legend-dot" style="background:#f59e0b;"></span>已回复
          </div>
        </div>
        <div ref="emailChartRef" class="chart-body"></div>
      </div>

      <!-- 客户来源 — 现代环形图 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <h3 class="chart-card__title">客户来源分布</h3>
        </div>
        <div ref="sourceChartRef" class="chart-body"></div>
      </div>
    </div>

    <div class="chart-row">
      <!-- 画像状态 — 渐变进度条 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <div>
            <h3 class="chart-card__title">画像状态分布</h3>
          </div>
        </div>
        <div class="icp-bars">
          <div class="icp-bar-item">
            <div class="icp-bar-label">
              <span class="icp-bar-dot" style="background:#22c55e;"></span>已完成
              <strong>{{ stats.completed_icps || 0 }}</strong>
            </div>
            <div class="icp-bar-track"><div class="icp-bar-fill" :style="{ width: icpPct('completed') + '%', background: 'linear-gradient(90deg, #22c55e, #4ade80)' }"></div></div>
          </div>
          <div class="icp-bar-item">
            <div class="icp-bar-label">
              <span class="icp-bar-dot" style="background:#f59e0b;"></span>生成中
              <strong>{{ stats.generating_icps || 0 }}</strong>
            </div>
            <div class="icp-bar-track"><div class="icp-bar-fill" :style="{ width: icpPct('generating') + '%', background: 'linear-gradient(90deg, #f59e0b, #fbbf24)' }"></div></div>
          </div>
          <div class="icp-bar-item">
            <div class="icp-bar-label">
              <span class="icp-bar-dot" style="background:#94a3b8;"></span>草稿
              <strong>{{ stats.draft_icps || 0 }}</strong>
            </div>
            <div class="icp-bar-track"><div class="icp-bar-fill" :style="{ width: icpPct('draft') + '%', background: 'linear-gradient(90deg, #94a3b8, #c0c7d0)' }"></div></div>
          </div>
          <div class="icp-bar-item">
            <div class="icp-bar-label">
              <span class="icp-bar-dot" style="background:#ef4444;"></span>失败
              <strong>{{ stats.failed_icps || 0 }}</strong>
            </div>
            <div class="icp-bar-track"><div class="icp-bar-fill" :style="{ width: icpPct('failed') + '%', background: 'linear-gradient(90deg, #ef4444, #f87171)' }"></div></div>
          </div>
        </div>
      </div>

      <!-- 邮件转化漏斗 — 横向渐变条 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <div>
            <h3 class="chart-card__title">邮件转化漏斗</h3>
          </div>
        </div>
        <div class="funnel-section">
          <div class="funnel-step">
            <div class="funnel-step__header">
              <span class="funnel-step__label">已发送</span>
              <span class="funnel-step__num">{{ stats.total_emails_sent || 0 }}</span>
            </div>
            <div class="funnel-step__bar" style="width: 100%; background: linear-gradient(90deg, #6366f1, #818cf8);"></div>
          </div>
          <div class="funnel-step">
            <div class="funnel-step__header">
              <span class="funnel-step__label">已打开</span>
              <span class="funnel-step__num">{{ stats.total_emails_opened || 0 }}</span>
              <span class="funnel-step__pct" v-if="stats.total_emails_sent">{{ (stats.total_emails_opened / stats.total_emails_sent * 100).toFixed(0) }}%</span>
            </div>
            <div class="funnel-step__bar" :style="{ width: funnelW('opened') + '%', background: 'linear-gradient(90deg, #8b5cf6, #a78bfa)' }"></div>
          </div>
          <div class="funnel-step">
            <div class="funnel-step__header">
              <span class="funnel-step__label">已回复</span>
              <span class="funnel-step__num">{{ stats.total_emails_replied || 0 }}</span>
              <span class="funnel-step__pct" v-if="stats.total_emails_sent">{{ (stats.reply_rate * 100).toFixed(0) }}%</span>
            </div>
            <div class="funnel-step__bar" :style="{ width: funnelW('replied') + '%', background: 'linear-gradient(90deg, #22c55e, #4ade80)' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { UserFilled, PictureFilled, Message, TrendCharts } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'
import * as echarts from 'echarts/core'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const authStore = useAuthStore()

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

// ── 百分比计算 ──
const icpMax = computed(() => {
  const { completed_icps, generating_icps, draft_icps, failed_icps } = stats.value
  return Math.max(completed_icps, generating_icps, draft_icps, failed_icps, 1)
})
function icpPct(key: string) {
  const max = icpMax.value
  const v = (stats.value as any)[key + '_icps'] || 0
  return Math.round((v / max) * 100)
}
function funnelW(stage: string) {
  const sent = stats.value.total_emails_sent || 1
  if (stage === 'opened') return Math.round((stats.value.total_emails_opened || 0) / sent * 100)
  if (stage === 'replied') return Math.round((stats.value.total_emails_replied || 0) / sent * 100)
  return 100
}

// ── 图表 ──
const emailChartRef = ref<HTMLDivElement>()
const sourceChartRef = ref<HTMLDivElement>()
let emailChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null

const COL = { line: '#e8ecf1', text: '#94a3b8', axis: '#cbd5e1' }

function renderEmailChart() {
  if (!emailChartRef.value) return
  if (!emailChart) emailChart = echarts.init(emailChartRef.value)
  const data = stats.value.daily_email_stats
  const days = data.map(d => d.day.slice(5))
  const sent = data.map(d => d.sent)
  const opened = data.map(d => d.opened)
  const replied = data.map(d => d.replied)

  emailChart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#e8ecf1',
      borderWidth: 1,
      textStyle: { color: '#334155', fontSize: 12 },
      boxShadow: '0 8px 24px rgba(0,0,0,0.06)',
    },
    legend: { show: false },
    grid: { left: 0, right: 8, top: 10, bottom: 0, containLabel: true },
    xAxis: {
      type: 'category', data: days,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: COL.text, fontSize: 10, interval: Math.max(Math.floor(days.length / 6), 0) },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: COL.line, type: 'dashed' } },
      axisLabel: { color: COL.text, fontSize: 10 },
    },
    series: [
      {
        name: '已发送', type: 'line', data: sent,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#6366f1', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(99,102,241,0.12)' },
            { offset: 1, color: 'rgba(99,102,241,0.0)' },
          ]),
        },
      },
      {
        name: '已打开', type: 'line', data: opened,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#22c55e', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(34,197,94,0.10)' },
            { offset: 1, color: 'rgba(34,197,94,0.0)' },
          ]),
        },
      },
      {
        name: '已回复', type: 'line', data: replied,
        smooth: true, symbol: 'none',
        lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' },
      },
    ],
  })
}

function renderSourceChart() {
  if (!sourceChartRef.value) return
  if (!sourceChart) sourceChart = echarts.init(sourceChartRef.value)
  const data = stats.value.customer_sources
  const palette = ['#6366f1', '#22c55e', '#f59e0b', '#3b82f6', '#ec4899', '#94a3b8']

  const seriesData = data.length > 0
    ? data.map((d, i) => ({ ...d, itemStyle: { color: palette[i % palette.length], borderRadius: 6, borderColor: '#fff', borderWidth: 2 } }))
    : [{ value: 1, name: '暂无数据', itemStyle: { color: '#e8ecf1' }, tooltip: { show: false } }]

  sourceChart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: '#fff',
      borderColor: '#e8ecf1',
      borderWidth: 1,
      textStyle: { color: '#334155', fontSize: 12 },
      boxShadow: '0 8px 24px rgba(0,0,0,0.06)',
      formatter: '{b}: {c} ({d}%)',
    },
    series: [{
      type: 'pie',
      radius: ['58%', '82%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      label: { show: false },
      emphasis: { scaleSize: 6, label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: seriesData,
    }],
  })
}

function handleResize() {
  emailChart?.resize()
  sourceChart?.resize()
}

async function loadStats() {
  try {
    const { data } = await api.get('/dashboard/stats', { silent: true })
    stats.value = { ...stats.value, ...data }
  } catch { /* */ }
  nextTick(() => { renderEmailChart(); renderSourceChart() })
}

onMounted(async () => {
  await loadStats()
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  emailChart?.dispose(); sourceChart?.dispose()
})
</script>

<style scoped lang="scss">
$bg:     #f8f9fb;
$card:   #fff;
$border: #eaecef;
$radius: 16px;
$shadow: 0 1px 3px rgba(0,0,0,.03);
$t1: #0f172a;
$t2: #475569;
$t3: #94a3b8;

.dv-page { max-width: 1050px; margin: 0 auto; }

// ── 指标卡片 ──
.kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
  margin-bottom: 18px;
}
.kpi-card {
  background: $card; border: 1px solid $border; border-radius: $radius;
  box-shadow: $shadow; padding: 20px 22px;
  display: flex; align-items: center; gap: 14px;
  transition: box-shadow .2s;
  &:hover { box-shadow: 0 4px 14px rgba(0,0,0,.04); }
}
.kpi-icon {
  width: 40px; height: 40px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.kpi-info { flex: 1; display: flex; flex-direction: column; }
.kpi-val {
  font-size: 22px; font-weight: 700; color: $t1; line-height: 1.2;
  font-variant-numeric: tabular-nums;
}
.kpi-total { font-size: 14px; font-weight: 500; color: $t3; margin-left: 2px; }
.kpi-lbl { font-size: 11px; color: $t3; }
.kpi-sub  { font-size: 11px; color: $t3; flex-shrink: 0; }

// ── 图表行 ──
.chart-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
  margin-bottom: 14px;
}

// ── 图表卡片 ──
.chart-card {
  background: $card; border: 1px solid $border; border-radius: $radius;
  box-shadow: $shadow; padding: 22px 24px 18px;
  transition: box-shadow .2s;
  &:hover { box-shadow: 0 4px 14px rgba(0,0,0,.04); }

  &__head {
    display: flex; align-items: flex-start; justify-content: space-between;
    margin-bottom: 12px;
  }
  &__title { margin: 0; font-size: 14px; font-weight: 700; color: $t1; }
  &__sub  { font-size: 11px; color: $t3; }
}

.chart-legend { display: flex; align-items: center; gap: 4px 12px; flex-wrap: wrap; font-size: 11px; color: $t3; }
.legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin-right: 4px; }

.chart-body { width: 100%; height: 240px; }

// ── 画像进度条 ──
.icp-bars {
  display: flex; flex-direction: column; gap: 14px;
  padding: 6px 0 8px;
}
.icp-bar-item {
  display: flex; align-items: center; gap: 12px;
}
.icp-bar-label {
  width: 90px; flex-shrink: 0;
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: $t2;
  strong { font-weight: 600; color: $t1; margin-left: auto; }
}
.icp-bar-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.icp-bar-track {
  flex: 1; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden;
}
.icp-bar-fill {
  height: 100%; border-radius: 4px;
  min-width: 0; transition: width .6s cubic-bezier(.4,0,.2,1);
}

// ── 漏斗 ──
.funnel-section {
  display: flex; flex-direction: column; gap: 18px;
  padding: 6px 0 8px;
}
.funnel-step {
  &__header {
    display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px;
  }
  &__label { font-size: 12px; color: $t2; }
  &__num   { font-size: 16px; font-weight: 700; color: $t1; }
  &__pct   { font-size: 12px; color: $t3; margin-left: auto; }
  &__bar {
    height: 10px; border-radius: 5px;
    min-width: 4px;
    transition: width .6s cubic-bezier(.4,0,.2,1);
  }
}
</style>
