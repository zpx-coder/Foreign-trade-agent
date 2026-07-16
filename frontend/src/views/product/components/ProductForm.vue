<template>
  <el-form
    ref="elFormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    class="product-form"
  >
    <el-row :gutter="24">
      <el-col :span="16">
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入产品名称" maxlength="255" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="产品分类" prop="category">
          <el-input v-model="form.category" placeholder="如：电子产品" maxlength="100" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="产品描述" prop="description">
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="3"
        placeholder="描述产品特性、规格、材质等"
        maxlength="2000"
        show-word-limit
      />
    </el-form-item>

    <el-row :gutter="24">
      <el-col :span="8">
        <el-form-item label="价格 (USD)" prop="price_usd">
          <el-input-number
            v-model="form.price_usd"
            :precision="2"
            :min="0"
            :max="999999.99"
            :controls="false"
            placeholder="0.00"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="起订量 (MOQ)" prop="moq">
          <el-input-number
            v-model="form.moq"
            :min="1"
            :max="999999"
            :controls="false"
            placeholder="最小起订量"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="HS 编码" prop="hs_code">
          <el-input v-model="form.hs_code" placeholder="海关编码" maxlength="20" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="产品图片 URL" prop="image_url">
      <el-input v-model="form.image_url" placeholder="https://example.com/image.jpg" maxlength="512" />
    </el-form-item>

    <el-form-item v-if="showActive" label="上架状态" prop="is_active">
      <el-switch v-model="form.is_active" active-text="已上架" inactive-text="已下架" />
    </el-form-item>

    <el-form-item class="form-actions">
      <el-button type="primary" :loading="saving" @click="handleSubmit">
        {{ saving ? "保存中..." : "保存" }}
      </el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from "vue";
import { type FormInstance, type FormRules } from "element-plus";

interface ProductFormData {
  name: string;
  description: string;
  category: string;
  hs_code: string;
  price_usd: number | undefined;
  moq: number | undefined;
  image_url: string;
  is_active: boolean;
}

const props = withDefaults(
  defineProps<{
    initial?: ProductFormData;
    saving?: boolean;
    showActive?: boolean;
  }>(),
  {
    initial: () => ({
      name: "",
      description: "",
      category: "",
      hs_code: "",
      price_usd: undefined,
      moq: undefined,
      image_url: "",
      is_active: true,
    }),
    saving: false,
    showActive: false,
  }
);

const emit = defineEmits<{
  submit: [data: Record<string, unknown>];
  cancel: [];
}>();

const elFormRef = ref<FormInstance>();

const form = reactive<ProductFormData>({
  name: "",
  description: "",
  category: "",
  hs_code: "",
  price_usd: undefined,
  moq: undefined,
  image_url: "",
  is_active: true,
});

// 初始化表单数据
watch(
  () => props.initial,
  (val) => {
    Object.assign(form, val);
  },
  { immediate: true, deep: true }
);

const rules: FormRules = {
  name: [
    { required: true, message: "请输入产品名称", trigger: "blur" },
    { max: 255, message: "产品名称不超过 255 个字符", trigger: "blur" },
  ],
};

async function handleSubmit() {
  const valid = await elFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  const submitData: Record<string, unknown> = {
    name: form.name,
    description: form.description || null,
    category: form.category || null,
    hs_code: form.hs_code || null,
    price_usd: form.price_usd ?? null,
    moq: form.moq ?? null,
    image_url: form.image_url || null,
  };

  if (props.showActive) {
    submitData.is_active = form.is_active;
  }

  // 清理空字符串
  Object.keys(submitData).forEach((key) => {
    if (submitData[key] === "") submitData[key] = null;
  });

  emit("submit", submitData);
}
</script>

<script lang="ts">
export default {
  name: "ProductForm",
};
</script>

<style scoped lang="scss">
.product-form {
  max-width: 100%;
}

.form-actions {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;

  :deep(.el-form-item__content) {
    display: flex;
    gap: 12px;
  }
}
</style>
