<template>
  <div class="streaming-output">
    <!-- 生成中动画 -->
    <div v-if="isStreaming" class="generating-panel">
      <!-- 脉冲环 -->
      <div class="pulse-ring">
        <div class="pulse-ring__core" />
        <div class="pulse-ring__wave wave-1" />
        <div class="pulse-ring__wave wave-2" />
      </div>

      <p class="gen-status-text">{{ thinkingText }}</p>

      <!-- 进度条 -->
      <div class="gen-progress-bar">
        <div class="gen-progress-bar__track" />
        <div class="gen-progress-bar__fill" :style="{ width: progressPercent + '%' }" />
      </div>

      <!-- 步骤列表 -->
      <div class="gen-sections">
        <div
          v-for="s in sectionList"
          :key="s.key"
          class="gen-section"
          :class="{ active: s.key === currentSection, done: completedSections.has(s.key) }"
        >
          <div class="gen-section__dot">
            <el-icon v-if="completedSections.has(s.key)" class="icon-done"><CircleCheckFilled /></el-icon>
            <span v-else-if="s.key === currentSection" class="icon-active" />
            <span v-else class="icon-pending" />
          </div>
          <span class="gen-section__label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <!-- 完成状态 -->
    <div v-if="done" class="done-panel">
      <div class="done-icon-wrap">
        <svg class="done-check" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="30" stroke="#10b981" stroke-width="3" fill="none" class="done-circle" />
          <path d="M20 32l8 8 16-16" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" class="done-path" />
        </svg>
      </div>
      <p class="done-text">画像生成完成</p>
      <slot name="done" />
    </div>

    <!-- 错误 -->
    <div v-if="error" class="streaming-error">
      <el-alert :title="error" type="error" show-icon :closable="false" />
    </div>

    <!-- 内容区（仅在完成后展示） -->
    <div v-if="done" class="streaming-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { CircleCheckFilled } from "@element-plus/icons-vue";

const props = defineProps<{
  isStreaming: boolean;
  currentSection: string | null;
  error: string | null;
  done?: boolean;
}>();

const sectionList = [
  { key: "summary", label: "生成画像摘要" },
  { key: "target_market", label: "分析目标市场" },
  { key: "customer_persona", label: "构建客户画像" },
  { key: "competitive_advantages", label: "梳理竞争优势" },
  { key: "recommended_approach", label: "生成推荐策略" },
];

const completedSections = computed(() => {
  if (!props.currentSection) return new Set<string>();
  const idx = sectionList.findIndex((s) => s.key === props.currentSection);
  return new Set(sectionList.slice(0, idx).map((s) => s.key));
});

const progressPercent = computed(() => {
  if (!props.currentSection) return 8;
  const idx = sectionList.findIndex((s) => s.key === props.currentSection);
  return Math.min(Math.round(((idx + 1) / sectionList.length) * 100), 92);
});

const THINKING_TEXTS = ["AI 正在分析输入信息...", "正在生成市场洞察...", "正在构建客户画像...", "正在优化策略建议...", "即将完成..."];
const thinkingText = computed(() => {
  if (!props.currentSection) return THINKING_TEXTS[0];
  const idx = sectionList.findIndex((s) => s.key === props.currentSection);
  return THINKING_TEXTS[Math.min(idx, THINKING_TEXTS.length - 1)];
});
</script>

<style scoped lang="scss">
.streaming-output {
  //
}

// ── 生成面板 ──
.generating-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0 24px;
}

// 脉冲环（中心动画）
.pulse-ring {
  position: relative;
  width: 64px;
  height: 64px;
  margin-bottom: 16px;

  &__core {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 14px;
    height: 14px;
    margin: -7px 0 0 -7px;
    border-radius: 50%;
    background: #2563eb;
    z-index: 2;
  }
  &__wave {
    position: absolute;
    top: 50%;
    left: 50%;
    border-radius: 50%;
    border: 2px solid #2563eb;
    animation: pulse-expand 2s ease-out infinite;

    &.wave-1 {
      width: 64px;
      height: 64px;
      margin: -32px 0 0 -32px;
    }
    &.wave-2 {
      width: 64px;
      height: 64px;
      margin: -32px 0 0 -32px;
      animation-delay: 1s;
    }
  }
}

@keyframes pulse-expand {
  0% {
    transform: scale(0.4);
    opacity: 0.6;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

.gen-status-text {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 20px 0;
}

// 进度条
.gen-progress-bar {
  width: 100%;
  max-width: 360px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin-bottom: 24px;
  overflow: hidden;
  position: relative;

  &__track {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.08), transparent);
    animation: shimmer 2s infinite;
  }
  &__fill {
    height: 100%;
    background: linear-gradient(90deg, #2563eb, #6366f1);
    border-radius: 2px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    z-index: 1;
  }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

// 步骤列表
.gen-sections {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 300px;
}

.gen-section {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s;

  &.done &__label { color: #64748b; }
  &.active &__label { color: #1e293b; font-weight: 500; }
  &:not(.done):not(.active) &__label { color: #cbd5e1; }

  &__dot {
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  &__label {
    font-size: 13px;
    transition: color 0.3s;
  }
}

.icon-done {
  color: #10b981;
  font-size: 16px;
}
.icon-active {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2563eb;
  box-shadow: 0 0 8px rgba(37, 99, 235, 0.5);
  animation: icon-pulse 1.5s ease-in-out infinite;
}
.icon-pending {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #cbd5e1;
}
@keyframes icon-pulse {
  0%, 100% { box-shadow: 0 0 4px rgba(37, 99, 235, 0.3); }
  50% { box-shadow: 0 0 12px rgba(37, 99, 235, 0.6); }
}

// ── 完成面板 ──
.done-panel {
  text-align: center;
  padding: 24px 0 8px;
}
.done-icon-wrap {
  margin-bottom: 12px;
}
.done-check {
  width: 64px;
  height: 64px;
}
.done-circle {
  stroke-dasharray: 188;
  stroke-dashoffset: 0;
  animation: circle-draw 0.6s ease-out;
}
.done-path {
  stroke-dasharray: 50;
  stroke-dashoffset: 0;
  animation: path-draw 0.4s ease-out 0.3s both;
}
@keyframes circle-draw {
  from { stroke-dashoffset: 188; }
  to { stroke-dashoffset: 0; }
}
@keyframes path-draw {
  from { stroke-dashoffset: 50; }
  to { stroke-dashoffset: 0; }
}
.done-text {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.streaming-content {
  margin-top: 16px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.streaming-error {
  margin-top: 16px;
}
</style>
