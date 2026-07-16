<template>
  <div class="campaign-detail-page">
    <PageHeader :title="campaign?.name || '任务详情'" :breadcrumb="[{title:'发送任务', path:'/app/email/campaigns'}, {title:'详情'}]">
      <template #actions>
        <el-button v-if="campaign?.status === 'draft'" type="primary" @click="handleSend">立即发送</el-button>
        <el-button v-if="campaign?.status === 'sending'" type="warning" @click="handlePause">暂停发送</el-button>
        <el-button v-if="campaign?.status === 'paused'" type="primary" @click="handleSend">继续发送</el-button>
        <el-button @click="$router.push('/app/email/campaigns')">返回列表</el-button>
      </template>
    </PageHeader>

    <LoadingSkeleton v-if="loading" variant="detail" />
    <template v-else-if="campaign">
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4"><el-card shadow="never" class="stat-card"><div class="stat-num">{{ campaign.total_recipients }}</div><div class="stat-label">总收件人</div></el-card></el-col>
        <el-col :span="4"><el-card shadow="never" class="stat-card"><div class="stat-num">{{ campaign.sent_count }}</div><div class="stat-label">已发送</div></el-card></el-col>
        <el-col :span="4"><el-card shadow="never" class="stat-card"><div class="stat-num">{{ campaign.opened_count }}</div><div class="stat-label">已打开</div></el-card></el-col>
        <el-col :span="4"><el-card shadow="never" class="stat-card"><div class="stat-num">{{ campaign.bounced_count }}</div><div class="stat-label">退信</div></el-card></el-col>
        <el-col :span="8">
          <el-card shadow="never" class="stat-card">
            <div class="stat-label">发送进度</div>
            <el-progress v-if="campaign.total_recipients > 0"
              :percentage="Math.round(campaign.sent_count / campaign.total_recipients * 100)"
              :status="campaign.status === 'completed' ? 'success' : campaign.status === 'failed' ? 'exception' : undefined"
              :stroke-width="16" style="margin-top:8px" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 状态 & 时间 -->
      <el-card class="info-card">
        <el-descriptions :column="4" size="small">
          <el-descriptions-item label="状态"><StatusBadge :status="campaign.status" /></el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ new Date(campaign.created_at).toLocaleString("zh-CN") }}</el-descriptions-item>
          <el-descriptions-item label="开始发送">{{ campaign.started_at ? new Date(campaign.started_at).toLocaleString("zh-CN") : "—" }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ campaign.completed_at ? new Date(campaign.completed_at).toLocaleString("zh-CN") : "—" }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 发送日志 -->
      <el-card class="table-card">
        <template #header><span>发送日志</span></template>
        <el-table :data="sendLogs" stripe max-height="500">
          <el-table-column prop="recipient_email" label="收件人" min-width="200" />
          <el-table-column prop="subject" label="邮件主题" min-width="180" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }"><StatusBadge :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="opened_at" label="打开时间" width="160">
            <template #default="{ row }">{{ row.opened_at ? new Date(row.opened_at).toLocaleString("zh-CN") : "—" }}</template>
          </el-table-column>
          <el-table-column prop="error_message" label="备注" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">{{ row.error_message || "—" }}</template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import { useEmailStore, type CampaignDetail, type SendLogItem } from "@/stores/email";

const route = useRoute();
const store = useEmailStore();
const loading = ref(true);
const campaign = ref<CampaignDetail | null>(null);
const sendLogs = ref<SendLogItem[]>([]);
const pollTimer = ref<ReturnType<typeof setInterval> | null>(null);

async function loadDetail() {
  const id = route.params.id as string;
  try {
    campaign.value = await store.fetchCampaign(id);
    sendLogs.value = campaign.value.send_logs || [];
  } catch { /* */ }
  finally { loading.value = false; }
}

function startPolling() {
  if (pollTimer.value) return;
  pollTimer.value = setInterval(async () => {
    if (campaign.value?.status === "sending") {
      await loadDetail();
    } else if (pollTimer.value) {
      clearInterval(pollTimer.value);
      pollTimer.value = null;
    }
  }, 5000);
}

async function handleSend() {
  const id = route.params.id as string;
  try {
    await store.sendCampaign(id);
    ElMessage.success("发送已启动");
    await loadDetail();
    startPolling();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "启动失败"); }
}

async function handlePause() {
  const id = route.params.id as string;
  try {
    await store.pauseCampaign(id);
    ElMessage.success("已暂停");
    await loadDetail();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "暂停失败"); }
}

onMounted(async () => {
  await loadDetail();
  if (campaign.value?.status === "sending") startPolling();
});
onUnmounted(() => { if (pollTimer.value) clearInterval(pollTimer.value); });
</script>

<style scoped lang="scss">
.campaign-detail-page {
  .stats-row { margin-bottom: 16px; }
  .stat-card { text-align: center; border-radius: 12px; }
  .stat-num { font-size: 28px; font-weight: 700; color: #1e293b; }
  .stat-label { font-size: 13px; color: #94a3b8; margin-top: 4px; }
  .info-card { margin-bottom: 16px; border-radius: 12px; }
  .table-card { border-radius: 14px; border: 1px solid #e2e8f0; }
}
</style>
