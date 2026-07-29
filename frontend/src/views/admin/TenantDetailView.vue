<template>
  <div class="page-tenant-detail">
    <div class="page-header">
      <el-button text @click="$router.push('/admin/tenants')">← 返回租户列表</el-button>
      <h2>{{ tenant.name }}</h2>
    </div>

    <!-- 基本信息 -->
    <el-card shadow="never" class="section-card">
      <template #header><span>基本信息</span></template>
      <el-descriptions :column="2" border v-loading="loading">
        <el-descriptions-item label="租户 ID">{{ tenant.id }}</el-descriptions-item>
        <el-descriptions-item label="租户名称">{{ tenant.name }}</el-descriptions-item>
        <el-descriptions-item label="套餐">
          <template v-if="editMode">
            <el-select v-model="editForm.plan_type" size="small" style="width:140px">
              <el-option label="免费版" value="free" />
              <el-option label="专业版" value="pro" />
              <el-option label="企业版" value="enterprise" />
            </el-select>
          </template>
          <el-tag v-else :type="planTag(tenant.plan_type)" size="small">{{ planLabel(tenant.plan_type) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <template v-if="editMode">
            <el-select v-model="editForm.status" size="small" style="width:140px">
              <el-option label="正常" value="active" />
              <el-option label="已停用" value="suspended" />
              <el-option label="已注销" value="cancelled" />
            </el-select>
          </template>
          <el-tag v-else :type="statTag(tenant.status)" size="small">{{ statLabel(tenant.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="入驻时间">{{ fmt(tenant.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ fmt(tenant.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <div class="actions-bar" style="margin-top:16px">
        <template v-if="editMode">
          <el-button type="primary" size="small" @click="saveTenant" :loading="saving">保存</el-button>
          <el-button size="small" @click="editMode = false">取消</el-button>
        </template>
        <el-button v-else type="primary" size="small" @click="startEdit">修改套餐/状态</el-button>
      </div>
    </el-card>

    <!-- 用户列表 -->
    <el-card shadow="never" class="section-card" style="margin-top:16px">
      <template #header><span>成员列表（{{ tenant.users?.length || 0 }} 人）</span></template>
      <el-table :data="tenant.users || []" stripe>
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="roleTag(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '已禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="180">
          <template #default="{ row }">{{ fmt(row.last_login_at) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 业务数据统计 -->
    <el-card shadow="never" class="section-card" style="margin-top:16px" v-loading="statsLoading">
      <template #header><span>业务数据统计</span></template>

      <!-- ICP 画像 -->
      <h4 class="stats-group-title">📊 客户画像</h4>
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num">{{ stats.icp.total }}</span><span class="stat-label">总数</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#67c23a">{{ stats.icp.completed }}</span><span class="stat-label">已完成</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#409eff">{{ stats.icp.generating }}</span><span class="stat-label">生成中</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#909399">{{ stats.icp.draft }}</span><span class="stat-label">草稿</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#f56c6c">{{ stats.icp.failed }}</span><span class="stat-label">失败</span></div>
        </el-col>
      </el-row>

      <!-- 客户 -->
      <h4 class="stats-group-title">👥 客户</h4>
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num">{{ stats.customer.total }}</span><span class="stat-label">总数</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#67c23a">{{ stats.customer.reached }}</span><span class="stat-label">已触达</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#409eff">{{ (stats.customer.reach_rate * 100).toFixed(1) }}%</span><span class="stat-label">触达率</span></div>
        </el-col>
        <el-col :span="12">
          <div class="stat-item stat-item--tags">
            <span class="stat-label">状态分布</span>
            <span class="stat-tags-wrap">
              <el-tag v-for="(cnt, st) in stats.customer.status_counts" :key="st" size="small" class="stat-tag">
                {{ custStatLabel(st) }} {{ cnt }}
              </el-tag>
            </span>
          </div>
        </el-col>
      </el-row>

      <!-- 邮件 -->
      <h4 class="stats-group-title">📧 邮件</h4>
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num">{{ stats.email.total_sent }}</span><span class="stat-label">已发送</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#409eff">{{ stats.email.total_opened }}</span><span class="stat-label">已打开</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#67c23a">{{ (stats.email.open_rate * 100).toFixed(1) }}%</span><span class="stat-label">打开率</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#e6a23c">{{ stats.email.total_replied }}</span><span class="stat-label">已回复</span></div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item"><span class="stat-num" style="color:#f56c6c">{{ (stats.email.reply_rate * 100).toFixed(1) }}%</span><span class="stat-label">回复率</span></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import api from "@/api/client";

interface UserInfo {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}
interface TenantDetail {
  id: string;
  name: string;
  plan_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  users: UserInfo[];
}

interface TenantStats {
  icp: { total: number; completed: number; generating: number; draft: number; failed: number };
  customer: { total: number; reached: number; reach_rate: number; status_counts: Record<string, number> };
  email: { total_sent: number; total_opened: number; open_rate: number; total_replied: number; reply_rate: number };
}

const route = useRoute();
const router = useRouter();
const tenant = ref<TenantDetail>({ id: "", name: "", plan_type: "free", status: "active", created_at: "", updated_at: "", users: [] });
const loading = ref(false);
const saving = ref(false);
const editMode = ref(false);
const editForm = reactive({ plan_type: "", status: "" });

const stats = ref<TenantStats>({
  icp: { total: 0, completed: 0, generating: 0, draft: 0, failed: 0 },
  customer: { total: 0, reached: 0, reach_rate: 0, status_counts: {} },
  email: { total_sent: 0, total_opened: 0, open_rate: 0, total_replied: 0, reply_rate: 0 },
});
const statsLoading = ref(false);

const planMap: Record<string, string> = { free: "免费版", pro: "专业版", enterprise: "企业版" };
const planTagMap: Record<string, string> = { free: "info", pro: "warning", enterprise: "success" };
const statMap: Record<string, string> = { active: "正常", suspended: "已停用", cancelled: "已注销" };
const statTagMap: Record<string, string> = { active: "success", suspended: "warning", cancelled: "danger" };
const roleMap: Record<string, string> = { super_admin: "超管", admin: "管理员", sales: "销售", readonly: "只读" };
const roleTagMap: Record<string, string> = { super_admin: "danger", admin: "warning", sales: "success", readonly: "info" };

function planLabel(v: string) { return planMap[v] || v; }
function planTag(v: string) { return planTagMap[v] || "info"; }
function statLabel(v: string) { return statMap[v] || v; }
function statTag(v: string) { return statTagMap[v] || "info"; }
function roleLabel(v: string) { return roleMap[v] || v; }
function roleTag(v: string) { return roleTagMap[v] || "info"; }
function fmt(d: string | null) { return d ? new Date(d).toLocaleDateString("zh-CN") : "-"; }

const custStatLabelMap: Record<string, string> = {
  new: "新线索", contacted: "已联系", screened: "已筛选",
  negotiating: "洽谈中", deal: "已成交", lost: "已流失",
};
function custStatLabel(st: string) { return custStatLabelMap[st] || st; }

async function fetchStats() {
  statsLoading.value = true;
  try {
    const { data } = await api.get(`/admin/tenants/${route.params.id}/stats`);
    stats.value = data;
  } catch {
    // 无数据保持默认 0
  } finally {
    statsLoading.value = false;
  }
}

function startEdit() {
  editForm.plan_type = tenant.value.plan_type;
  editForm.status = tenant.value.status;
  editMode.value = true;
}

async function saveTenant() {
  saving.value = true;
  try {
    await api.put(`/admin/tenants/${route.params.id}`, {
      plan_type: editForm.plan_type,
      status: editForm.status,
    });
    // 合并响应，保留 users 数组不被覆盖
    tenant.value.plan_type = editForm.plan_type;
    tenant.value.status = editForm.status;
    editMode.value = false;
    ElMessage.success("保存成功");
  } catch {
    // handled by interceptor
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await api.get(`/admin/tenants/${route.params.id}`);
    tenant.value = data;
  } finally {
    loading.value = false;
  }
  fetchStats();
});
</script>

<style scoped>
.page-tenant-detail { padding: 0; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 8px 0 0; font-size: 22px; }
.section-card { border-radius: 8px; }
.actions-bar { display: flex; gap: 8px; }

.stats-group-title { margin: 0 0 12px; font-size: 15px; color: var(--el-text-color-primary); }
.stats-group-title:not(:first-child) { margin-top: 20px; }
.stats-row { margin-bottom: 8px; }
.stat-item { text-align: center; padding: 12px 8px; background: var(--el-fill-color-lighter); border-radius: 8px; }
.stat-num { display: block; font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-label { display: block; margin-top: 4px; font-size: 13px; color: var(--el-text-color-secondary); }
.stat-item--tags { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
.stat-tags-wrap { display: flex; flex-wrap: wrap; gap: 4px; }
.stat-tag { margin: 0; }
</style>
