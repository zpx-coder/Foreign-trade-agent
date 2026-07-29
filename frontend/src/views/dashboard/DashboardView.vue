<template>
  <div class="dashboard-page">
    <!-- 背景装饰 -->
    <div class="bg-decor">
      <div class="bg-decor__orb bg-decor__orb--1"></div>
      <div class="bg-decor__orb bg-decor__orb--2"></div>
      <div class="bg-decor__orb bg-decor__orb--3"></div>
      <div class="bg-decor__grid"></div>
    </div>

    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-banner__content">
        <div class="welcome-banner__greeting">
          <span class="welcome-banner__date">{{ todayStr }}</span>
          <h1>你好，{{ authStore.user?.name || "用户" }}<span class="wave">👋</span></h1>
          <p>AI 外贸助手已就绪，助你高效开拓海外市场</p>
        </div>
        <div class="welcome-banner__stats">
          <div class="welcome-stat">
            <div class="welcome-stat__icon" style="background:rgba(59,130,246,.2);color:#60a5fa;">
              <el-icon :size="16"><UserFilled /></el-icon>
            </div>
            <div class="welcome-stat__info">
              <span class="welcome-stat__num">{{ stats.total_customers || 0 }}</span>
              <span class="welcome-stat__label">获取客户</span>
            </div>
          </div>
          <div class="welcome-stat">
            <div class="welcome-stat__icon" style="background:rgba(16,185,129,.2);color:#34d399;">
              <el-icon :size="16"><PictureFilled /></el-icon>
            </div>
            <div class="welcome-stat__info">
              <span class="welcome-stat__num">{{ stats.total_icps || 0 }}</span>
              <span class="welcome-stat__label">客户画像</span>
            </div>
          </div>
          <div class="welcome-stat">
            <div class="welcome-stat__icon" style="background:rgba(139,92,246,.2);color:#a78bfa;">
              <el-icon :size="16"><Message /></el-icon>
            </div>
            <div class="welcome-stat__info">
              <span class="welcome-stat__num">{{ stats.total_emails_sent || 0 }}</span>
              <span class="welcome-stat__label">已发邮件</span>
            </div>
          </div>
        </div>
      </div>
      <div class="welcome-banner__illustration">
        <svg viewBox="0 0 280 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- 地球 -->
          <circle cx="200" cy="100" r="55" stroke="rgba(255,255,255,.1)" stroke-width="1.5"/>
          <ellipse cx="200" cy="100" rx="28" ry="55" stroke="rgba(255,255,255,.08)" stroke-width="1"/>
          <line x1="145" y1="100" x2="255" y2="100" stroke="rgba(255,255,255,.08)" stroke-width="1"/>
          <path d="M160 70 Q200 55 240 70" stroke="rgba(255,255,255,.06)" stroke-width="1" fill="none"/>
          <path d="M160 130 Q200 145 240 130" stroke="rgba(255,255,255,.06)" stroke-width="1" fill="none"/>
          <!-- 节点和连线 -->
          <circle cx="200" cy="45" r="3" fill="#60a5fa" opacity=".8"><animate attributeName="opacity" values=".4;.8;.4" dur="3s" repeatCount="indefinite"/></circle>
          <line x1="200" y1="45" x2="200" y2="70" stroke="rgba(96,165,250,.2)" stroke-width="1" stroke-dasharray="3 3"/>
          <circle cx="155" cy="85" r="2.5" fill="#34d399" opacity=".7"><animate attributeName="opacity" values=".3;.7;.3" dur="2.5s" repeatCount="indefinite"/></circle>
          <line x1="155" y1="85" x2="175" y2="95" stroke="rgba(52,211,153,.15)" stroke-width="1"/>
          <circle cx="245" cy="115" r="2.5" fill="#a78bfa" opacity=".7"><animate attributeName="opacity" values=".3;.7;.3" dur="3.5s" repeatCount="indefinite"/></circle>
          <line x1="245" y1="115" x2="225" y2="105" stroke="rgba(167,139,250,.15)" stroke-width="1"/>
          <circle cx="170" cy="145" r="2" fill="#fbbf24" opacity=".6"><animate attributeName="opacity" values=".2;.6;.2" dur="4s" repeatCount="indefinite"/></circle>
          <line x1="170" y1="145" x2="190" y2="125" stroke="rgba(251,191,36,.12)" stroke-width="1"/>
          <!-- 飞机轨迹 -->
          <path d="M60 120 Q130 80 200 45" stroke="rgba(255,255,255,.08)" stroke-width="1" stroke-dasharray="6 4" fill="none"/>
          <circle cx="85" cy="105" r="4" fill="rgba(255,255,255,.15)"/>
        </svg>
      </div>
    </div>

    <!-- 快捷入口 — 大卡片 -->
    <div class="quick-grid">
      <div class="quick-card quick-card--blue" @click="$router.push('/app/enterprise')">
        <div class="quick-card__illustration">
          <svg viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="20" width="40" height="50" rx="4" stroke="rgba(59,130,246,.3)" stroke-width="1.5" fill="rgba(59,130,246,.06)"/>
            <rect x="18" y="28" width="24" height="6" rx="2" fill="rgba(59,130,246,.2)"/>
            <rect x="18" y="38" width="16" height="4" rx="2" fill="rgba(59,130,246,.12)"/>
            <rect x="18" y="46" width="20" height="4" rx="2" fill="rgba(59,130,246,.12)"/>
            <rect x="55" y="30" width="40" height="14" rx="3" stroke="rgba(59,130,246,.25)" stroke-width="1.2" fill="rgba(59,130,246,.04)"/>
            <rect x="55" y="48" width="40" height="10" rx="3" stroke="rgba(59,130,246,.2)" stroke-width="1.2" fill="rgba(59,130,246,.03)"/>
            <rect x="70" y="55" width="5" height="8" rx="1.5" fill="rgba(16,185,129,.3)"/>
          </svg>
        </div>
        <div class="quick-card__body">
          <h4>企业资料 &amp; 产品</h4>
          <p>完善公司信息与出口产品，AI 基于此精准匹配客户</p>
        </div>
        <div class="quick-card__footer">
          <span class="quick-card__step">步骤 1</span>
          <el-icon :size="18" class="quick-card__arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="quick-card quick-card--green" @click="$router.push('/app/icps')">
        <div class="quick-card__illustration">
          <svg viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="35" r="20" stroke="rgba(16,185,129,.25)" stroke-width="1.5" fill="rgba(16,185,129,.04)"/>
            <circle cx="40" cy="28" r="6" fill="rgba(16,185,129,.15)"/>
            <line x1="40" y1="34" x2="40" y2="48" stroke="rgba(16,185,129,.2)" stroke-width="2" stroke-linecap="round"/>
            <line x1="40" y1="42" x2="33" y2="38" stroke="rgba(16,185,129,.2)" stroke-width="2" stroke-linecap="round"/>
            <line x1="40" y1="42" x2="47" y2="38" stroke="rgba(16,185,129,.2)" stroke-width="2" stroke-linecap="round"/>
            <rect x="72" y="22" width="36" height="8" rx="2" fill="rgba(16,185,129,.12)"/>
            <rect x="72" y="34" width="28" height="6" rx="2" fill="rgba(16,185,129,.08)"/>
            <rect x="72" y="44" width="32" height="6" rx="2" fill="rgba(16,185,129,.08)"/>
            <circle cx="78" cy="26" r="1.5" fill="rgba(16,185,129,.4)"/>
            <circle cx="78" cy="37" r="1.5" fill="rgba(16,185,129,.3)"/>
            <circle cx="78" cy="47" r="1.5" fill="rgba(16,185,129,.3)"/>
          </svg>
        </div>
        <div class="quick-card__body">
          <h4>客户画像<span class="badge-ai">AI</span></h4>
          <p>智能分析生成理想客户画像，锁定精准目标市场与决策人</p>
        </div>
        <div class="quick-card__footer">
          <span class="quick-card__step">步骤 2</span>
          <el-icon :size="18" class="quick-card__arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="quick-card quick-card--amber" @click="$router.push('/app/customers')">
        <div class="quick-card__illustration">
          <svg viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 放大镜 -->
            <circle cx="38" cy="35" r="16" stroke="rgba(245,158,11,.3)" stroke-width="1.5" fill="rgba(245,158,11,.05)"/>
            <line x1="50" y1="47" x2="60" y2="57" stroke="rgba(245,158,11,.25)" stroke-width="2.5" stroke-linecap="round"/>
            <!-- 搜索结果 -->
            <rect x="68" y="20" width="40" height="8" rx="2" fill="rgba(245,158,11,.15)"/>
            <rect x="68" y="32" width="34" height="8" rx="2" fill="rgba(245,158,11,.1)"/>
            <rect x="68" y="44" width="38" height="8" rx="2" fill="rgba(245,158,11,.07)"/>
          </svg>
        </div>
        <div class="quick-card__body">
          <h4>AI 全渠道获客</h4>
          <p>多渠道路径搜索海外客户，AI 自动聚合去重与智能补全</p>
        </div>
        <div class="quick-card__footer">
          <span class="quick-card__step">步骤 3</span>
          <el-icon :size="18" class="quick-card__arrow"><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="quick-card quick-card--purple" @click="$router.push('/app/email/templates')">
        <div class="quick-card__illustration">
          <svg viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- 信封 -->
            <rect x="15" y="22" width="70" height="46" rx="4" stroke="rgba(139,92,246,.25)" stroke-width="1.5" fill="rgba(139,92,246,.04)"/>
            <path d="M15 22 L50 48 L85 22" stroke="rgba(139,92,246,.2)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="30" y1="38" x2="55" y2="38" stroke="rgba(139,92,246,.12)" stroke-width="2" stroke-linecap="round"/>
            <line x1="30" y1="46" x2="65" y2="46" stroke="rgba(139,92,246,.08)" stroke-width="2" stroke-linecap="round"/>
            <!-- 发送箭头 -->
            <circle cx="100" cy="28" r="10" stroke="rgba(16,185,129,.3)" stroke-width="1.2" fill="rgba(16,185,129,.08)"/>
            <path d="M96 28 L104 28 M101 25 L104 28 L101 31" stroke="rgba(16,185,129,.4)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="quick-card__body">
          <h4>邮件营销</h4>
          <p>AI 生成多语种开发信，一键批量发送与追踪转化效果</p>
        </div>
        <div class="quick-card__footer">
          <span class="quick-card__step">步骤 4</span>
          <el-icon :size="18" class="quick-card__arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 设置进度 -->
    <el-card class="setup-card">
      <div class="setup-card__inner">
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
              <span v-else class="step-desc todo">AI 全渠道搜索客户</span>
            </template>
          </el-step>
          <el-step title="邮件营销">
            <template #description>
              <span v-if="stats.total_emails_sent > 0" class="step-desc done">已发送 {{ stats.total_emails_sent }} 封邮件</span>
              <span v-else class="step-desc todo">创建邮件模板并发送</span>
            </template>
          </el-step>
        </el-steps>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { OfficeBuilding, PictureFilled, Search, ArrowRight, UserFilled, Message } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/api/client";

const authStore = useAuthStore();

// ── 今天日期 ──
const todayStr = computed(() => {
  const d = new Date();
  const weekNames = ["日", "一", "二", "三", "四", "五", "六"];
  return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日 · 星期${weekNames[d.getDay()]}`;
});

// ── 基础状态 ──
const enterpriseDone = ref(false);
const setupStep = ref(1);

interface DashboardStats {
  total_icps: number;
  completed_icps: number;
  total_customers: number;
  total_emails_sent: number;
}

const stats = ref<DashboardStats>({
  total_icps: 0, completed_icps: 0,
  total_customers: 0, total_emails_sent: 0,
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
    stats.value = {
      total_icps: data.total_icps || 0,
      completed_icps: data.completed_icps || 0,
      total_customers: data.total_customers || 0,
      total_emails_sent: data.total_emails_sent || 0,
    };
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

onMounted(async () => {
  await Promise.all([loadStats(), loadEnterpriseStatus()]);
});
</script>

<style scoped lang="scss">
// ═══════════════════════════════════════════
// 背景装饰
// ═══════════════════════════════════════════
.dashboard-page {
  position: relative;
  min-height: 100%;
  padding: 28px 32px 40px;
  overflow: hidden;
}

.bg-decor {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;

  &__orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: .35;
    &--1 { width: 360px; height: 360px; background: rgba(59,130,246,.12); top: -100px; right: -80px; }
    &--2 { width: 280px; height: 280px; background: rgba(16,185,129,.08); bottom: -60px; left: -60px; }
    &--3 { width: 200px; height: 200px; background: rgba(139,92,246,.07); top: 40%; left: 50%; }
  }

  &__grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(59,130,246,.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(59,130,246,.03) 1px, transparent 1px);
    background-size: 60px 60px;
    mask-image: radial-gradient(ellipse 80% 60% at 50% 30%, black 20%, transparent 70%);
  }
}

// ═══════════════════════════════════════════
// 欢迎横幅
// ═══════════════════════════════════════════
.welcome-banner {
  position: relative;
  z-index: 1;
  background: linear-gradient(135deg, #0c1929 0%, #152238 30%, #1a3350 60%, #1d4ed8 100%);
  border-radius: 20px;
  padding: 40px 48px;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;

  &__content {
    position: relative;
    z-index: 1;
    flex: 1;
  }

  &__greeting {
    margin-bottom: 28px;
    h1 { margin: 4px 0 6px; font-size: 26px; font-weight: 700; color: #fff; letter-spacing: -.3px; }
    .wave { display: inline-block; animation: wave 2s ease-in-out infinite; transform-origin: 70% 70%; }
    p { margin: 0; font-size: 14px; color: rgba(255,255,255,.55); }
  }

  &__date {
    font-size: 12px;
    color: rgba(255,255,255,.35);
    background: rgba(255,255,255,.06);
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,.08);
    display: inline-block;
  }

  &__stats {
    display: flex;
    gap: 20px;
  }

  &__illustration {
    position: relative;
    z-index: 1;
    width: 280px;
    flex-shrink: 0;
    svg { width: 280px; height: 200px; }
  }
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  75% { transform: rotate(-8deg); }
}

.welcome-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 12px;
  padding: 12px 18px;
  min-width: 140px;

  &__icon {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &__info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  &__num { font-size: 22px; font-weight: 800; color: #fff; line-height: 1.1; }
  &__label { font-size: 11px; color: rgba(255,255,255,.45); }
}

// ═══════════════════════════════════════════
// 快捷入口 — 大卡片
// ═══════════════════════════════════════════
.quick-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 28px;
}

.quick-card {
  position: relative;
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 18px;
  padding: 28px 28px 20px;
  cursor: pointer;
  transition: all .25s;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;

  // 顶部色条
  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
  }

  &--blue::before  { background: linear-gradient(90deg, #3b82f6, #6366f1); }
  &--green::before { background: linear-gradient(90deg, #10b981, #34d399); }
  &--amber::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
  &--purple::before { background: linear-gradient(90deg, #7c3aed, #a78bfa); }

  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 8px 32px rgba(59,130,246,.1);
    transform: translateY(-3px);

    .quick-card__arrow { opacity: 1; transform: translateX(0); color: #3b82f6; }
    .quick-card__illustration svg { transform: scale(1.03); }
  }

  &__illustration {
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8fafc;
    border-radius: 12px;
    border: 1px solid #f1f5f9;

    svg {
      width: 120px;
      height: 80px;
      transition: transform .3s;
    }
  }

  &__body {
    flex: 1;
    h4 { margin: 0 0 6px; font-size: 16px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; }
    p { margin: 0; font-size: 13px; color: #64748b; line-height: 1.5; }
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__step {
    font-size: 11px;
    color: #94a3b8;
    background: #f1f5f9;
    padding: 3px 10px;
    border-radius: 6px;
    border: 1px solid #e8ecf1;
  }

  &__arrow {
    color: #cbd5e1;
    opacity: 0;
    transform: translateX(-4px);
    transition: all .2s;
  }
}

.badge-ai {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  padding: 1px 7px;
  border-radius: 4px;
}

// ═══════════════════════════════════════════
// 设置进度
// ═══════════════════════════════════════════
.setup-card {
  position: relative;
  z-index: 1;
  border-radius: 18px;
  border: 1px solid #e8ecf1;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
  background: #fff;

  :deep(.el-card__body) { padding: 28px 36px 32px; }
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;

  &__title { margin: 0; font-size: 16px; font-weight: 700; color: #0f172a; }
  &__hint { font-size: 12px; color: #94a3b8; }
}

.setup-steps {
  :deep(.el-step__head.is-success) { color: #10b981; border-color: #10b981; }
  :deep(.el-step__head.is-process) { color: #3b82f6; border-color: #3b82f6; }
  :deep(.el-step__title) { font-size: 14px; font-weight: 600; }
  :deep(.el-step__description) { margin-top: 4px; }
  :deep(.el-step__line) { background: #e8ecf1; }
}

.step-desc { font-size: 12px; &.done { color: #10b981; } &.todo { color: #64748b; } }
</style>
