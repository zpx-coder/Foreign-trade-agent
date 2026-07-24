<template>
  <div class="enterprise-products">
    <!-- 操作栏 -->
    <div class="products-toolbar">
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>添加产品
      </el-button>
    </div>

    <!-- 表格 -->
    <LoadingSkeleton v-if="loading" variant="table" />
    <EmptyState
      v-else-if="!products.length"
      description="暂未添加产品"
      action-text="添加产品"
      @action="openCreateDialog"
    />
    <template v-else>
      <el-table :data="products" stripe style="width: 100%">
        <el-table-column label="图片" width="70">
          <template #default="{ row }">
            <img
              v-if="(row.images && row.images.length) || row.image_url"
              :src="(row.images && row.images[0]) || row.image_url"
              class="product-thumb"
            />
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="产品名称" min-width="160">
          <template #default="{ row }">
            <span class="product-name-text">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="110" />
        <el-table-column prop="price_usd" label="价格 (USD)" width="130" align="right">
          <template #default="{ row }">
            <span v-if="row.price_usd">${{ Number(row.price_usd).toFixed(2) }}</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="moq" label="起订量" width="90" align="right">
          <template #default="{ row }">
            {{ row.moq ?? "—" }}
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <StatusBadge :status="row.is_active ? 'active' : 'inactive'" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          size="small"
          @current-change="fetchProducts"
          @size-change="fetchProducts"
        />
      </div>
    </template>

    <!-- 创建/编辑弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.mode === 'create' ? '添加产品' : '编辑产品'"
      width="620px"
      :close-on-click-modal="false"
      destroy-on-close
      center
    >
      <ProductForm
        v-if="dialog.visible"
        :key="dialog.key"
        :initial="dialog.initial"
        :saving="dialog.saving"
        :show-active="dialog.mode === 'edit'"
        :product-id="dialog.mode === 'edit' ? dialog.productId : ''"
        @submit="handleFormSubmit"
        @cancel="dialog.visible = false"
      />
    </el-dialog>

    <!-- 删除确认 -->
    <ConfirmDialog
      v-model:visible="deleteDialog.visible"
      title="删除产品"
      :message="`确定要删除产品「${deleteDialog.name}」吗？删除后不可恢复。`"
      confirm-type="danger"
      confirm-text="删除"
      :loading="deleting"
      @confirm="handleDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import ProductForm from "@/views/product/components/ProductForm.vue";
import api from "@/api/client";

interface ProductItem {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  hs_code: string | null;
  price_usd: string | null;
  moq: number | null;
  image_url: string | null;
  images: string[] | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── 列表状态 ──
const products = ref<ProductItem[]>([]);
const loading = ref(true);

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
});

async function fetchProducts() {
  loading.value = true;
  try {
    const params: Record<string, string | number | boolean> = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };
    const { data } = await api.get("/products", { params });
    products.value = data.items;
    pagination.total = data.total;
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "加载产品列表失败");
  } finally {
    loading.value = false;
  }
}

// ── 弹窗状态 ──
const dialog = reactive({
  visible: false,
  mode: "create" as "create" | "edit",
  key: 0,
  saving: false,
  productId: "",
  initial: {} as Record<string, unknown>,
});

function openCreateDialog() {
  dialog.mode = "create";
  dialog.productId = "";
  dialog.initial = {};
  dialog.key = Date.now();
  dialog.visible = true;
}

function openEditDialog(row: ProductItem) {
  dialog.mode = "edit";
  dialog.productId = row.id;
  dialog.initial = {
    name: row.name,
    description: row.description || "",
    category: row.category || "",
    hs_code: row.hs_code || "",
    price_usd: row.price_usd != null ? Number(row.price_usd) : undefined,
    moq: row.moq ?? undefined,
    image_url: row.image_url || "",
    images: row.images || [],
    is_active: row.is_active,
  };
  dialog.key = Date.now();
  dialog.visible = true;
}

async function handleFormSubmit(data: Record<string, unknown>, files?: File[]) {
  dialog.saving = true;
  try {
    if (dialog.mode === "create") {
      const { data: created } = await api.post("/products", data);
      // 上传本地图片
      if (files && files.length > 0 && created.id) {
        await uploadImages(created.id, files);
      }
      ElMessage.success("产品已添加");
    } else {
      await api.put(`/products/${dialog.productId}`, data);
      ElMessage.success("产品已更新");
    }
    dialog.visible = false;
    fetchProducts();
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "保存失败");
  } finally {
    dialog.saving = false;
  }
}

async function uploadImages(productId: string, files: File[]) {
  for (const file of files) {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await api.post(`/products/${productId}/images`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    } catch {
      // 图片上传失败不影响产品创建
    }
  }
}

// ── 删除状态 ──
const deleting = ref(false);
const deleteDialog = reactive({
  visible: false,
  id: "",
  name: "",
});

function confirmDelete(row: ProductItem) {
  deleteDialog.id = row.id;
  deleteDialog.name = row.name;
  deleteDialog.visible = true;
}

async function handleDelete() {
  deleting.value = true;
  try {
    await api.delete(`/products/${deleteDialog.id}`);
    ElMessage.success("产品已删除");
    deleteDialog.visible = false;
    fetchProducts();
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "删除失败");
  } finally {
    deleting.value = false;
  }
}

onMounted(fetchProducts);
</script>

<style scoped lang="scss">
.enterprise-products {
  .products-toolbar {
    margin-bottom: 16px;
    display: flex;
    justify-content: flex-end;
  }

  .product-name-text {
    font-weight: 500;
    color: #1e293b;
  }

  .text-muted {
    color: #c0c4cc;
  }

  .product-thumb {
    width: 48px;
    height: 48px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }
}
</style>
