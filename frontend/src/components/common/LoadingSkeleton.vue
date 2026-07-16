<template>
  <div class="loading-skeleton">
    <el-skeleton v-if="variant === 'card' || variant === 'detail'" :loading="true" animated :rows="1" />
    <template v-if="variant === 'form' || variant === 'detail'">
      <div class="loading-skeleton__form">
        <el-skeleton :loading="true" animated :rows="1" style="width: 30%; margin-bottom: 24px" />
        <el-skeleton v-for="i in 4" :key="i" :loading="true" animated :rows="1" style="margin-bottom: 20px" />
      </div>
    </template>
    <template v-if="variant === 'table' || variant === 'card'">
      <div class="loading-skeleton__toolbar">
        <el-skeleton :loading="true" animated :rows="1" style="width: 200px" />
      </div>
      <el-skeleton v-for="i in rows" :key="i" :loading="true" animated :rows="1" style="margin-bottom: 12px" />
    </template>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: "card" | "table" | "form" | "detail";
  rows?: number;
}>(), {
  variant: "card",
  rows: 5,
});
</script>

<style scoped lang="scss">
.loading-skeleton {
  padding: 20px;

  &__form {
    margin-top: 20px;
  }

  &__toolbar {
    margin-bottom: 20px;
  }
}
</style>
