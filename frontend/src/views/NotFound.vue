<template>
  <div class="not-found-page">
    <div class="nf-content">
      <div class="nf-code">404</div>
      <h1 class="nf-title">页面不存在</h1>
      <p class="nf-desc">您访问的页面可能已被移除或地址输入有误。</p>
      <div class="nf-actions">
        <el-button type="primary" @click="$router.push('/app/dashboard')">返回工作台</el-button>
        <el-button @click="$router.push('/admin/dashboard')">管理后台</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f8fafc;
}
.nf-content {
  text-align: center;
}
.nf-code {
  font-size: 96px;
  font-weight: 800;
  color: #e2e8f0;
  line-height: 1;
  letter-spacing: -2px;
}
.nf-title {
  font-size: 24px;
  color: #1e293b;
  margin: 16px 0 8px;
}
.nf-desc {
  color: #64748b;
  margin: 0 0 24px;
}
.nf-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>
