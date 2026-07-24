<template>
  <AuthLayout>
    <!-- 登录方式切换 tab -->
    <div class="auth-tabs">
      <button class="auth-tab auth-tab--active">邮箱登录</button>
      <!-- 预留：手机号登录 -->
      <!-- <button class="auth-tab">手机登录</button> -->
    </div>

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
        <el-input
          v-model="form.email"
          placeholder="请输入邮箱地址"
          prefix-icon="Message"
          size="large"
          @input="errorMessage = ''"
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          prefix-icon="Lock"
          size="large"
          show-password
          @input="errorMessage = ''"
        />
      </el-form-item>

      <!-- 忘记密码 -->
      <a class="auth-forgot" @click.prevent>忘记密码？</a>

      <el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          native-type="submit"
          class="auth-submit-btn"
        >
          {{ loading ? "登录中..." : "登 录" }}
        </el-button>
      </el-form-item>

      <div class="auth-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>

      <!-- 第三方登录 -->
      <div class="auth-divider">其他方式登录</div>
      <div class="auth-social">
        <div class="auth-social__icon" title="微信登录">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.5 11a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3Zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3Zm-6.95 4.5c.9 1.5 2.6 2.5 4.5 2.5.5 0 1-.1 1.45-.25l1.55.8-.4-1.4c1-.7 1.65-1.8 1.65-3 0-2.2-2-4-4.4-4-2.45 0-4.4 1.8-4.4 4 0 .55.15 1.1.4 1.55l-.35 1.3Zm11.05-.5c0-1.5-1.3-2.75-3-3.2A4.5 4.5 0 0 0 12.4 8C9.35 8 6.85 10.1 6.85 12.7c0 1.45.7 2.75 1.8 3.6l-.45 1.75 1.9-.95a5.7 5.7 0 0 0 2.3.5c2.55 0 4.65-1.6 5.1-3.7.35.1.7.15 1.1.15A3.4 3.4 0 0 0 22 10.65c0-1.7-1.4-3.1-3.15-3.1-.2 0-.4 0-.6.05.1.35.15.75.15 1.15 0 2.5-2.05 4.55-4.55 4.55-.35 0-.7-.05-1-.1.35 1.1 1.4 1.95 2.7 1.95.35 0 .7-.05 1.05-.15l1.45.75-.35-1.05c.8-.55 1.3-1.4 1.3-2.35Z" fill="#07C160"/>
          </svg>
        </div>
        <div class="auth-social__icon" title="Google 登录">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1Z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23Z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62Z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53Z" fill="#EA4335"/>
          </svg>
        </div>
        <div class="auth-social__icon" title="Apple 登录">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.5-3.24 0-1.44.62-2.2.44-3.06-.4C4.25 17.15 4.9 9.63 9.06 9.33c1 .05 1.7.55 2.28.55.56 0 1.62-.68 2.72-.58 1.16.1 2.03.56 2.6 1.4-2.36 1.42-1.8 4.54.37 5.42-.43 1.16-.99 2.3-1.98 3.16ZM12.03 9.25c-.15-2.23 1.66-4.07 3.74-4.25.3 2.08-1.8 4.07-3.74 4.25Z" fill="#1d1d1f"/>
          </svg>
        </div>
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
    { required: true, message: "请输入邮箱地址", trigger: "blur" },
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
.error-alert {
  margin-bottom: 20px;
}
</style>
