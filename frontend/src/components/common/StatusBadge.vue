<template>
  <el-tag :type="tagType" :size="size" :effect="effect" round>
    {{ label }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from "vue";

const STATUS_MAP: Record<string, { type: "success" | "info" | "warning" | "danger"; label: string }> = {
  // 通用
  active: { type: "success", label: "启用" },
  inactive: { type: "info", label: "禁用" },
  enabled: { type: "success", label: "已启用" },
  disabled: { type: "info", label: "已禁用" },
  // 租户/企业
  pending: { type: "warning", label: "待审核" },
  suspended: { type: "danger", label: "已停用" },
  // Plan
  free: { type: "info", label: "免费版" },
  pro: { type: "warning", label: "专业版" },
  enterprise: { type: "success", label: "企业版" },
  // ICP
  draft: { type: "info", label: "草稿" },
  generating: { type: "warning", label: "生成中" },
  completed: { type: "success", label: "已完成" },
  // 客户状态
  new: { type: "info", label: "新客户" },
  contacted: { type: "warning", label: "已联系" },
  qualified: { type: "success", label: "已确认意向" },
  negotiating: { type: "warning", label: "洽谈中" },
  closed: { type: "success", label: "已成交" },
  rejected: { type: "danger", label: "已拒绝" },
  // 客户来源
  manual: { type: "info", label: "手动添加" },
  ai_extraction: { type: "success", label: "AI 提取" },
  import: { type: "warning", label: "批量导入" },
  ai_search: { type: "success", label: "AI 搜索" },
  google_search: { type: "", label: "Google 搜索" },
  linkedin_search: { type: "", label: "LinkedIn 搜索" },
  duckduckgo_search: { type: "", label: "DuckDuckGo 搜索" },
  // 邮件
  sending: { type: "warning", label: "发送中" },
  sent: { type: "success", label: "已发送" },
  failed: { type: "danger", label: "失败" },
  cancelled: { type: "info", label: "已取消" },
};

const props = withDefaults(
  defineProps<{
    status: string;
    size?: "small" | "default" | "large";
    effect?: "dark" | "light" | "plain";
  }>(),
  {
    size: "small",
    effect: "light",
  }
);

const tagType = computed(() => STATUS_MAP[props.status]?.type ?? "info");
const label = computed(() => STATUS_MAP[props.status]?.label ?? props.status);
</script>
