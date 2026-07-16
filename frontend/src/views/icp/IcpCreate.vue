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
                <el-input v-model="form.target_industry" placeholder="如：消费电子" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公司规模">
                <el-select v-model="form.company_size" placeholder="请选择" style="width: 100%">
                  <el-option label="小型企业 (1-50人)" value="小型企业 (1-50人)" />
                  <el-option label="中型企业 (50-200人)" value="中型企业 (50-200人)" />
                  <el-option label="大型企业 (200-1000人)" value="大型企业 (200-1000人)" />
                  <el-option label="超大型企业 (1000人+)" value="超大型企业 (1000人+)" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <!-- Step 1: 产品信息 -->
        <template v-if="step === 1">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="产品品类">
                <el-input v-model="form.product_category" placeholder="如：蓝牙耳机、智能穿戴" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="价格区间">
                <el-input v-model="form.product_price_range" placeholder="如：$15-50 / 件" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="产品特点 / 优势">
            <el-input v-model="form.product_features" type="textarea" :rows="3" placeholder="如：ANC主动降噪、IPX5防水、支持无线充电" />
          </el-form-item>
        </template>

        <!-- Step 2: 客户特征 -->
        <template v-if="step === 2">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="客户预算">
                <el-input v-model="form.customer_budget" placeholder="如：$5,000-50,000 / 批" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="决策者角色">
                <el-input v-model="form.decision_makers" placeholder="如：采购经理、产品总监、CEO" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="客户痛点">
            <el-input v-model="form.pain_points" type="textarea" :rows="3" placeholder="如：现有供应商交期不稳定、质量参差不齐" />
          </el-form-item>
          <el-form-item label="补充说明">
            <el-input v-model="form.additional_notes" type="textarea" :rows="2" placeholder="其他需要 AI 了解的信息（选填）" />
          </el-form-item>
        </template>
      </el-form>

      <div class="step-actions">
        <el-button v-if="step > 0" @click="step--">上一步</el-button>
        <el-button v-if="step < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="step === 2" type="primary" size="large" :loading="saving" @click="handleCreateAndGenerate">
          <el-icon><MagicStick /></el-icon>保存并生成画像
        </el-button>
      </div>
    </el-card>

    <!-- AI 生成面板 -->
    <el-card v-if="showGeneratePanel" class="generate-card">
      <template #header><span class="card-title">AI 生成结果</span></template>
      <StreamingOutput
        :is-streaming="isStreaming"
        :current-section="currentSection"
        :error="genError"
        :done="completed"
      >
        <template #done>
          <el-button type="primary" size="large" @click="goDetail">
            查看完整画像 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </template>
      </StreamingOutput>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { MagicStick, ArrowRight } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import StreamingOutput from "@/components/ai/StreamingOutput.vue";
import { useSSE } from "@/composables/useSSE";
import { useIcpStore } from "@/stores/icp";

const router = useRouter();
const icpStore = useIcpStore();
const step = ref(0);
const saving = ref(false);

const form = reactive({
  name: "",
  target_industry: "",
  target_region: "",
  company_size: "",
  product_category: "",
  product_price_range: "",
  product_features: "",
  customer_budget: "",
  pain_points: "",
  decision_makers: "",
  additional_notes: "",
});

function nextStep() {
  if (step.value === 0 && !form.name.trim()) { ElMessage.warning("请输入画像名称"); return; }
  step.value++;
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
  if (!form.name.trim()) { ElMessage.warning("请输入画像名称"); return; }
  saving.value = true;
  try {
    const { name, ...inputData } = form;
    const icp = await icpStore.create({ name, ...inputData });
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

.generate-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}
</style>
