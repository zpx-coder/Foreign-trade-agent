<template>
  <div class="icp-create-page">
    <PageHeader title="新建客户画像" :breadcrumb="[{ title: '客户画像', path: '/app/icps' }, { title: '新建画像' }]" />

    <!-- 步骤表单 -->
    <el-card class="form-card">
      <el-steps :active="step" finish-status="success" align-center class="steps">
        <el-step title="目标市场" />
        <el-step title="产品信息" />
        <el-step title="客户特征" />
      </el-steps>

      <el-form ref="formRef" :model="form" label-position="top" class="icp-form">
        <!-- Step 0: 目标市场 -->
        <template v-if="step === 0">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="画像名称" required>
                <el-input v-model="form.name" placeholder="如：北美蓝牙耳机进口商" maxlength="255" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="目标地区">
                <el-input v-model="form.target_region" placeholder="如：北美、西欧" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="目标行业">
                <el-select
                  v-model="form.target_industry"
                  filterable
                  allow-create
                  clearable
                  placeholder="请选择或输入行业"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in B2B_INDUSTRIES"
                    :key="item"
                    :label="item"
                    :value="item"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公司规模">
                <el-select v-model="form.company_size" multiple placeholder="请选择（可多选）" style="width: 100%">
                  <el-option label="小型企业 (1-50人)" value="小型企业（1-50人）" />
                  <el-option label="中型企业 (50-200人)" value="中型企业（50-200人）" />
                  <el-option label="大型企业 (200-1000人)" value="大型企业（200-1000人）" />
                  <el-option label="超大型企业 (1000人+)" value="超大型企业（1000人+）" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <!-- Step 1: 产品信息（v1.5：支持关联产品 + 手动填写） -->
        <template v-if="step === 1">
          <!-- 来源切换 -->
          <el-form-item label="产品来源">
            <el-radio-group v-model="form.product_source">
              <el-radio-button value="linked">关联已有产品</el-radio-button>
              <el-radio-button value="manual">手动填写产品</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <!-- 方式一：关联已有产品 -->
          <template v-if="form.product_source === 'linked'">
            <el-form-item label="选择产品">
              <ProductSelector
                v-model="form.product_ids"
                @update:productsInline="handleProductsInline"
              />
            </el-form-item>
          </template>

          <!-- 方式二：手动填写产品 -->
          <template v-else>
            <div v-for="(mp, idx) in form.manual_products" :key="idx" class="manual-product-card">
              <div class="manual-product-card__header">
                <span class="manual-product-card__title">产品 {{ idx + 1 }}</span>
                <el-button type="danger" text size="small" @click="removeManualProduct(idx)">
                  <el-icon><Delete /></el-icon>删除
                </el-button>
              </div>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="产品名称" required>
                    <el-input v-model="mp.name" placeholder="如：蓝牙降噪耳机 Pro Max" maxlength="255" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="产品品类">
                    <el-input v-model="mp.category" placeholder="如：消费电子、家居用品" maxlength="100" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="16">
                <el-col :span="8">
                  <el-form-item label="单价 (USD)">
                    <el-input-number v-model="mp.price_usd" :precision="2" :min="0" :controls="false" placeholder="如：12.99" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="起订量 (MOQ)">
                    <el-input-number v-model="mp.moq" :precision="0" :min="1" :controls="false" placeholder="如：500" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="HS 编码">
                    <el-input v-model="mp.hs_code" placeholder="如：8518.30" maxlength="20" />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="产品描述">
                <el-input v-model="mp.description" type="textarea" :rows="2" placeholder="简要描述产品特性、材质、用途等" maxlength="2000" show-word-limit />
              </el-form-item>
            </div>

            <el-button type="primary" dashed class="add-product-btn" @click="addManualProduct">
              <el-icon><Plus /></el-icon>添加产品
            </el-button>
          </template>
        </template>

        <!-- Step 2: 采购商特征 -->
        <template v-if="step === 2">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="买家类型">
                <el-select v-model="form.buyer_type" placeholder="请选择买家类型" style="width: 100%" clearable>
                  <el-option label="进口商" value="进口商" />
                  <el-option label="品牌商/品牌贴牌" value="品牌商/品牌贴牌" />
                  <el-option label="批发商" value="批发商" />
                  <el-option label="经销商/代理商" value="经销商/代理商" />
                  <el-option label="零售商/连锁店" value="零售商/连锁店" />
                  <el-option label="电商卖家" value="电商卖家" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="客户单批次采购预算 (USD)">
                <div class="price-range-row">
                  <el-input-number v-model="form.customer_budget_min" :precision="0" :min="0" :controls="false" placeholder="最低预算" style="width: 130px" />
                  <span class="price-sep">—</span>
                  <el-input-number v-model="form.customer_budget_max" :precision="0" :min="0" :controls="false" placeholder="最高预算" style="width: 130px" />
                  <span class="price-unit">USD</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="关键决策因素">
                <el-select v-model="form.key_decision_factors" multiple placeholder="可多选" style="width: 100%">
                  <el-option label="价格竞争力" value="价格" />
                  <el-option label="产品质量/品控" value="质量" />
                  <el-option label="交期稳定性" value="交期" />
                  <el-option label="认证资质（CE/FDA等）" value="认证资质" />
                  <el-option label="售后/退换货服务" value="售后服务" />
                  <el-option label="付款条件（L/C、赊销等）" value="付款条件" />
                  <el-option label="设计/定制能力" value="设计能力" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="决策者角色">
                <el-input v-model="form.decision_makers" placeholder="如：采购经理、产品总监、CEO" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="客户痛点">
            <el-input v-model="form.pain_points" type="textarea" :rows="3" placeholder="如：现有供应商交期不稳定、质量参差不齐、起订量过高" />
          </el-form-item>
          <el-form-item label="补充说明">
            <el-input v-model="form.additional_notes" type="textarea" :rows="2" placeholder="其他需要 AI 了解的信息（选填）" />
          </el-form-item>
        </template>
      </el-form>

      <div class="step-actions">
        <el-button v-if="step > 0" @click="step--">上一步</el-button>
        <el-button v-if="step < 2" type="primary" @click="nextStep">下一步</el-button>
        <template v-if="step === 2">
          <el-button size="large" :loading="saving" @click="handleSaveDraft">保存草稿</el-button>
          <el-button type="primary" size="large" :loading="saving" @click="handleCreateAndGenerate">
            <el-icon><MagicStick /></el-icon>保存并生成画像
          </el-button>
        </template>
      </div>
    </el-card>

    <!-- AI 生成弹窗 -->
    <el-dialog
      v-model="showGeneratePanel"
      title="AI 生成结果"
      width="600px"
      :close-on-click-modal="false"
      destroy-on-close
      center
      class="generate-dialog"
    >
      <StreamingOutput
        :is-streaming="isStreaming"
        :current-section="currentSection"
        :error="genError"
        :done="completed"
      >
        <template #done>
          <div class="dialog-done-actions">
            <el-button type="primary" size="large" @click="goDetail">
              查看完整画像 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
      </StreamingOutput>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { MagicStick, ArrowRight, Delete, Plus } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import StreamingOutput from "@/components/ai/StreamingOutput.vue";
import ProductSelector from "./components/ProductSelector.vue";
import { useSSE } from "@/composables/useSSE";
import { B2B_INDUSTRIES } from "@/constants/industries";
import { useIcpStore } from "@/stores/icp";
import type { ProductInline } from "@/stores/icp";

const router = useRouter();
const icpStore = useIcpStore();
const step = ref(0);
const saving = ref(false);

// v1.5: 手动填写产品
interface ManualProduct {
  name: string;
  category: string;
  description: string;
  price_usd: number | undefined;
  moq: number | undefined;
  hs_code: string;
}
const emptyManualProduct = (): ManualProduct => ({
  name: "",
  category: "",
  description: "",
  price_usd: undefined,
  moq: undefined,
  hs_code: "",
});

const form = reactive<Record<string, unknown>>({
  name: "",
  target_industry: "",
  target_region: "",
  company_size: [] as string[],
  product_ids: [] as string[],
  product_source: "linked",
  manual_products: [] as ManualProduct[],
  customer_budget_min: undefined as number | undefined,
  customer_budget_max: undefined as number | undefined,
  buyer_type: "",
  key_decision_factors: [] as string[],
  pain_points: "",
  decision_makers: "",
  additional_notes: "",
});

// v1.3: 产品内联数据（供 AI prompt 使用）
const productsInlineData = ref<ProductInline[]>([]);

function handleProductsInline(products: ProductInline[]) {
  productsInlineData.value = products;
}

// v1.5: 手动产品管理
function addManualProduct() {
  (form.manual_products as ManualProduct[]).push(emptyManualProduct());
}
function removeManualProduct(idx: number) {
  (form.manual_products as ManualProduct[]).splice(idx, 1);
}

function nextStep() {
  if (step.value === 0 && !(form.name as string).trim()) {
    ElMessage.warning("请输入画像名称");
    return;
  }
  step.value++;
}

// ── 构建输入数据 ──
function buildInputData(): Record<string, unknown> {
  const inputData: Record<string, unknown> = {
    target_industry: form.target_industry || null,
    target_region: form.target_region || null,
    company_size: (form.company_size as string[]).length > 0 ? form.company_size : null,
    product_ids: (form.product_ids as string[]).length > 0 ? form.product_ids : null,
    customer_budget_min: form.customer_budget_min ?? null,
    customer_budget_max: form.customer_budget_max ?? null,
    buyer_type: form.buyer_type || null,
    key_decision_factors: (form.key_decision_factors as string[]).length > 0 ? form.key_decision_factors : null,
    pain_points: form.pain_points || null,
    decision_makers: form.decision_makers || null,
    additional_notes: form.additional_notes || null,
  };
  // 产品内联快照（关联模式）
  if (form.product_source === "linked" && productsInlineData.value.length > 0) {
    inputData._products_inline = productsInlineData.value;
  }
  // v1.5: 手动填写产品
  inputData.product_source = form.product_source || "linked";
  if (form.product_source === "manual" && (form.manual_products as ManualProduct[]).length > 0) {
    inputData.manual_products = form.manual_products;
  }
  return inputData;
}

// ── 保存草稿 ──
async function handleSaveDraft() {
  if (!(form.name as string).trim()) {
    ElMessage.warning("请输入画像名称");
    return;
  }
  saving.value = true;
  try {
    const inputData = buildInputData();
    await icpStore.createDraft({ name: form.name as string, ...inputData } as any);
    ElMessage.success("草稿已保存");
    router.push("/app/icps");
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
}

// ── AI 生成 ──
const showGeneratePanel = ref(false);
const completed = ref(false);
const genError = ref<string | null>(null);
let createdId: string | null = null;

const { isStreaming, currentSection, error: sseError, start: startSSE } = useSSE({
  onError: (msg) => { genError.value = msg; },
  onComplete: () => { completed.value = true; },
});

watch(sseError, (v) => { if (v) genError.value = v; });
watch(isStreaming, (v, prev) => {
  if (prev && !v && !completed.value && !genError.value) {
    completed.value = true;
  }
});

async function handleCreateAndGenerate() {
  if (!(form.name as string).trim()) {
    ElMessage.warning("请输入画像名称");
    return;
  }
  saving.value = true;
  try {
    const inputData = buildInputData();
    const { name, ...rest } = { name: form.name as string, ...inputData };
    const icp = await icpStore.create({ name, ...rest } as any);
    createdId = icp.id;
    showGeneratePanel.value = true;
    completed.value = false;
    genError.value = null;

    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";
    startSSE(`${baseUrl}/icps/${createdId}/generate`);
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "创建失败");
  } finally {
    saving.value = false;
  }
}

function goDetail() {
  if (createdId) router.push(`/app/icps/${createdId}`);
}
</script>

<style scoped lang="scss">
.form-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;

  :deep(.el-card__body) {
    padding: 32px;
  }
}

.steps {
  margin-bottom: 36px;

  :deep(.el-step__title) {
    font-size: 14px;
    font-weight: 500;
  }
}

.icp-form {
  max-width: 860px;
  margin: 0 auto;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid #f1f5f9;
}

.generate-dialog {
  :deep(.el-dialog__body) {
    padding-top: 8px;
  }
}

.dialog-done-actions {
  text-align: center;
  margin-top: 20px;
}

// ── 价格区间行 ──
.price-range-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-sep {
  color: #94a3b8;
  font-size: 14px;
}

.price-unit {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

// ── v1.5 手动产品卡片 ──
.manual-product-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e8ecf1;
  }

  &__title {
    font-size: 15px;
    font-weight: 600;
    color: #1e293b;
  }
}

.add-product-btn {
  width: 100%;
  border-style: dashed;
  margin-top: 4px;
}
</style>
