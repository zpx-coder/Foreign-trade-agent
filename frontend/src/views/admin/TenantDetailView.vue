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

const route = useRoute();
const router = useRouter();
const tenant = ref<TenantDetail>({ id: "", name: "", plan_type: "free", status: "active", created_at: "", updated_at: "", users: [] });
const loading = ref(false);
const saving = ref(false);
const editMode = ref(false);
const editForm = reactive({ plan_type: "", status: "" });

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
});
</script>

<style scoped>
.page-tenant-detail { padding: 0; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 8px 0 0; font-size: 22px; }
.section-card { border-radius: 8px; }
.actions-bar { display: flex; gap: 8px; }
</style>
