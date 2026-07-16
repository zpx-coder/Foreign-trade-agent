<template>
  <div class="page-header">
    <div class="page-header__left">
      <h2 class="page-header__title">{{ title }}</h2>
      <el-breadcrumb v-if="breadcrumb.length" separator="/">
        <el-breadcrumb-item v-for="item in breadcrumb" :key="item.path || item.title" :to="item.path ? { path: item.path } : undefined">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface BreadcrumbItem {
  title: string;
  path?: string;
}

withDefaults(defineProps<{
  title: string;
  breadcrumb?: BreadcrumbItem[];
}>(), {
  breadcrumb: () => [],
});
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;

  &__title {
    margin: 0 0 6px 0;
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.3px;
  }

  &__actions {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
  }
}
</style>
