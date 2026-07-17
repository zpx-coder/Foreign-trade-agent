<template>
  <div class="product-selector">
    <!-- 产品多选下拉 -->
    <el-select
      v-model="selectedIds"
      multiple
      filterable
      placeholder="搜索并选择产品（最多 10 个）"
      :disabled="disabled"
      :loading="loading"
      style="width: 100%"
      @change="handleSelectionChange"
    >
      <el-option
        v-for="p in products"
        :key="p.id"
        :label="p.name"
        :value="p.id"
        :disabled="selectedIds.length >= 10 && !selectedIds.includes(p.id)"
      >
        <div class="product-option">
          <span class="product-option-name">{{ p.name }}</span>
          <span class="product-option-meta">
            <template v-if="p.category">{{ p.category }} · </template>
            <template v-if="p.price_usd != null">${{ p.price_usd }}</template>
          </span>
        </div>
      </el-option>
    </el-select>

    <!-- 已选产品卡片 -->
    <div v-if="selectedProducts.length" class="selected-products">
      <div v-for="p in selectedProducts" :key="p.id" class="product-card">
        <img
          v-if="p.image_url || (p.images && p.images[0])"
          :src="p.image_url || (p.images && p.images[0])"
          class="product-card-img"
        />
        <div class="product-card-body">
          <div class="product-card-name">{{ p.name }}</div>
          <div class="product-card-meta">
            <template v-if="p.category">{{ p.category }}</template>
            <template v-if="p.price_usd != null"> · ${{ p.price_usd }} USD</template>
            <template v-if="p.moq != null"> · MOQ: {{ p.moq }}</template>
          </div>
        </div>
        <el-button
          v-if="!disabled"
          circle
          size="small"
          type="danger"
          :icon="Delete"
          @click="removeProduct(p.id)"
        />
      </div>
    </div>

    <div v-if="!selectedProducts.length && !loading && !disabled" class="product-selector-empty">
      暂未选择产品，请从上方搜索添加
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { Delete } from "@element-plus/icons-vue";
import api from "@/api/client";
import type { ProductInline } from "@/stores/icp";

interface ProductItem {
  id: string;
  name: string;
  description?: string;
  category?: string;
  price_usd?: number;
  moq?: number;
  hs_code?: string;
  image_url?: string;
  images?: string[];
  is_active?: boolean;
}

const props = withDefaults(
  defineProps<{
    modelValue?: string[];
    disabled?: boolean;
  }>(),
  {
    modelValue: () => [],
    disabled: false,
  }
);

const emit = defineEmits<{
  "update:modelValue": [ids: string[]];
  "update:productsInline": [products: ProductInline[]];
}>();

const products = ref<ProductItem[]>([]);
const loading = ref(false);
const selectedIds = ref<string[]>([...props.modelValue]);

const selectedProducts = computed(() =>
  products.value.filter((p) => selectedIds.value.includes(p.id))
);

async function loadProducts() {
  loading.value = true;
  try {
    const { data } = await api.get("/products", { params: { page: 1, page_size: 100 } });
    products.value = (data.items || []).filter((p: ProductItem) => p.is_active !== false);
  } catch {
    products.value = [];
  } finally {
    loading.value = false;
  }
}

function handleSelectionChange(ids: string[]) {
  selectedIds.value = ids;
  emit("update:modelValue", ids);
  // 构建内联产品信息快照供 AI prompt 使用
  const inlineData: ProductInline[] = selectedProducts.value.map((p) => ({
    id: p.id,
    name: p.name,
    description: p.description,
    category: p.category,
    price_usd: p.price_usd,
    moq: p.moq,
    hs_code: p.hs_code,
    image_url: p.image_url,
    images: p.images,
  }));
  emit("update:productsInline", inlineData);
}

function removeProduct(id: string) {
  selectedIds.value = selectedIds.value.filter((sid) => sid !== id);
  handleSelectionChange(selectedIds.value);
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) selectedIds.value = [...val];
  },
  { deep: true }
);

onMounted(loadProducts);
</script>

<script lang="ts">
export default { name: "ProductSelector" };
</script>

<style scoped lang="scss">
.product-selector {
  width: 100%;
}

.product-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 8px;

  &-name {
    font-weight: 500;
    color: #1e293b;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &-meta {
    font-size: 12px;
    color: #94a3b8;
    flex-shrink: 0;
  }
}

.selected-products {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.product-card {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: border-color 0.15s;

  &:hover {
    border-color: #cbd5e1;
  }
}

.product-card-img {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.product-card-body {
  flex: 1;
  min-width: 0;
}

.product-card-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-card-meta {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.product-selector-empty {
  margin-top: 10px;
  padding: 14px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  background: #f8fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 10px;
}
</style>
