<template>
  <div class="page-settings">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 个人信息 -->
      <el-tab-pane label="个人信息" name="profile">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ authStore.user?.name }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ authStore.user?.email }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ roleLabel(authStore.user?.role) }}</el-descriptions-item>
          <el-descriptions-item label="租户">{{ authStore.tenant?.name }}</el-descriptions-item>
          <el-descriptions-item label="套餐">{{ planLabel(authStore.tenant?.plan_type) }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>

      <!-- Tab 2: 修改密码 -->
      <el-tab-pane label="修改密码" name="password">
        <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-width="120px" style="max-width:480px">
          <el-form-item label="旧密码" prop="old_password">
            <el-input v-model="pwdForm.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="pwdForm.new_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input v-model="pwdForm.confirm_password" type="password" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePassword" :loading="pwdLoading">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- Tab 3: 默认 SMTP 配置 -->
      <el-tab-pane label="默认 SMTP 配置" name="smtp">
        <div v-if="smtpLoadingData" v-loading="smtpLoadingData" style="min-height:120px" />
        <el-alert v-else-if="smtpLoadError" :title="smtpLoadError" type="error" show-icon style="margin-bottom:16px" />
        <template v-else>
          <el-alert type="info" :closable="false" style="margin-bottom:20px">
            <template #title>
              请填写<strong>用于发送邮件的外部邮箱</strong>的 SMTP 连接信息，并非您当前登录账号的密码
            </template>
            <template #default>
              常用邮箱 SMTP 配置参考：
              Gmail：smtp.gmail.com，端口 465（SSL），需使用「应用专用密码」；
              QQ 邮箱：smtp.qq.com，端口 465（SSL），需使用「授权码」；
              163 邮箱：smtp.163.com，端口 465（SSL），需使用「授权码」
            </template>
          </el-alert>
          <el-form :model="smtpForm" label-width="140px" style="max-width:560px">
            <el-form-item label="SMTP 服务器地址">
              <el-input v-model="smtpForm.host" placeholder="smtp.gmail.com" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input-number v-model="smtpForm.port" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="发件邮箱地址">
              <el-input v-model="smtpForm.username" placeholder="your-email@gmail.com" />
              <div class="form-extra">用于登录 SMTP 服务器的邮箱账号</div>
            </el-form-item>
            <el-form-item label="邮箱授权码">
              <el-input
                v-model="smtpForm.password"
                :type="showSmtpPassword ? 'text' : 'password'"
                :placeholder="hasSavedSmtp ? '已保存授权码，留空则不修改' : '邮箱服务商生成的授权码，非邮箱登录密码'"
              >
                <template #suffix>
                  <el-icon class="pwd-toggle-icon" @click.stop="showSmtpPassword = !showSmtpPassword">
                    <component :is="showSmtpPassword ? Hide : View" />
                  </el-icon>
                </template>
              </el-input>
              <div class="form-extra">
                <template v-if="hasSavedSmtp">已保存授权码，如需修改请重新输入，留空则保留原授权码不变</template>
                <template v-else>不是邮箱登录密码，是 SMTP 专用授权码/应用专用密码</template>
              </div>
            </el-form-item>
            <el-form-item label="发件人名称">
              <el-input v-model="smtpForm.from_name" placeholder="如：张三 / ABC Company" />
              <div class="form-extra">收件人看到的发件人名称，发件邮箱即为认证邮箱地址</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSmtp" :loading="smtpLoading">保存配置</el-button>
            </el-form-item>
          </el-form>
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { View, Hide } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/api/client";

const authStore = useAuthStore();
const activeTab = ref("profile");

const roleMap: Record<string, string> = { super_admin: "超管", admin: "管理员", sales: "销售", readonly: "只读" };
const planMap: Record<string, string> = { free: "免费版", pro: "专业版", enterprise: "企业版" };
function roleLabel(r?: string) { return roleMap[r || ""] || r || "-"; }
function planLabel(p?: string) { return planMap[p || ""] || p || "-"; }

// ── 密码修改 ──
const pwdFormRef = ref<FormInstance>();
const pwdLoading = ref(false);
const pwdForm = reactive({ old_password: "", new_password: "", confirm_password: "" });
const validateConfirm = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (value !== pwdForm.new_password) callback(new Error("两次输入的新密码不一致"));
  else callback();
};
const pwdRules: FormRules = {
  old_password: [{ required: true, message: "请输入旧密码", trigger: "blur" }],
  new_password: [{ required: true, min: 8, message: "新密码至少 8 位", trigger: "blur" }],
  confirm_password: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    { validator: validateConfirm, trigger: "blur" },
  ],
};

async function changePassword() {
  const valid = await pwdFormRef.value?.validate().catch(() => false);
  if (!valid) return;
  pwdLoading.value = true;
  try {
    await api.post("/auth/change-password", { ...pwdForm });
    ElMessage.success("密码已修改，下次登录时请使用新密码");
    pwdForm.old_password = "";
    pwdForm.new_password = "";
    pwdForm.confirm_password = "";
  } finally {
    pwdLoading.value = false;
  }
}

// ── SMTP 配置 ──
const smtpLoading = ref(false);
const smtpLoadError = ref("");
const smtpLoadingData = ref(false);
const showSmtpPassword = ref(false);
const hasSavedSmtp = ref(false);
const smtpForm = reactive({
  host: "smtp.gmail.com",
  port: 465,
  username: "",
  password: "",
  from_name: "",
});

async function loadSmtp() {
  smtpLoadingData.value = true;
  smtpLoadError.value = "";
  try {
    const { data } = await api.get("/settings/smtp");
    smtpForm.host = data.host;
    smtpForm.port = data.port;
    smtpForm.username = data.username;
    smtpForm.password = "";  // 密码不可逆，不返回
    smtpForm.from_name = data.from_name;
    // 有 host + username 即表示已配置 SMTP（密码已加密存储，不可查看）
    hasSavedSmtp.value = !!(data.host && data.username);
  } catch (err: any) {
    hasSavedSmtp.value = false;
    if (err?.response?.status !== 404) {
      smtpLoadError.value = "加载 SMTP 配置失败";
    }
    // 404 表示尚无配置，使用默认值即可
  } finally {
    smtpLoadingData.value = false;
  }
}

async function saveSmtp() {
  smtpLoading.value = true;
  try {
    await api.put("/settings/smtp", { ...smtpForm });
    ElMessage.success("SMTP 配置已保存");
    hasSavedSmtp.value = true;
  } catch {
    // 错误提示已由 API 拦截器统一处理
  } finally {
    smtpLoading.value = false;
  }
}

loadSmtp();
</script>

<style scoped>
.page-settings { padding: 0; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 22px; }
.form-extra {
  font-size: 12px; color: #94a3b8; margin-top: 2px;
}
.pwd-toggle-icon {
  cursor: pointer; color: #94a3b8; font-size: 16px;
  &:hover { color: #3b82f6; }
}
</style>
