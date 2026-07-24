<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:visible', $event)"
    @close="$emit('cancel')"
  >
    <p class="confirm-dialog__body">{{ message }}</p>
    <template #footer>
      <el-button @click="$emit('cancel'); $emit('update:visible', false)">取消</el-button>
      <el-button :type="confirmType" :loading="loading" @click="$emit('confirm')">
        {{ confirmText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineEmits<{
  confirm: [];
  cancel: [];
  "update:visible": [value: boolean];
}>();

withDefaults(defineProps<{
  visible: boolean;
  title?: string;
  message?: string;
  confirmText?: string;
  confirmType?: "primary" | "danger" | "warning";
  loading?: boolean;
  width?: string;
}>(), {
  title: "确认操作",
  message: "确定要执行此操作吗？",
  confirmText: "确定",
  confirmType: "primary",
  loading: false,
  width: "420px",
});
</script>

<style scoped lang="scss">
.confirm-dialog__body {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}
</style>
