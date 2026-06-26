<template>
  <AuthLayout subtitle="平台管理后台">
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      :closable="true"
      class="error-alert"
      @close="errorMessage = ''"
    />

    <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
      <el-form-item prop="email">
        <el-input v-model="form.email" placeholder="管理员邮箱" prefix-icon="Message" size="large" @input="errorMessage = ''" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="密码"
          prefix-icon="Lock"
          size="large"
          show-password
          @input="errorMessage = ''"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" native-type="submit" class="w-full">
          {{ loading ? "登录中..." : "管理员登录" }}
        </el-button>
      </el-form-item>
      <div class="form-footer">
        <span>企业用户？</span><router-link to="/login">返回用户登录</router-link>
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

const form = reactive({ email: "", password: "" });
const rules: FormRules = {
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" },
  ],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  loading.value = true;
  errorMessage.value = "";
  try {
    await authStore.adminLogin(form.email, form.password);
    ElMessage.success("管理员登录成功");
    router.push("/admin/dashboard");
  } catch (err: any) {
    const detail = err?.response?.data?.detail || "";
    if (detail.includes("密码") || detail.includes("password") || detail.includes("凭证")) {
      errorMessage.value = "邮箱或密码错误";
    } else if (detail.includes("不存在") || detail.includes("管理员")) {
      errorMessage.value = "该管理员账号不存在";
    } else if (detail.includes("禁用") || detail.includes("停用")) {
      errorMessage.value = "该管理员账号已被停用";
    } else {
      errorMessage.value = detail || "登录失败，请稍后重试";
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
