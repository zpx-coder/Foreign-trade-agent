<template>
  <div class="dashboard-preview">
    <!-- ── 欢迎横幅 ── -->
    <section class="hero-banner">
      <div class="hero-banner__greeting">
        <h1>你好，{{ authStore.user?.name || '用户' }}<span class="wave">👋</span></h1>
        <p class="hero-banner__sub">AI 外贸助手已就绪，今日待办与关键数据一览</p>
      </div>
      <div class="hero-banner__kpis">
        <div class="hero-kpi">
          <span class="hero-kpi__num">{{ stats.total_customers || 0 }}</span>
          <span class="hero-kpi__label">获取客户</span>
        </div>
        <div class="hero-kpi">
          <span class="hero-kpi__num">{{ stats.total_emails_sent || 0 }}</span>
          <span class="hero-kpi__label">已发邮件</span>
        </div>
        <div class="hero-kpi">
          <span class="hero-kpi__num">{{ stats.total_customers ? (stats.reply_rate * 100).toFixed(0) + '%' : '—' }}</span>
          <span class="hero-kpi__label">回复率</span>
        </div>
      </div>
    </section>

    <!-- ── 快捷操作 ── -->
    <section class="quick-actions">
      <div class="quick-action-card" @click="$router.push('/app/customers')">
        <div class="qa-icon qa-icon--accent">
          <el-icon :size="20"><MagicStick /></el-icon>
        </div>
        <span class="qa-label">AI 全渠道获客</span>
      </div>
      <div class="quick-action-card" @click="$router.push('/app/icps')">
        <div class="qa-icon qa-icon--blue">
          <el-icon :size="20"><PictureFilled /></el-icon>
        </div>
        <span class="qa-label">客户画像</span>
      </div>
      <div class="quick-action-card" @click="$router.push('/app/enterprise')">
        <div class="qa-icon qa-icon--green">
          <el-icon :size="20"><OfficeBuilding /></el-icon>
        </div>
        <span class="qa-label">企业资料</span>
      </div>
      <div class="quick-action-card" @click="$router.push('/app/email')">
        <div class="qa-icon qa-icon--purple">
          <el-icon :size="20"><Message /></el-icon>
        </div>
        <span class="qa-label">邮件营销</span>
      </div>
    </section>

    <!-- ── 双栏主体 ── -->
    <section class="main-grid">
      <!-- 左栏：最近动态 -->
      <div class="main-left">
        <div class="panel panel--activity">
          <div class="panel__header">
            <h3 class="panel__title">最近动态</h3>
            <span class="panel__badge">{{ activities.length }} 条</span>
          </div>
          <div class="activity-list">
            <div v-for="item in activities" :key="item.id" class="activity-item">
              <div class="activity-dot" :class="'dot--' + item.type" />
              <div class="activity-body">
                <span class="activity-title">{{ item.title }}</span>
                <span class="activity-desc">{{ item.desc }}</span>
              </div>
              <span class="activity-time">{{ item.time }}</span>
            </div>
            <div v-if="activities.length === 0" class="activity-empty">
              <span>暂无动态，快去搜索客户吧</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右栏：数据概览 + 待办 -->
      <div class="main-right">
        <!-- 数据概览卡片 -->
        <div class="panel panel--stats">
          <div class="panel__header">
            <h3 class="panel__title">数据概览</h3>
          </div>
          <div class="mini-stats">
            <div class="mini-stat">
              <div class="mini-stat__icon" style="background:#eff6ff;color:#3b82f6;">
                <el-icon :size="16"><PictureFilled /></el-icon>
              </div>
              <div class="mini-stat__info">
                <span class="mini-stat__val">{{ stats.total_icps }}</span>
                <span class="mini-stat__lbl">客户画像</span>
              </div>
              <span class="mini-stat__sub">{{ stats.completed_icps || 0 }} 已完成</span>
            </div>
            <div class="mini-stat">
              <div class="mini-stat__icon" style="background:#ecfdf5;color:#10b981;">
                <el-icon :size="16"><UserFilled /></el-icon>
              </div>
              <div class="mini-stat__info">
                <span class="mini-stat__val">{{ stats.total_customers || '—' }}</span>
                <span class="mini-stat__lbl">获取客户</span>
              </div>
              <span class="mini-stat__sub">{{ stats.customers_reached || 0 }} 已触达</span>
            </div>
            <div class="mini-stat">
              <div class="mini-stat__icon" style="background:#fffbeb;color:#f59e0b;">
                <el-icon :size="16"><TrendCharts /></el-icon>
              </div>
              <div class="mini-stat__info">
                <span class="mini-stat__val">{{ stats.total_customers ? (stats.reach_rate * 100).toFixed(0) + '%' : '—' }}</span>
                <span class="mini-stat__lbl">触达率</span>
              </div>
              <span class="mini-stat__sub">触达 / 总客户</span>
            </div>
            <div class="mini-stat">
              <div class="mini-stat__icon" style="background:#f5f3ff;color:#6366f1;">
                <el-icon :size="16"><Message /></el-icon>
              </div>
              <div class="mini-stat__info">
                <span class="mini-stat__val">{{ stats.total_emails_sent ? (stats.reply_rate * 100).toFixed(0) + '%' : '—' }}</span>
                <span class="mini-stat__lbl">回复率</span>
              </div>
              <span class="mini-stat__sub">已回复 / 已发送</span>
            </div>
          </div>
        </div>

        <!-- 系统进度 -->
        <div class="panel panel--progress">
          <div class="panel__header">
            <h3 class="panel__title">系统进度</h3>
            <span class="progress-pct">{{ setupStep }}/4</span>
          </div>
          <div class="progress-list">
            <div class="progress-item" :class="{ done: enterpriseDone }">
              <el-icon v-if="enterpriseDone" :size="14" class="prog-check"><CircleCheckFilled /></el-icon>
              <el-icon v-else :size="14" class="prog-pending"><RemoveFilled /></el-icon>
              <span>企业资料与产品</span>
            </div>
            <div class="progress-item" :class="{ done: stats.completed_icps > 0 }">
              <el-icon v-if="stats.completed_icps > 0" :size="14" class="prog-check"><CircleCheckFilled /></el-icon>
              <el-icon v-else :size="14" class="prog-pending"><RemoveFilled /></el-icon>
              <span>生成客户画像</span>
            </div>
            <div class="progress-item" :class="{ done: stats.total_customers > 0 }">
              <el-icon v-if="stats.total_customers > 0" :size="14" class="prog-check"><CircleCheckFilled /></el-icon>
              <el-icon v-else :size="14" class="prog-pending"><RemoveFilled /></el-icon>
              <span>AI 搜索客户</span>
            </div>
            <div class="progress-item" :class="{ done: stats.total_emails_sent > 0 }">
              <el-icon v-if="stats.total_emails_sent > 0" :size="14" class="prog-check"><CircleCheckFilled /></el-icon>
              <el-icon v-else :size="14" class="prog-pending"><RemoveFilled /></el-icon>
              <span>发送营销邮件</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { OfficeBuilding, PictureFilled, ArrowRight, UserFilled, TrendCharts, Message, MagicStick, CircleCheckFilled, RemoveFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const authStore = useAuthStore()

interface DashboardStats {
  total_icps: number
  completed_icps: number
  total_customers: number
  customers_reached: number
  reach_rate: number
  total_emails_sent: number
  reply_rate: number
}

const stats = ref<DashboardStats>({
  total_icps: 0, completed_icps: 0,
  total_customers: 0, customers_reached: 0, reach_rate: 0,
  total_emails_sent: 0, reply_rate: 0,
})

const enterpriseDone = ref(false)

const setupStep = computed(() => {
  let s = 1
  if (enterpriseDone.value) s = 2
  if (stats.value.completed_icps > 0) s = 3
  if (stats.value.total_customers > 0) s = 4
  if (stats.value.total_emails_sent > 0) s = 5  // extra
  return Math.min(s, 4)
})

// 模拟活动数据（后续接真实 API）
interface Activity {
  id: string; type: string; title: string; desc: string; time: string
}
const activities = ref<Activity[]>([])

function buildActivities(s: DashboardStats) {
  const result: Activity[] = []
  if (s.total_customers > 0) {
    result.push({ id: '1', type: 'customer', title: '客户获取', desc: `共获取 ${s.total_customers} 个潜在客户`, time: '最新' })
  }
  if (s.total_emails_sent > 0) {
    result.push({ id: '2', type: 'email', title: '邮件营销', desc: `已发送 ${s.total_emails_sent} 封营销邮件`, time: '最新' })
  }
  if (s.completed_icps > 0) {
    result.push({ id: '3', type: 'icp', title: '客户画像', desc: `已完成 ${s.completed_icps} 个客户画像`, time: '最新' })
  }
  if (s.total_customers > 0 && s.customers_reached > 0) {
    result.push({ id: '4', type: 'reach', title: '客户触达', desc: `触达率 ${(s.reach_rate * 100).toFixed(0)}%，${s.customers_reached} 个客户已联系`, time: '最新' })
  }
  if (result.length === 0) {
    result.push({ id: '0', type: 'welcome', title: '欢迎使用', desc: '完善企业资料后开始 AI 智能获客', time: '现在' })
  }
  activities.value = result
}

async function loadStats() {
  try {
    const { data } = await api.get('/dashboard/stats', { silent: true })
    stats.value = { ...stats.value, ...data }
    buildActivities(stats.value)
  } catch { /* not critical */ }
}

async function loadEnterprise() {
  try {
    await api.get('/enterprise', { silent: true })
    enterpriseDone.value = true
  } catch { /* 404 — not yet */ }
}

onMounted(async () => {
  await Promise.all([loadStats(), loadEnterprise()])
})
</script>

<style scoped lang="scss">
// ── 变量 ──
$radius-lg: 16px;
$radius-md: 12px;
$border: #e9ecf1;
$text-1: #0f172a;
$text-2: #475569;
$text-3: #94a3b8;

// ── 欢迎横幅 ──
.hero-banner {
  background: linear-gradient(135deg, #0b1a2e 0%, #132742 40%, #1a3a5c 70%, #1d4ed8 100%);
  border-radius: $radius-lg;
  padding: 32px 40px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;

  // 装饰光晕
  &::before {
    content: '';
    position: absolute;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(59,130,246,.15) 0%, transparent 70%);
    top: -80px; right: -60px;
    pointer-events: none;
  }
  &::after {
    content: '';
    position: absolute;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,102,241,.12) 0%, transparent 70%);
    bottom: -60px; left: 30%;
    pointer-events: none;
  }

  &__greeting {
    position: relative;
    z-index: 1;
    h1 {
      margin: 0 0 6px;
      font-size: 22px; font-weight: 700;
      color: #fff;
      letter-spacing: -.3px;
    }
    .wave {
      display: inline-block;
      animation: wave 2s ease-in-out infinite;
      transform-origin: 70% 70%;
    }
  }
  &__sub {
    margin: 0;
    font-size: 13px;
    color: rgba(255,255,255,.55);
  }

  &__kpis {
    position: relative;
    z-index: 1;
    display: flex;
    gap: 40px;
  }
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  75% { transform: rotate(-8deg); }
}

.hero-kpi {
  text-align: center;
  &__num {
    display: block;
    font-size: 24px; font-weight: 800;
    color: #fff;
    font-family: 'Inter', sans-serif;
    letter-spacing: -.5px;
  }
  &__label {
    font-size: 11px;
    color: rgba(255,255,255,.5);
    margin-top: 2px;
  }
}

// ── 快捷操作 ──
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;

  @media (max-width: 900px) { grid-template-columns: repeat(2, 1fr); }
}

.quick-action-card {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius-md;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: all .2s;
  box-shadow: 0 1px 2px rgba(0,0,0,.03);

  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 14px rgba(59,130,246,.08);
    transform: translateY(-1px);
  }
}

.qa-icon {
  width: 42px; height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  &--accent { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
  &--blue   { background: #eff6ff; color: #3b82f6; }
  &--green  { background: #ecfdf5; color: #10b981; }
  &--purple { background: #f5f3ff; color: #6366f1; }
}

.qa-label {
  font-size: 14px; font-weight: 600;
  color: $text-1;
}

// ── 双栏主体 ──
.main-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;

  @media (max-width: 1024px) { grid-template-columns: 1fr; }
}

// ── 通用面板 ──
.panel {
  background: #fff;
  border: 1px solid $border;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,.03);

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 24px 0;
    margin-bottom: 14px;
  }
  &__title {
    margin: 0;
    font-size: 15px; font-weight: 700;
    color: $text-1;
    letter-spacing: -.2px;
  }
  &__badge {
    font-size: 11px; color: $text-3;
    background: #f1f5f9;
    padding: 2px 10px; border-radius: 10px;
  }
}

// ── 最近动态 ──
.panel--activity {
  .panel__header {
    padding: 20px 24px 0;
  }
}

.activity-list {
  padding: 0 24px 20px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
  &:last-child { border-bottom: none; }
}

.activity-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
  &.dot--customer { background: #3b82f6; }
  &.dot--email    { background: #6366f1; }
  &.dot--icp      { background: #10b981; }
  &.dot--reach    { background: #f59e0b; }
  &.dot--welcome  { background: #94a3b8; }
}

.activity-body {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; gap: 2px;
}

.activity-title {
  font-size: 13px; font-weight: 600;
  color: $text-1;
}

.activity-desc {
  font-size: 12px;
  color: $text-3;
  line-height: 1.4;
}

.activity-time {
  font-size: 11px;
  color: $text-3;
  flex-shrink: 0;
  margin-top: 2px;
}

.activity-empty {
  padding: 40px 0;
  text-align: center;
  color: $text-3;
  font-size: 13px;
}

// ── 右栏：数据概览 ──
.panel--stats {
  margin-bottom: 20px;
}

.mini-stats {
  padding: 0 24px 20px;
  display: flex; flex-direction: column; gap: 12px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 10px;
  transition: background .15s;
  &:hover { background: #f1f5f9; }

  &__icon {
    width: 34px; height: 34px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  &__info {
    flex: 1;
    display: flex; flex-direction: column;
  }
  &__val {
    font-size: 16px; font-weight: 700;
    color: $text-1;
    line-height: 1.2;
  }
  &__lbl {
    font-size: 11px; color: $text-3;
  }
  &__sub {
    font-size: 11px; color: $text-3;
    flex-shrink: 0;
  }
}

// ── 系统进度 ──
.progress-pct {
  font-size: 12px; font-weight: 600;
  color: #3b82f6;
}

.progress-list {
  padding: 0 24px 20px;
  display: flex; flex-direction: column; gap: 4px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px; color: $text-2;
  transition: background .15s;

  &:hover { background: #f8fafc; }

  &.done {
    color: $text-1;
    .prog-check { color: #10b981; }
  }
}

.prog-check { color: #10b981; flex-shrink: 0; }
.prog-pending { color: #cbd5e1; flex-shrink: 0; }
</style>
