<template>
  <div class="product-edit-page">
    <PageHeader
      title="编辑产品"
      :breadcrumb="[
        { title: '产品管理', path: '/app/products' },
        { title: '编辑产品' },
      ]"
    />

    <LoadingSkeleton v-if="loading" variant="form" />
    <el-alert
      v-else-if="loadError"
      :title="loadError"
      type="error"
      show-icon
      class="page-alert"
    />

    <el-card v-else class="form-card">
      <ProductForm
        ref="formRef"
        :initial="initialData"
        :saving="saving"
        :product-id="route.params.id as string"
        show-active
        @submit="handleUpdate"
        @cancel="$router.push('/app/products')"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import ProductForm from "./components/ProductForm.vue";
import api from "@/api/client";

const route = useRoute();
const router = useRouter();
const formRef = ref<InstanceType<typeof ProductForm>>();
const loading = ref(true);
const saving = ref(false);
const loadError = ref("");

const initialData = reactive<Record<string, any>>({
  name: "",
  description: "",
  category: "",
  hs_code: "",
  price_usd: undefined as number | undefined,
  moq: undefined as number | undefined,
  image_url: "",
  images: [] as string[],
  is_active: true,
});

async function loadProduct() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get(`/products/${route.params.id}`);
    initialData.name = data.name;
    initialData.description = data.description || "";
    initialData.category = data.category || "";
    initialData.hs_code = data.hs_code || "";
    initialData.price_usd = data.price_usd ? Number(data.price_usd) : undefined;
    initialData.moq = data.moq ?? undefined;
    initialData.image_url = data.image_url || "";
    initialData.images = data.images || [];
    initialData.is_active = data.is_active;
  } catch (err: any) {
    loadError.value = err?.response?.data?.detail || "加载产品信息失败";
  } finally {
    loading.value = false;
  }
}

async function handleUpdate(formData: Record<string, unknown>) {
  saving.value = true;
  try {
    await api.put(`/products/${route.params.id}`, formData);
    ElMessage.success("产品信息已更新");
    router.push("/app/products");
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "更新失败");
  } finally {
    saving.value = false;
  }
}

onMounted(loadProduct);
</script>

<style scoped lang="scss">
.product-edit-page {
  // uses MainLayout content-inner max-width
}

.form-card {
  border-radius: 8px;
}

.page-alert {
  margin-bottom: 20px;
}
</style>
