<template>
  <div class="icp-detail-page">
    <PageHeader :title="icp?.name || '画像详情'" :breadcrumb="[{ title: '客户画像', path: '/app/icps' }, { title: icp?.name || '详情' }]">
      <template #actions>
        <el-button v-if="icp?.status === 'draft' || icp?.status === 'failed'" type="primary" :loading="regenerating" @click="handleRegenerate">重新生成</el-button>
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
        <!-- 输入摘要 -->
        <el-card class="section-card">
          <template #header><span class="card-title">输入信息</span></template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="目标行业">{{ inputData.target_industry || "—" }}</el-descriptions-item>
            <el-descriptions-item label="目标地区">{{ inputData.target_region || "—" }}</el-descriptions-item>
            <el-descriptions-item label="公司规模">{{ inputData.company_size || "—" }}</el-descriptions-item>
            <el-descriptions-item label="产品品类">{{ inputData.product_category || "—" }}</el-descriptions-item>
            <el-descriptions-item label="价格区间">{{ inputData.product_price_range || "—" }}</el-descriptions-item>
            <el-descriptions-item label="客户预算">{{ inputData.customer_budget || "—" }}</el-descriptions-item>
            <el-descriptions-item label="产品优势">{{ inputData.product_features || "—" }}</el-descriptions-item>
            <el-descriptions-item label="客户痛点">{{ inputData.pain_points || "—" }}</el-descriptions-item>
            <el-descriptions-item label="决策者">{{ inputData.decision_makers || "—" }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- AI 输出 -->
        <el-card v-if="!icp.output_data?.parse_error" class="section-card">
          <template #header><span class="card-title">AI 画像报告</span></template>

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
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import { useIcpStore } from "@/stores/icp";
import type { IcpItem } from "@/stores/icp";

const route = useRoute();
const icpStore = useIcpStore();
const icp = ref<IcpItem | null>(null);
const loading = ref(true);
const loadError = ref("");
const regenerating = ref(false);

const inputData = computed(() => icp.value?.input_data || {});
const output = computed(() => (icp.value?.output_data as Record<string, unknown>) || {});

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

async function handleRegenerate() {
  regenerating.value = true;
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";
    const resp = await fetch(`${baseUrl}/icps/${route.params.id}/generate`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: "请求失败" }));
      throw new Error(err.detail || "请求失败");
    }
    // 读取 SSE 流直到完成（避免资源泄漏）
    const reader = resp.body?.getReader();
    if (reader) {
      const decoder = new TextDecoder();
      while (true) {
        const { done } = await reader.read();
        if (done) break;
      }
    }
    ElMessage.success("重新生成完成，正在刷新...");
    setTimeout(() => loadData(), 500);
  } catch (err: any) {
    ElMessage.error(err.message || "触发失败");
  } finally {
    regenerating.value = false;
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

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
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
