<template>
  <div class="icp-list-page">
    <PageHeader title="客户画像">
      <template #actions>
        <el-button type="primary" size="large" @click="$router.push('/app/icps/create')">
          <el-icon><Plus /></el-icon>新建画像
        </el-button>
      </template>
    </PageHeader>

    <!-- 统计卡片 -->
    <div class="stat-bar">
      <div class="stat-item">
        <span class="stat-num">{{ icpStats.total }}</span>
        <span class="stat-label">全部画像</span>
      </div>
      <div class="stat-item stat-item--done">
        <span class="stat-num">{{ icpStats.completed }}</span>
        <span class="stat-label">已完成</span>
      </div>
      <div class="stat-item stat-item--progress">
        <span class="stat-num">{{ icpStats.generating }}</span>
        <span class="stat-label">生成中</span>
      </div>
      <div class="stat-item stat-item--draft">
        <span class="stat-num">{{ icpStats.draft }}</span>
        <span class="stat-label">草稿</span>
      </div>
      <div class="stat-item stat-item--fail">
        <span class="stat-num">{{ icpStats.failed }}</span>
        <span class="stat-label">失败</span>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" @change="handleFilter">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="completed">已完成</el-radio-button>
        <el-radio-button value="generating">生成中</el-radio-button>
        <el-radio-button value="draft">草稿</el-radio-button>
        <el-radio-button value="failed">失败</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 表格 -->
    <el-card class="table-card">
      <el-alert v-if="error" :title="error" type="error" show-icon class="page-alert" @close="error = ''" />
      <LoadingSkeleton v-if="loading" variant="table" />
      <EmptyState v-else-if="!icpList.length" description="暂无客户画像" action-text="创建第一个画像" @action="$router.push('/app/icps/create')" />
      <template v-else>
        <el-table :data="icpList" stripe @row-click="goDetail">
          <el-table-column prop="name" label="画像名称" min-width="240">
            <template #default="{ row }">
              <span class="icp-name">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }"><StatusBadge :status="row.status" /></template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">{{ new Date(row.created_at).toLocaleString("zh-CN") }}</template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click.stop="goDetail(row)">查看</el-button>
              <el-button link type="danger" size="small" @click.stop="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="loadData"
          />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import { useIcpStore } from "@/stores/icp";
import type { IcpItem } from "@/stores/icp";
import api from "@/api/client";

const router = useRouter();
const icpStore = useIcpStore();
const icpList = ref<IcpItem[]>([]);
const total = ref(0);
const loading = ref(true);
const error = ref("");
const page = ref(1);
const pageSize = 20;
const statusFilter = ref("");
const icpStats = ref({ total: 0, completed: 0, generating: 0, draft: 0, failed: 0 });

async function loadStats() {
  try {
    const { data } = await api.get("/dashboard/stats");
    icpStats.value = {
      total: data.total_icps || 0,
      completed: data.completed_icps || 0,
      generating: data.generating_icps || 0,
      draft: data.draft_icps || 0,
      failed: data.failed_icps || 0,
    };
  } catch { /* */ }
}

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: pageSize };
    if (statusFilter.value) params.status = statusFilter.value;
    await icpStore.fetchList(params);
    icpList.value = icpStore.list;
    total.value = icpStore.total;
  } catch (err: any) {
    error.value = err?.response?.data?.detail || "加载失败";
  } finally { loading.value = false; }
}

function handleFilter() { page.value = 1; loadData(); }
function goDetail(row: IcpItem) { router.push(`/app/icps/${row.id}`); }

async function handleDelete(row: IcpItem) {
  try {
    await ElMessageBox.confirm(`确定删除画像「${row.name}」？`, "删除确认", { confirmButtonText: "删除", cancelButtonText: "取消", type: "warning" });
    await icpStore.remove(row.id);
    ElMessage.success("已删除");
    loadData();
  } catch { /* cancelled */ }
}

onMounted(() => { loadData(); loadStats(); });
</script>

<style scoped lang="scss">
// ── 统计卡片 ──
.stat-bar {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.stat-item {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 20px;
  text-align: center;
  transition: box-shadow 0.2s;
  &:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
  .stat-num { display: block; font-size: 28px; font-weight: 800; color: #0f172a; font-family: "Inter", sans-serif; }
  .stat-label { display: block; font-size: 13px; color: #64748b; margin-top: 2px; }
  &--done { border-left: 3px solid #10b981; .stat-num { color: #10b981; } }
  &--progress { border-left: 3px solid #f59e0b; .stat-num { color: #f59e0b; } }
  &--draft { border-left: 3px solid #94a3b8; .stat-num { color: #94a3b8; } }
  &--fail { border-left: 3px solid #ef4444; .stat-num { color: #ef4444; } }
}

.filter-bar {
  margin-bottom: 16px;
}

.table-card {
  border-radius: 14px;
  border: 1px solid #e2e8f0;

  :deep(.el-card__body) {
    padding: 0;
  }

  :deep(.el-table) {
    --el-table-header-bg-color: #f8fafc;
    --el-table-row-hover-bg-color: #f8fafc;

    th {
      font-weight: 600;
      color: #64748b;
      font-size: 13px;
      border-bottom: 1px solid #e2e8f0;
    }
    td {
      border-bottom: 1px solid #f1f5f9;
    }
  }
}

.icp-name {
  font-weight: 600;
  cursor: pointer;
  color: #2563eb;

  &:hover {
    color: #1d4ed8;
  }
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
}
</style>
