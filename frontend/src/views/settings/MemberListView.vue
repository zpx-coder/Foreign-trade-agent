<template>
  <div class="page-members">
    <div class="page-header">
      <div>
        <h2>成员管理</h2>
        <p class="page-desc">管理团队成员及其权限</p>
      </div>
      <el-button v-if="authStore.canManageMembers" type="primary" @click="showInvite = true">
        + 邀请成员
      </el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="140">
          <template #default="{ row }">
            <template v-if="canEditRole(row)">
              <el-select
                :model-value="row.role"
                @change="(val: string) => updateRole(row, val)"
                size="small"
                style="width:100px"
              >
                <el-option label="销售" value="sales" />
                <el-option label="只读" value="readonly" />
                <el-option v-if="authStore.userRole === 'super_admin'" label="管理员" value="admin" />
              </el-select>
            </template>
            <el-tag v-else :type="roleTag(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
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
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canDisable(row)"
              text
              type="danger"
              size="small"
              @click="disableMember(row)"
            >禁用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 邀请弹窗 -->
    <el-dialog v-model="showInvite" title="邀请成员" width="460px" :close-on-click-modal="false">
      <el-form :model="inviteForm" :rules="inviteRules" ref="inviteFormRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="inviteForm.name" placeholder="成员姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="inviteForm.email" placeholder="成员邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="inviteForm.password" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="inviteForm.role" style="width:100%">
            <el-option label="销售" value="sales" />
            <el-option label="只读" value="readonly" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInvite = false">取消</el-button>
        <el-button type="primary" @click="doInvite" :loading="inviting">确认邀请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import api from "@/api/client";

interface MemberRow {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
}

const authStore = useAuthStore();
const list = ref<MemberRow[]>([]);
const loading = ref(false);

const roleMap: Record<string, string> = { super_admin: "超管", admin: "管理员", sales: "销售", readonly: "只读" };
const roleTagMap: Record<string, string> = { super_admin: "danger", admin: "warning", sales: "success", readonly: "info" };
function roleLabel(r: string) { return roleMap[r] || r; }
function roleTag(r: string) { return roleTagMap[r] || "info"; }
function fmt(d: string | null) { return d ? new Date(d).toLocaleDateString("zh-CN") : "-"; }

function canEditRole(row: MemberRow) {
  if (row.role === "super_admin") return false;
  if (authStore.userRole === "super_admin") return true;
  if (authStore.userRole === "admin" && row.role !== "admin") return true;
  return false;
}
function canDisable(row: MemberRow) {
  if (row.role === "super_admin") return false;
  if (row.id === authStore.user?.id) return false;
  return authStore.canManageMembers;
}

async function fetchMembers() {
  loading.value = true;
  try {
    const { data } = await api.get("/members");
    list.value = data.items;
  } finally {
    loading.value = false;
  }
}

async function updateRole(row: MemberRow, newRole: string) {
  const oldRole = row.role;
  try {
    await api.put(`/members/${row.id}`, { role: newRole });
    row.role = newRole;
    ElMessage.success("角色已更新");
  } catch {
    // 失败时回退角色显示
    row.role = oldRole;
    ElMessage.error("角色更新失败");
  }
}

async function disableMember(row: MemberRow) {
  try {
    await ElMessageBox.confirm(
      `确定要禁用成员「${row.name}」吗？禁用后该成员将无法登录。`,
      "确认禁用",
      { confirmButtonText: "确定禁用", cancelButtonText: "取消", type: "warning" },
    );
  } catch {
    return;
  }
  try {
    await api.put(`/members/${row.id}`, { is_active: false });
    row.is_active = false;
    ElMessage.success("成员已禁用");
  } catch {
    ElMessage.error("操作失败");
  }
}

// ── 邀请 ──
const showInvite = ref(false);
const inviting = ref(false);
const inviteFormRef = ref<FormInstance>();
const inviteForm = reactive({ name: "", email: "", password: "", role: "sales" });
const inviteRules: FormRules = {
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
  password: [{ required: true, min: 8, message: "密码至少 8 位", trigger: "blur" }],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
};

async function doInvite() {
  const valid = await inviteFormRef.value?.validate().catch(() => false);
  if (!valid) return;
  inviting.value = true;
  try {
    await api.post("/members/invite", { ...inviteForm });
    ElMessage.success("成员已邀请");
    showInvite.value = false;
    inviteForm.name = "";
    inviteForm.email = "";
    inviteForm.password = "";
    inviteForm.role = "sales";
    await fetchMembers();
  } finally {
    inviting.value = false;
  }
}

onMounted(() => fetchMembers());
</script>

<style scoped>
.page-members { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 22px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 14px; }
.table-card { border-radius: 8px; }
</style>
