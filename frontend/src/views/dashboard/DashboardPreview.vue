<template>
  <div class="dashboard-preview">
    <!-- ═══ 问候卡片（白底，非暗色横幅） ═══ -->
    <div class="greeting-card">
      <div class="greeting-card__left">
        <h1 class="greeting-card__hi">Hi, {{ authStore.user?.name || '用户' }}<span class="wave">👋</span></h1>
        <p class="greeting-card__sub">AI 外贸助手已就绪，助你高效开拓海外市场</p>
      </div>
      <div class="greeting-card__right">
        <div class="greeting-stat">
          <span class="greeting-stat__num">{{ stats.total_customers || 0 }}</span>
          <span class="greeting-stat__label">获取客户</span>
        </div>
        <div class="greeting-stat">
          <span class="greeting-stat__num">{{ stats.completed_icps || 0 }}</span>
          <span class="greeting-stat__label">客户画像</span>
        </div>
        <div class="greeting-stat">
          <span class="greeting-stat__num">{{ stats.total_emails_sent || 0 }}</span>
          <span class="greeting-stat__label">已发邮件</span>
        </div>
      </div>
    </div>

    <!-- ═══ 快捷入口（4 卡片，仅图标+标题） ═══ -->
    <div class="quick-row">
      <div class="quick-card" @click="$router.push('/app/customers')">
        <div class="quick-card__icon qci--gradient">
          <el-icon :size="18"><MagicStick /></el-icon>
        </div>
        <span class="quick-card__label">AI 全渠道获客</span>
      </div>
      <div class="quick-card" @click="$router.push('/app/icps')">
        <div class="quick-card__icon qci--blue">
          <el-icon :size="18"><PictureFilled /></el-icon>
        </div>
        <span class="quick-card__label">客户画像</span>
      </div>
      <div class="quick-card" @click="$router.push('/app/enterprise')">
        <div class="quick-card__icon qci--green">
          <el-icon :size="18"><OfficeBuilding /></el-icon>
        </div>
        <span class="quick-card__label">企业资料</span>
      </div>
      <div class="quick-card" @click="$router.push('/app/email')">
        <div class="quick-card__icon qci--purple">
          <el-icon :size="18"><Message /></el-icon>
        </div>
        <span class="quick-card__label">邮件营销</span>
      </div>
    </div>

    <!-- ═══ 双栏主体 ═══ -->
    <div class="main-two-col">
      <!-- 左栏：最新动态 -->
      <div class="panel panel--activity">
        <div class="panel__head">
          <h3 class="panel__title">最新动态</h3>
          <a class="panel__more" href="javascript:void(0)">更多 →</a>
        </div>
        <div class="panel__body">
          <template v-if="activities.length > 0">
            <div v-for="item in activities" :key="item.id" class="feed-item">
              <span class="feed-dot" :class="'dot--' + item.type"></span>
              <div class="feed-body">
                <span class="feed-title">{{ item.title }}</span>
                <span class="feed-desc">{{ item.desc }}</span>
              </div>
              <span class="feed-time">{{ item.time }}</span>
            </div>
          </template>
          <div v-else class="feed-empty">暂无动态，完善企业资料后开始 AI 获客</div>
        </div>
      </div>

      <!-- 右栏：日历 + 任务 -->
      <div class="right-col">
        <!-- 迷你日历 -->
        <div class="panel panel--calendar">
          <div class="panel__head">
            <h3 class="panel__title">{{ calendarYear }} 年 {{ calendarMonth }} 月</h3>
            <div class="cal-nav">
              <button class="cal-nav__btn" @click="prevMonth">&lt;</button>
              <button class="cal-nav__btn" @click="nextMonth">&gt;</button>
            </div>
          </div>
          <div class="panel__body cal-body">
            <div class="cal-weekdays">
              <span v-for="d in weekLabels" :key="d" class="cal-wd">{{ d }}</span>
            </div>
            <div class="cal-grid">
              <span
                v-for="(d, i) in calendarDays"
                :key="i"
                class="cal-day"
                :class="{
                  'cal-day--other': !d.current,
                  'cal-day--today': d.isToday,
                  'cal-day--active': d.isActive,
                }"
              >{{ d.day }}</span>
            </div>
          </div>
        </div>

        <!-- 任务列表 -->
        <div class="panel panel--tasks">
          <div class="panel__head">
            <h3 class="panel__title">任务列表</h3>
            <span class="task-count">{{ doneCount }}/{{ taskItems.length }}</span>
          </div>
          <div class="panel__body task-list">
            <div
              v-for="t in taskItems"
              :key="t.key"
              class="task-item"
              :class="{ 'task-item--done': t.done }"
              @click="t.done = !t.done"
            >
              <span class="task-check" :class="{ checked: t.done }">
                <el-icon v-if="t.done" :size="12"><Check /></el-icon>
              </span>
              <span class="task-text">{{ t.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { OfficeBuilding, PictureFilled, Message, MagicStick, Check } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const authStore = useAuthStore()

// ── 数据 ──
interface DashboardStats {
  total_icps: number; completed_icps: number
  total_customers: number; customers_reached: number; reach_rate: number
  total_emails_sent: number; reply_rate: number
}
const stats = ref<DashboardStats>({
  total_icps: 0, completed_icps: 0,
  total_customers: 0, customers_reached: 0, reach_rate: 0,
  total_emails_sent: 0, reply_rate: 0,
})

// ── 活动动态 ──
interface Activity { id: string; type: string; title: string; desc: string; time: string }
const activities = ref<Activity[]>([])

function buildActivities(s: DashboardStats) {
  const a: Activity[] = []
  if (s.total_customers > 0) a.push({ id: '1', type: 'customer', title: '客户获取', desc: `已获取 ${s.total_customers} 个潜在客户`, time: '刚刚' })
  if (s.completed_icps > 0) a.push({ id: '2', type: 'icp', title: '客户画像', desc: `${s.completed_icps} 个画像已完成生成`, time: '刚刚' })
  if (s.total_emails_sent > 0) a.push({ id: '3', type: 'email', title: '邮件营销', desc: `累计发送 ${s.total_emails_sent} 封营销邮件`, time: '刚刚' })
  if (s.total_customers > 0 && s.customers_reached > 0) a.push({ id: '4', type: 'reach', title: '客户触达', desc: `已触达 ${s.customers_reached} 个客户，触达率 ${(s.reach_rate * 100).toFixed(0)}%`, time: '刚刚' })
  if (a.length === 0) a.push({ id: '0', type: 'welcome', title: '欢迎使用 AI 外贸助手', desc: '完善企业资料后开始 AI 智能获客', time: '现在' })
  activities.value = a
}

// ── 企业状态 ──
const enterpriseDone = ref(false)

// ── 任务列表 ──
const taskItems = reactive([
  { key: 'enterprise', label: '完善企业资料与产品信息', done: false },
  { key: 'icp',       label: '生成目标客户画像',       done: false },
  { key: 'customer',  label: 'AI 全渠道搜索客户',      done: false },
  { key: 'email',     label: '创建邮件模板并发送营销',  done: false },
])
const doneCount = computed(() => taskItems.filter(t => t.done).length)

function syncTasks() {
  taskItems[0].done = enterpriseDone.value
  taskItems[1].done = stats.value.completed_icps > 0
  taskItems[2].done = stats.value.total_customers > 0
  taskItems[3].done = stats.value.total_emails_sent > 0
}

// ── 迷你日历 ──
const now = new Date()
const calendarYear = ref(now.getFullYear())
const calendarMonth = ref(now.getMonth() + 1) // 1-based
const weekLabels = ['一', '二', '三', '四', '五', '六', '日']

interface CalDay { day: number; current: boolean; isToday: boolean; isActive: boolean }
const calendarDays = computed<CalDay[]>(() => {
  const y = calendarYear.value
  const m = calendarMonth.value - 1 // Date month is 0-based
  const firstDay = new Date(y, m, 1)
  const startDayOfWeek = firstDay.getDay() || 7 // Mon=1 ... Sun=7
  const daysInMonth = new Date(y, m + 1, 0).getDate()
  const daysInPrev = new Date(y, m, 0).getDate()

  const today = new Date()
  const todayY = today.getFullYear()
  const todayM = today.getMonth()
  const todayD = today.getDate()

  const result: CalDay[] = []

  // 上月填充
  for (let i = startDayOfWeek - 1; i > 0; i--) {
    const d = daysInPrev - i + 1
    result.push({ day: d, current: false, isToday: false, isActive: false })
  }

  // 当月
  for (let d = 1; d <= daysInMonth; d++) {
    result.push({
      day: d,
      current: true,
      isToday: y === todayY && m === todayM && d === todayD,
      isActive: false, // 后续可接真实活动日期
    })
  }

  // 下月填充
  const remaining = 7 - (result.length % 7)
  if (remaining < 7) {
    for (let d = 1; d <= remaining; d++) {
      result.push({ day: d, current: false, isToday: false, isActive: false })
    }
  }

  return result
})

function prevMonth() {
  if (calendarMonth.value === 1) { calendarMonth.value = 12; calendarYear.value-- }
  else calendarMonth.value--
}
function nextMonth() {
  if (calendarMonth.value === 12) { calendarMonth.value = 1; calendarYear.value++ }
  else calendarMonth.value++
}

// ── 加载 ──
async function loadStats() {
  try {
    const { data } = await api.get('/dashboard/stats', { silent: true })
    stats.value = { ...stats.value, ...data }
  } catch { /* */ }
  buildActivities(stats.value)
  syncTasks()
}
async function loadEnterprise() {
  try { await api.get('/enterprise', { silent: true }); enterpriseDone.value = true } catch { /* */ }
  syncTasks()
}

onMounted(async () => {
  await Promise.all([loadStats(), loadEnterprise()])
})
</script>

<style scoped lang="scss">
// ══════════════════════════════════════════
// 设计参考 /docs/UI/工作台.png
// 风格：浅灰背景 + 白色卡片 + 极淡投影
// ══════════════════════════════════════════

$bg:        #f5f6f8;
$card-bg:   #fff;
$border:    #eaecef;
$shadow:    0 1px 2px rgba(0,0,0,.04);
$shadow-hv: 0 4px 12px rgba(0,0,0,.06);
$radius:    14px;
$text-1:    #1a1a2e;
$text-2:    #5a5f6e;
$text-3:    #949aab;

.dashboard-preview {
  max-width: 1100px;
  margin: 0 auto;
}

// ── 问候卡片（白底，参考图无暗色横幅） ──
.greeting-card {
  background: $card-bg;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow;
  padding: 24px 32px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &__left {
    h1 { margin: 0 0 4px; font-size: 20px; font-weight: 700; color: $text-1; }
    .wave { display: inline-block; animation: wave 2s ease-in-out infinite; transform-origin: 70% 70%; }
  }
  &__sub { margin: 0; font-size: 13px; color: $text-3; }

  &__right { display: flex; gap: 36px; }
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  75% { transform: rotate(-8deg); }
}

.greeting-stat {
  text-align: center;
  &__num   { display: block; font-size: 22px; font-weight: 700; color: $text-1; }
  &__label { font-size: 11px; color: $text-3; margin-top: 1px; }
}

// ── 快捷入口（4 卡片横排，仅图标+标题） ──
.quick-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}

.quick-card {
  background: $card-bg;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow;
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all .18s;
  &:hover { border-color: #3b82f6; box-shadow: $shadow-hv; }

  &__icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  &__label { font-size: 13px; font-weight: 600; color: $text-1; white-space: nowrap; }
}

.qci--gradient { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.qci--blue     { background: #eef2ff; color: #4f6ef7; }
.qci--green    { background: #eafaf1; color: #22c55e; }
.qci--purple   { background: #f3f0ff; color: #7c3aed; }

// ── 双栏 ──
.main-two-col {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 18px;
  align-items: start;
}

// ── 通用面板 ──
.panel {
  background: $card-bg;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow;

  &__head {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 22px 0;
    margin-bottom: 10px;
  }
  &__title { margin: 0; font-size: 14px; font-weight: 700; color: $text-1; }
  &__more  { font-size: 12px; color: $text-3; text-decoration: none; &:hover { color: #3b82f6; } }
  &__body { padding: 0 22px 18px; }
}

// ── 动态列表 ──
.feed-item {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 13px 0;
  border-bottom: 1px solid #f2f3f5;
  &:last-child { border-bottom: none; }
}

.feed-dot {
  width: 7px; height: 7px; border-radius: 50%;
  margin-top: 5px; flex-shrink: 0;
  &.dot--customer { background: #3b82f6; }
  &.dot--icp      { background: #22c55e; }
  &.dot--email    { background: #7c3aed; }
  &.dot--reach    { background: #f59e0b; }
  &.dot--welcome  { background: #c0c7d0; }
}

.feed-body {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; gap: 1px;
}
.feed-title { font-size: 13px; font-weight: 600; color: $text-1; }
.feed-desc  { font-size: 12px; color: $text-3; line-height: 1.4; }
.feed-time  { font-size: 11px; color: $text-3; flex-shrink: 0; margin-top: 2px; }
.feed-empty { padding: 28px 0; text-align: center; font-size: 13px; color: $text-3; }

// ── 右栏 ──
.right-col { display: flex; flex-direction: column; gap: 18px; }

// ── 日历 ──
.cal-nav {
  display: flex; gap: 4px;
  &__btn {
    width: 24px; height: 24px; border: 1px solid $border; border-radius: 6px;
    background: #fff; font-size: 12px; color: $text-2; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    &:hover { border-color: #3b82f6; color: #3b82f6; }
  }
}

.cal-body { padding-bottom: 16px !important; }

.cal-weekdays {
  display: grid; grid-template-columns: repeat(7, 1fr);
  margin-bottom: 6px;
}
.cal-wd { text-align: center; font-size: 11px; color: $text-3; padding: 4px 0; }

.cal-grid {
  display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px;
}
.cal-day {
  text-align: center; font-size: 12px; color: $text-1;
  padding: 5px 0; border-radius: 6px; cursor: default;
  &--other { color: #d0d4dd; }
  &--today { background: #3b82f6; color: #fff; font-weight: 600; }
  &--active { background: #eef2ff; color: #3b82f6; font-weight: 600; }
}

// ── 任务列表 ──
.task-count { font-size: 12px; color: $text-3; }

.task-list { display: flex; flex-direction: column; gap: 2px; }

.task-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 10px; border-radius: 8px;
  cursor: pointer; transition: background .15s;
  font-size: 13px; color: $text-1;
  &:hover { background: #f8f9fb; }

  &--done {
    .task-text { color: $text-3; text-decoration: line-through; }
  }
}

.task-check {
  width: 18px; height: 18px; border-radius: 5px;
  border: 1.5px solid #d0d4dd;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  &.checked { background: #22c55e; border-color: #22c55e; color: #fff; }
}

.task-text { flex: 1; }
</style>
