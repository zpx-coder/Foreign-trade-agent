<template>
  <div class="enterprise-edit-page">
    <PageHeader title="企业资料">
      <template #actions>
        <el-button type="primary" size="large" :loading="saving" @click="handleSaveProfile">保存企业资料</el-button>
      </template>
    </PageHeader>

    <LoadingSkeleton v-if="loading" variant="form" />
    <el-alert v-else-if="loadError" :title="loadError" type="error" show-icon class="block-alert" />

    <!-- 两栏布局 -->
    <div v-else class="enterprise-grid">
      <!-- 公司信息 -->
      <el-card class="section-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">公司信息</span>
            <span class="card-hint">完善信息以解锁 AI 画像生成</span>
          </div>
        </template>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="公司名称" prop="company_name">
                <el-input v-model="form.company_name" placeholder="请输入公司名称" maxlength="255" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属行业" prop="industry">
                <el-input v-model="form.industry" placeholder="如：机械制造、电子产品" maxlength="100" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="国家" prop="country">
                <el-input v-model="form.country" placeholder="如：中国" maxlength="100" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="城市" prop="city">
                <el-input v-model="form.city" placeholder="如：深圳" maxlength="100" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="详细地址" prop="address">
            <el-input v-model="form.address" placeholder="请输入详细地址" maxlength="500" />
          </el-form-item>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="公司官网" prop="website">
                <el-input v-model="form.website" placeholder="https://www.example.com" maxlength="255" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系邮箱" prop="contact_email">
                <el-input v-model="form.contact_email" placeholder="contact@example.com" maxlength="255" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="联系人职位" prop="contact_position">
                <el-input v-model="form.contact_position" placeholder="如：外贸经理" maxlength="100" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" prop="contact_phone">
                <el-input v-model="form.contact_phone" placeholder="+86-755-12345678" maxlength="50" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="公司简介" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="4" placeholder="简要介绍公司业务、优势、资质等" maxlength="2000" show-word-limit />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 产品信息 -->
      <el-card class="section-card">
        <template #header>
          <div class="card-header-row">
            <span class="card-title">产品信息</span>
            <el-button type="primary" @click="openProductDialog()">
              <el-icon><Plus /></el-icon>添加产品
            </el-button>
          </div>
        </template>

        <EmptyState v-if="!productsLoading && products.length === 0" description="暂未添加产品" action-text="添加第一个产品" @action="openProductDialog()" />
        <el-table v-else :data="products" stripe v-loading="productsLoading" class="product-table">
          <el-table-column prop="name" label="产品名称" min-width="180" />
          <el-table-column prop="category" label="分类" width="130" />
          <el-table-column label="价格 (USD)" width="130" align="right">
            <template #default="{ row }">
              <span v-if="row.price_usd" class="price">${{ Number(row.price_usd).toFixed(2) }}</span>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="moq" label="起订量" width="90" align="right">
            <template #default="{ row }">{{ row.moq ?? "—" }}</template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="openProductDialog(row)">编辑</el-button>
              <el-button link type="danger" size="small" @click="handleDeleteProduct(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 产品弹窗 -->
    <el-dialog v-model="productDialog.visible" :title="productDialog.isEdit ? '编辑产品' : '添加产品'" width="520px" :close-on-click-modal="false" @closed="resetProductForm">
      <el-form ref="productFormRef" :model="productForm" :rules="productRules" label-position="top" @submit.prevent>
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入产品名称" maxlength="255" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-input v-model="productForm.category" placeholder="如：电子产品" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="HS 编码" prop="hs_code">
              <el-input v-model="productForm.hs_code" placeholder="海关编码（选填）" maxlength="20" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="价格 (USD)" prop="price_usd">
              <el-input-number v-model="productForm.price_usd" :precision="2" :min="0" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="起订量" prop="moq">
              <el-input-number v-model="productForm.moq" :min="1" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="productForm.description" type="textarea" :rows="2" placeholder="产品描述（选填）" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="productDialog.saving" @click="handleSaveProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { type FormInstance, type FormRules, ElMessage, ElMessageBox } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import api from "@/api/client";

// ── 企业资料 ──
const formRef = ref<FormInstance>();
const loading = ref(true);
const saving = ref(false);
const loadError = ref("");

const form = reactive({
  company_name: "", industry: "", website: "", country: "", city: "",
  address: "", description: "", contact_email: "", contact_phone: "",
  contact_position: "",
});

const rules: FormRules = {
  company_name: [
    { required: true, message: "请输入公司名称", trigger: "blur" },
    { max: 255, message: "公司名称不超过 255 个字符", trigger: "blur" },
  ],
  contact_email: [{ type: "email", message: "邮箱格式不正确", trigger: "blur" }],
  website: [{ pattern: /^(https?:\/\/)?[\w.-]+\.[a-z]{2,}(\/\S*)?$/, message: "请输入有效的网址", trigger: "blur" }],
};

async function loadProfile() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await api.get("/enterprise");
    Object.assign(form, data);
  } catch (err: any) {
    if (err?.response?.status !== 404) loadError.value = err?.response?.data?.detail || "加载企业资料失败";
  } finally {
    loading.value = false;
  }
}

async function handleSaveProfile() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  saving.value = true;
  try {
    await api.put("/enterprise", form);
    ElMessage.success("企业资料已保存");
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

// ── 产品管理 ──
interface ProductItem {
  id: string;
  name: string;
  category: string | null;
  hs_code: string | null;
  price_usd: string | null;
  moq: number | null;
  description: string | null;
}

const products = ref<ProductItem[]>([]);
const productsLoading = ref(false);

const productFormRef = ref<FormInstance>();
const EMPTY_PRODUCT = { name: "", category: "", hs_code: "", price_usd: undefined as number | undefined, moq: undefined as number | undefined, description: "" };

const productForm = reactive({ ...EMPTY_PRODUCT });
const productDialog = reactive({
  visible: false,
  isEdit: false,
  editId: null as string | null,
  saving: false,
});

const productRules: FormRules = {
  name: [{ required: true, message: "请输入产品名称", trigger: "blur" }],
};

async function loadProducts() {
  productsLoading.value = true;
  try {
    const { data } = await api.get("/products", { params: { page: 1, page_size: 50 } });
    products.value = data.items;
  } catch { /* ignore */ }
  finally { productsLoading.value = false; }
}

function openProductDialog(row?: ProductItem) {
  if (row) {
    productDialog.isEdit = true;
    productDialog.editId = row.id;
    Object.assign(productForm, {
      name: row.name,
      category: row.category || "",
      hs_code: row.hs_code || "",
      price_usd: row.price_usd ? Number(row.price_usd) : undefined,
      moq: row.moq ?? undefined,
      description: row.description || "",
    });
  } else {
    productDialog.isEdit = false;
    productDialog.editId = null;
    resetProductForm();
  }
  productDialog.visible = true;
}

function resetProductForm() {
  Object.assign(productForm, { ...EMPTY_PRODUCT });
  productFormRef.value?.resetFields();
}

async function handleSaveProduct() {
  const valid = await productFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  productDialog.saving = true;
  try {
    const payload: Record<string, unknown> = {
      name: productForm.name,
      category: productForm.category || null,
      hs_code: productForm.hs_code || null,
      price_usd: productForm.price_usd ?? null,
      moq: productForm.moq ?? null,
      description: productForm.description || null,
    };
    Object.keys(payload).forEach(k => { if (payload[k] === "") payload[k] = null; });

    if (productDialog.isEdit) {
      await api.put(`/products/${productDialog.editId}`, payload);
      ElMessage.success("产品已更新");
    } else {
      await api.post("/products", payload);
      ElMessage.success("产品已添加");
    }
    productDialog.visible = false;
    loadProducts();
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "保存失败");
  } finally {
    productDialog.saving = false;
  }
}

async function handleDeleteProduct(row: ProductItem) {
  try {
    await ElMessageBox.confirm(`确定删除产品「${row.name}」？`, "删除产品", { confirmButtonText: "删除", cancelButtonText: "取消", type: "warning" });
    await api.delete(`/products/${row.id}`);
    ElMessage.success("已删除");
    loadProducts();
  } catch { /* cancelled */ }
}

onMounted(() => {
  loadProfile();
  loadProducts();
});
</script>

<style scoped lang="scss">
.block-alert {
  margin-bottom: 24px;
}

// ── 两栏布局 ──
.enterprise-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

// ── 卡片 ──
.section-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;

  :deep(.el-card__header) {
    padding: 18px 24px;
  }
  :deep(.el-card__body) {
    padding: 20px 24px;
  }
}

.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.card-hint {
  font-size: 12px;
  color: #94a3b8;
}

// ── 产品表格 ──
.product-table {
  :deep(th) {
    font-weight: 600;
    color: #64748b;
    font-size: 13px;
  }
}

.price {
  font-weight: 600;
  color: #1e293b;
  font-family: "Inter", monospace;
}

.text-muted {
  color: #cbd5e1;
}
</style>
