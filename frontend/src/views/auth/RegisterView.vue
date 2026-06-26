<template>
  <AuthLayout subtitle="创建您的企业账户">
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="true"
      class="error-alert"
      @close="errorMessage = ''"
    />

    <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister">
      <el-form-item prop="name">
        <el-input v-model="form.name" placeholder="您的姓名" prefix-icon="User" size="large" />
      </el-form-item>
      <el-form-item prop="company_name">
        <el-input v-model="form.company_name" placeholder="企业名称" prefix-icon="OfficeBuilding" size="large" />
      </el-form-item>
      <el-form-item prop="email">
        <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" size="large" @input="errorMessage = ''" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="密码（至少 8 位）"
          prefix-icon="Lock"
          size="large"
          show-password
          @input="onPasswordChange"
        />
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="确认密码"
          prefix-icon="Lock"
          size="large"
          show-password
          @input="errorMessage = ''"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" native-type="submit" class="w-full">
          {{ loading ? "注册中..." : "注 册" }}
        </el-button>
      </el-form-item>
      <div class="form-footer">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </el-form>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { type FormInstance, type FormRules, ElMessage } from "element-plus";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const formRef = ref<FormInstance>();
const loading = ref(false);
const errorMessage = ref("");

const form = reactive({
  name: "",
  company_name: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error("请再次输入密码"));
  } else if (value !== form.password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const rules: FormRules = {
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  company_name: [{ required: true, message: "请输入企业名称", trigger: "blur" }],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 8, message: "密码至少 8 位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: "blur" },
  ],
};

// 密码变更时重新校验确认密码
function onPasswordChange() {
  errorMessage.value = "";
  formRef.value?.validateField("confirmPassword");
}

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  loading.value = true;
  errorMessage.value = "";
  try {
    await authStore.register(form);
    ElMessage.success("注册成功，欢迎加入！");
    router.push("/app/dashboard");
  } catch (err: any) {
    const detail = err?.response?.data?.detail || "";
    if (detail.includes("已存在") || detail.includes("已注册") || detail.includes("duplicate")) {
      errorMessage.value = "该邮箱已注册，请直接登录";
    } else {
      errorMessage.value = detail || "注册失败，请稍后重试";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped lang="scss">
.w-full {
  width: 100%;
}
.error-alert {
  margin-bottom: 16px;
}
.form-footer {
  text-align: center;
  font-size: 13px;
  color: #909399;
  a {
    color: #1e6fff;
  }
}
</style>
