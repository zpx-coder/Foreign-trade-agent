<template>
  <AuthLayout subtitle="登录您的企业账户">
    <!-- 登录失败提示 -->
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
        <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" size="large" />
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
          {{ loading ? "登录中..." : "登 录" }}
        </el-button>
      </el-form-item>
      <div class="form-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
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
    await authStore.login(form.email, form.password);
    ElMessage.success("登录成功");
    router.push("/app/dashboard");
  } catch (err: any) {
    const detail = err?.response?.data?.detail || "";
    // 根据后端返回的不同错误给出中文提示
    if (detail.includes("密码") || detail.includes("password") || detail.includes("凭证")) {
      errorMessage.value = "邮箱或密码错误，请核对后重试";
    } else if (detail.includes("不存在") || detail.includes("用户")) {
      errorMessage.value = "该邮箱未注册，请先创建账号";
    } else if (detail.includes("禁用") || detail.includes("停用")) {
      errorMessage.value = "该账号已被停用，请联系管理员";
    } else if (detail.includes("租户") || detail.includes("企业")) {
      errorMessage.value = "企业账号异常，请联系客服";
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
