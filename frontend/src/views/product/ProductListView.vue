<template>
  <div class="product-list-page">
    <PageHeader title="产品管理" :breadcrumb="[{ title: '产品管理' }]">
      <template #actions>
        <el-button type="primary" @click="$router.push('/app/products/create')">
          <el-icon><Plus /></el-icon>
          添加产品
        </el-button>
      </template>
    </PageHeader>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="产品名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="filters.category" placeholder="产品分类" clearable @clear="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable style="width: 120px" @change="handleSearch">
            <el-option label="已上架" :value="true" />
            <el-option label="已下架" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card class="table-card">
      <LoadingSkeleton v-if="loading" variant="table" />
      <EmptyState
        v-else-if="!products.length"
        description="暂未添加产品"
        action-text="添加第一个产品"
        @action="$router.push('/app/products/create')"
      />
      <template v-else>
        <el-table :data="products" stripe style="width: 100%">
          <el-table-column prop="name" label="产品名称" min-width="180">
            <template #default="{ row }">
              <div class="product-name">
                <span class="product-name__text">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column prop="price_usd" label="价格 (USD)" width="140" align="right">
            <template #default="{ row }">
              <span v-if="row.price_usd">${{ Number(row.price_usd).toFixed(2) }}</span>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="moq" label="起订量" width="100" align="right">
            <template #default="{ row }">
              {{ row.moq ?? "—" }}
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100" align="center">
            <template #default="{ row }">
              <StatusBadge :status="row.is_active ? 'active' : 'inactive'" />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="170">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleDateString("zh-CN") }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="$router.push(`/app/products/${row.id}/edit`)">
                编辑
              </el-button>
              <el-button link type="danger" size="small" @click="confirmDelete(row)">
                删除
              </el-button>
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
            @current-change="fetchProducts"
            @size-change="fetchProducts"
          />
        </div>
      </template>
    </el-card>

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
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import api from "@/api/client";

interface ProductItem {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  price_usd: string | null;
  moq: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── 列表状态 ──
const products = ref<ProductItem[]>([]);
const loading = ref(true);

const filters = reactive({
  search: "",
  category: "",
  is_active: undefined as boolean | undefined,
});

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
});

// ── 删除状态 ──
const deleting = ref(false);
const deleteDialog = reactive({
  visible: false,
  id: "",
  name: "",
});

// ── 方法 ──
async function fetchProducts() {
  loading.value = true;
  try {
    const params: Record<string, string | number | boolean> = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };
    if (filters.search) params.search = filters.search;
    if (filters.category) params.category = filters.category;
    if (filters.is_active !== undefined) params.is_active = filters.is_active;

    const { data } = await api.get("/products", { params });
    products.value = data.items;
    pagination.total = data.total;
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "加载产品列表失败");
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  fetchProducts();
}

function handleReset() {
  filters.search = "";
  filters.category = "";
  filters.is_active = undefined;
  pagination.page = 1;
  fetchProducts();
}

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
.product-list-page {
  .filter-card {
    margin-bottom: 16px;
    border-radius: 8px;
  }

  .filter-form {
    :deep(.el-form-item) {
      margin-bottom: 0;
    }
  }

  .table-card {
    border-radius: 8px;
  }

  .product-name {
    display: flex;
    align-items: center;
    gap: 8px;

    &__text {
      font-weight: 500;
    }
  }

  .text-muted {
    color: #c0c4cc;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }
}
</style>
