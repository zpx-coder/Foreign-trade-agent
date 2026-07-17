<template>
  <div class="product-create-page">
    <PageHeader
      title="添加产品"
      :breadcrumb="[
        { title: '产品管理', path: '/app/products' },
        { title: '添加产品' },
      ]"
    />

    <el-card class="form-card">
      <ProductForm ref="formRef" :saving="saving" @submit="handleCreate" @cancel="$router.push('/app/products')" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import PageHeader from "@/components/common/PageHeader.vue";
import ProductForm from "./components/ProductForm.vue";
import api from "@/api/client";

const router = useRouter();
const formRef = ref<InstanceType<typeof ProductForm>>();
const saving = ref(false);

async function handleCreate(formData: Record<string, unknown>, files?: File[]) {
  saving.value = true;
  try {
    const { data } = await api.post("/products", formData);
    const productId = data.id as string;

    // 上传本地图片（如果有）
    if (files && files.length > 0) {
      for (const file of files) {
        const fd = new FormData();
        fd.append("file", file);
        await api.post(`/products/${productId}/images`, fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
    }

    ElMessage.success("产品创建成功");
    router.push("/app/products");
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "创建失败");
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped lang="scss">
.product-create-page {
  // uses MainLayout content-inner max-width
}

.form-card {
  border-radius: 8px;
}
</style>
