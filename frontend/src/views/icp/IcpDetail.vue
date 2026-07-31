<template>
  <div class="icp-detail-page">
    <PageHeader :title="icp?.name || '画像详情'" :breadcrumb="[{ title: '客户画像', path: '/app/icps' }, { title: icp?.name || '详情' }]">
      <template #actions>
        <!-- v1.3: 重新生成扩展到 completed/draft/failed -->
        <el-button v-if="icp && (icp.status === 'draft' || icp.status === 'failed' || icp.status === 'completed')" type="primary" :loading="regenerating" @click="handleRegenerateClick">
          {{ icp.status === 'completed' ? '重新生成' : '生成画像' }}
        </el-button>
        <el-button v-if="icp && !editing" @click="startEditing">编辑输入信息</el-button>
        <el-button @click="$router.push('/app/icps')">返回列表</el-button>
      </template>
    </PageHeader>

    <LoadingSkeleton v-if="loading" variant="detail" />
    <el-alert v-else-if="loadError" :title="loadError" type="error" show-icon class="block-alert" />

    <template v-else-if="icp">
      <!-- 状态 + 元信息 -->
      <el-card class="info-card">
        <div class="meta-row">
          <div class="meta-left">
            <StatusBadge :status="icp.status" size="default" />
            <span v-if="icp.generation_time_ms" class="gen-time">· 生成耗时 {{ (icp.generation_time_ms / 1000).toFixed(1) }}s</span>
          </div>
          <span class="date">创建于 {{ new Date(icp.created_at).toLocaleString("zh-CN") }}</span>
        </div>
        <el-alert v-if="icp.status === 'failed' && icp.error_message" :title="'生成失败: ' + icp.error_message" type="error" show-icon class="error-alert" />
      </el-card>

      <!-- 两栏布局：输入 + 输出 -->
      <div class="detail-grid">
        <!-- 输入摘要 / 编辑模式 -->
        <el-card class="section-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">{{ editing ? '编辑输入信息' : '输入信息' }}</span>
              <div v-if="editing" class="edit-actions">
                <el-button size="small" @click="cancelEditing">取消</el-button>
                <el-button size="small" type="primary" :loading="savingEdit" @click="handleSaveAndRegenerate">保存并重新生成</el-button>
              </div>
            </div>
          </template>

          <!-- 显示模式 -->
          <el-descriptions v-if="!editing" :column="1" border size="small">
            <el-descriptions-item label="目标行业">{{ inputData.target_industry || "—" }}</el-descriptions-item>
            <el-descriptions-item label="目标地区">{{ inputData.target_region || "—" }}</el-descriptions-item>
            <el-descriptions-item label="公司规模">{{ formatCompanySize(inputData.company_size) }}</el-descriptions-item>
            <el-descriptions-item label="买家类型">{{ inputData.buyer_type || "—" }}</el-descriptions-item>
            <el-descriptions-item label="客户单批次采购预算">{{ formatPriceRange(inputData.customer_budget_min, inputData.customer_budget_max) }}</el-descriptions-item>
            <el-descriptions-item label="关键决策因素">{{ formatCompanySize(inputData.key_decision_factors) }}</el-descriptions-item>
            <el-descriptions-item label="决策者角色">{{ inputData.decision_makers || "—" }}</el-descriptions-item>
            <el-descriptions-item label="客户痛点">{{ inputData.pain_points || "—" }}</el-descriptions-item>
          </el-descriptions>

          <!-- 编辑模式 -->
          <el-form v-else :model="editForm" label-position="top" class="edit-form">
            <el-form-item label="目标行业">
                <el-select
                  v-model="editForm.target_industry"
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
            <el-form-item label="目标地区">
              <el-input v-model="editForm.target_region" placeholder="如：北美、西欧" />
            </el-form-item>
            <el-form-item label="公司规模">
              <el-select v-model="editForm.company_size" multiple placeholder="可多选" style="width: 100%">
                <el-option label="小型企业 (1-50人)" value="小型企业（1-50人）" />
                <el-option label="中型企业 (50-200人)" value="中型企业（50-200人）" />
                <el-option label="大型企业 (200-1000人)" value="大型企业（200-1000人）" />
                <el-option label="超大型企业 (1000人+)" value="超大型企业（1000人+）" />
              </el-select>
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="买家类型">
                  <el-select v-model="editForm.buyer_type" placeholder="请选择" style="width: 100%" clearable>
                    <el-option label="进口商" value="进口商" />
                    <el-option label="品牌商/品牌贴牌" value="品牌商/品牌贴牌" />
                    <el-option label="批发商" value="批发商" />
                    <el-option label="经销商/代理商" value="经销商/代理商" />
                    <el-option label="零售商/连锁店" value="零售商/连锁店" />
                    <el-option label="电商卖家" value="电商卖家" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="客户单批次采购预算 (USD)">
              <div class="price-range-row">
                <el-input-number v-model="editForm.customer_budget_min" :precision="0" :min="0" :controls="false" placeholder="最低" style="width: 120px" />
                <span class="price-sep">—</span>
                <el-input-number v-model="editForm.customer_budget_max" :precision="0" :min="0" :controls="false" placeholder="最高" style="width: 120px" />
                <span class="price-unit">USD</span>
              </div>
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="关键决策因素">
                  <el-select v-model="editForm.key_decision_factors" multiple placeholder="可多选" style="width: 100%">
                    <el-option label="价格" value="价格" />
                    <el-option label="质量" value="质量" />
                    <el-option label="交期" value="交期" />
                    <el-option label="认证资质" value="认证资质" />
                    <el-option label="售后服务" value="售后服务" />
                    <el-option label="付款条件" value="付款条件" />
                    <el-option label="设计能力" value="设计能力" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="决策者角色">
              <el-input v-model="editForm.decision_makers" placeholder="如：采购经理、CEO" />
            </el-form-item>
            <el-form-item label="客户痛点">
              <el-input v-model="editForm.pain_points" type="textarea" :rows="2" placeholder="客户痛点" />
            </el-form-item>
            <el-form-item label="补充说明">
              <el-input v-model="editForm.additional_notes" type="textarea" :rows="2" />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- AI 输出 -->
        <el-card v-if="!icp.output_data?.parse_error" class="section-card">
          <template #header><span class="card-title">AI 画像报告</span></template>

          <!-- SSE 生成中 -->
          <StreamingOutput
            v-if="showStreaming"
            :is-streaming="isStreaming"
            :current-section="currentSection"
            :error="streamError"
            :done="streamDone"
          />

          <template v-else>
            <div v-if="!output.summary && !output.target_market && !output.customer_persona" class="empty-output">
              <el-empty description="暂无输出数据" :image-size="80" />
            </div>

            <div v-if="output.summary" class="output-section">
              <h3>画像摘要</h3>
              <p>{{ output.summary }}</p>
            </div>

            <div v-if="output.target_market" class="output-section">
              <h3>目标市场</h3>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="主要行业">{{ (output.target_market.primary_industries || []).join("、") || "—" }}</el-descriptions-item>
                <el-descriptions-item label="主要地区">{{ (output.target_market.primary_regions || []).join("、") || "—" }}</el-descriptions-item>
                <el-descriptions-item label="公司规模">{{ output.target_market.company_size_range || "—" }}</el-descriptions-item>
              </el-descriptions>
            </div>

            <div v-if="output.customer_persona" class="output-section">
              <h3>客户画像</h3>
              <div v-if="output.customer_persona.decision_makers?.length" class="sub-section">
                <h4>决策者</h4>
                <div v-for="(dm, i) in output.customer_persona.decision_makers" :key="i" class="persona-item">
                  <span class="role">{{ dm.title || dm.role }}</span>
                  <div class="concerns">{{ (dm.concerns || []).join("；") }}</div>
                </div>
              </div>
              <div v-if="output.customer_persona.pain_points?.length" class="sub-section">
                <h4>痛点</h4>
                <ul><li v-for="(p, i) in output.customer_persona.pain_points" :key="i">{{ p }}</li></ul>
              </div>
              <div v-if="output.customer_persona.buying_motivations?.length" class="sub-section">
                <h4>采购动机</h4>
                <ul><li v-for="(m, i) in output.customer_persona.buying_motivations" :key="i">{{ m }}</li></ul>
              </div>
            </div>

            <div v-if="output.competitive_advantages?.length" class="output-section">
              <h3>竞争优势</h3>
              <ul><li v-for="(a, i) in output.competitive_advantages" :key="i">{{ a }}</li></ul>
            </div>

            <div v-if="output.recommended_approach" class="output-section">
              <h3>推荐策略</h3>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="触达渠道">{{ (output.recommended_approach.outreach_channels || []).join("、") || "—" }}</el-descriptions-item>
                <el-descriptions-item label="切入点">{{ (output.recommended_approach.messaging_angles || []).join("；") || "—" }}</el-descriptions-item>
                <el-descriptions-item label="筛选问题">{{ (output.recommended_approach.qualifying_questions || []).join("；") || "—" }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </el-card>

        <!-- 解析失败回退 -->
        <el-card v-else class="section-card">
          <template #header><span class="card-title">原始输出</span></template>
          <pre class="raw-output">{{ icp.output_data.raw_text }}</pre>
        </el-card>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import StreamingOutput from "@/components/ai/StreamingOutput.vue";
import { B2B_INDUSTRIES } from "@/constants/industries";
import { useSSE } from "@/composables/useSSE";
import { useIcpStore } from "@/stores/icp";
import type { IcpItem } from "@/stores/icp";

const route = useRoute();
const icpStore = useIcpStore();
const icp = ref<IcpItem | null>(null);
const loading = ref(true);
const loadError = ref("");
const regenerating = ref(false);
const editing = ref(false);
const savingEdit = ref(false);

// ── 编辑表单 ──
const editForm = reactive<Record<string, unknown>>({
  target_industry: "",
  target_region: "",
  company_size: [] as string[],
  customer_budget_min: undefined as number | undefined,
  customer_budget_max: undefined as number | undefined,
  buyer_type: "",
  key_decision_factors: [] as string[],
  product_features: "",
  pain_points: "",
  decision_makers: "",
  additional_notes: "",
});

const inputData = computed(() => icp.value?.input_data || {} as Record<string, unknown>);
const output = computed(() => (icp.value?.output_data as Record<string, unknown>) || {});

// ── 格式化辅助 ──
function formatCompanySize(val: unknown) {
  if (!val) return "—";
  if (Array.isArray(val)) return val.join("、") || "—";
  return String(val);
}

function formatPriceRange(min: unknown, max: unknown) {
  if (min != null && max != null) return `$ ${min} — $ ${max} USD`;
  if (min != null) return `≥ $ ${min} USD`;
  if (max != null) return `≤ $ ${max} USD`;
  return "—";
}

// ── 编辑模式 ──
function startEditing() {
  const data = inputData.value;
  let companySize = data.company_size;
  if (typeof companySize === "string") companySize = [companySize];
  if (!Array.isArray(companySize)) companySize = [];

  Object.assign(editForm, {
    target_industry: data.target_industry || "",
    target_region: data.target_region || "",
    company_size: companySize,
    customer_budget_min: data.customer_budget_min ?? undefined,
    customer_budget_max: data.customer_budget_max ?? undefined,
    buyer_type: data.buyer_type || "",
    key_decision_factors: Array.isArray(data.key_decision_factors) ? [...data.key_decision_factors] : [],
    product_features: data.product_features || "",
    pain_points: data.pain_points || "",
    decision_makers: data.decision_makers || "",
    additional_notes: data.additional_notes || "",
  });
  editing.value = true;
}

function cancelEditing() {
  editing.value = false;
}

// ── SSE 流式重新生成 ──
const showStreaming = ref(false);
const streamDone = ref(false);
const streamError = ref<string | null>(null);

const { isStreaming, currentSection, error: sseError2, start: startStreaming } = useSSE({
  onError: (msg) => { streamError.value = msg; },
  onComplete: () => { streamDone.value = true; },
});

watch(sseError2, (v) => { if (v) streamError.value = v; });
watch(isStreaming, (v, prev) => {
  if (prev && !v && !streamDone.value && !streamError.value) {
    streamDone.value = true;
  }
});

// ── 触发重新生成（含 completed 覆盖确认）──
async function handleRegenerateClick() {
  if (icp.value?.status === "completed") {
    try {
      await ElMessageBox.confirm(
        "重新生成将覆盖现有画像结果，是否继续？",
        "确认重新生成",
        { confirmButtonText: "继续", cancelButtonText: "取消", type: "warning" }
      );
    } catch {
      return; // 用户取消
    }
  }
  await doRegenerate();
}

async function doRegenerate() {
  regenerating.value = true;
  streamDone.value = false;
  streamError.value = null;
  showStreaming.value = true;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";
    startStreaming(`${baseUrl}/icps/${route.params.id}/generate`);
    // 等待流结束
    await new Promise<void>((resolve) => {
      const stop = watch(streamDone, (v) => { if (v) { stop(); resolve(); } });
      const stopErr = watch(streamError, (v) => { if (v) { stopErr(); resolve(); } });
    });
    ElMessage.success("重新生成完成");
    await loadData();
    showStreaming.value = false;
  } catch (err: any) {
    ElMessage.error(err.message || "生成失败");
  } finally {
    regenerating.value = false;
  }
}

// ── 编辑并保存 + 重新生成 ──
async function handleSaveAndRegenerate() {
  savingEdit.value = true;
  try {
    const inputDataPayload: Record<string, unknown> = {
      target_industry: editForm.target_industry || null,
      target_region: editForm.target_region || null,
      company_size: (editForm.company_size as string[]).length > 0 ? editForm.company_size : null,
      customer_budget_min: editForm.customer_budget_min ?? null,
      customer_budget_max: editForm.customer_budget_max ?? null,
      buyer_type: editForm.buyer_type || null,
      key_decision_factors: (editForm.key_decision_factors as string[]).length > 0 ? editForm.key_decision_factors : null,
      product_features: editForm.product_features || null,
      pain_points: editForm.pain_points || null,
      decision_makers: editForm.decision_makers || null,
      additional_notes: editForm.additional_notes || null,
    };

    await icpStore.update(route.params.id as string, { input_data: inputDataPayload as any });
    editing.value = false;
    ElMessage.success("已保存，正在重新生成...");

    // 触发重新生成
    await doRegenerate();
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "保存失败");
  } finally {
    savingEdit.value = false;
  }
}

// ── 加载数据 ──
async function loadData() {
  loading.value = true;
  try {
    icp.value = await icpStore.fetchDetail(route.params.id as string);
  } catch (err: any) {
    loadError.value = err?.response?.data?.detail || "加载失败";
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped lang="scss">
.block-alert {
  margin-bottom: 20px;
}

// ── 状态卡 ──
.info-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;

  .meta-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }
  .meta-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .gen-time {
    color: #94a3b8;
    font-size: 13px;
  }
  .date {
    color: #94a3b8;
    font-size: 13px;
  }
  .error-alert {
    margin-top: 12px;
  }
}

// ── 双栏布局 ──
.detail-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  align-items: start;

  @media (max-width: 1024px) {
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
  gap: 8px;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

// ── 编辑表单 ──
.edit-form {
  :deep(.el-form-item) {
    margin-bottom: 14px;
  }

  :deep(.el-form-item__label) {
    padding-bottom: 2px;
    font-size: 13px;
    color: #64748b;
  }
}

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
}

// ── 输出内容 ──
.empty-output {
  padding: 20px 0;
}

.output-section {
  margin-bottom: 24px;

  &:last-child { margin-bottom: 0; }

  h3 {
    font-size: 15px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #f1f5f9;
  }
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    margin: 16px 0 8px 0;
  }
  p {
    margin: 0;
    line-height: 1.8;
    color: #475569;
    font-size: 14px;
  }
  ul {
    margin: 4px 0;
    padding-left: 20px;

    li {
      line-height: 1.8;
      color: #475569;
      font-size: 14px;
    }
  }
}

.persona-item {
  margin-bottom: 8px;
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #f1f5f9;

  .role {
    font-weight: 600;
    color: #1e293b;
    font-size: 14px;
  }
  .concerns {
    margin-top: 4px;
    font-size: 13px;
    color: #64748b;
  }
}

.raw-output {
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.7;
  color: #475569;
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}
</style>
