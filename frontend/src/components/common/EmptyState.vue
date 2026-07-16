<template>
  <div class="empty-state">
    <el-empty :description="description" :image-size="imageSize">
      <template v-if="$slots.default || actionText" #default>
        <slot>
          <el-button v-if="actionText" type="primary" @click="$emit('action')">
            {{ actionText }}
          </el-button>
        </slot>
      </template>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  action: [];
}>();

withDefaults(defineProps<{
  description?: string;
  actionText?: string;
  imageSize?: number;
}>(), {
  description: "暂无数据",
  imageSize: 100,
});
</script>

<style scoped lang="scss">
.empty-state {
  padding: 48px 0;
  text-align: center;
}
</style>
