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

    <el-form-item label="产品图片" prop="images">
      <!-- 已有产品：即时上传 -->
      <template v-if="productId">
        <ImageUpload
          v-model="form.images"
          :upload-url="`/products/${productId}/images`"
          label="产品图片"
          :max="6"
          hint="支持 PNG/JPEG/GIF/WebP，单张不超过 5MB"
        />
      </template>
      <!-- 新建产品：本地预选 + URL 输入，提交时一并上传 -->
      <template v-else>
        <div class="images-create-mode">
          <el-input
            v-model="imageUrlInput"
            placeholder="输入图片 URL 地址，按回车添加"
            maxlength="512"
            @blur="addImageUrl"
            @keyup.enter="addImageUrl"
          />
          <div v-if="form.images.length || localPreviews.length" class="images-preview-grid">
            <!-- URL 图片 -->
            <div v-for="(url, idx) in form.images" :key="'url-' + idx" class="images-preview-item">
              <img :src="url" class="images-preview-img" />
              <div class="images-preview-actions">
                <el-button circle size="small" type="danger" :icon="Delete" @click="removeUrlImage(idx)" />
              </div>
            </div>
            <!-- 本地文件预览 -->
            <div v-for="(preview, idx) in localPreviews" :key="'local-' + idx" class="images-preview-item">
              <img :src="preview" class="images-preview-img" />
              <div class="images-preview-actions">
                <el-button circle size="small" type="danger" :icon="Delete" @click="removeLocalFile(idx)" />
              </div>
            </div>
          </div>
          <div v-if="totalImageCount < 6" class="images-create-trigger" @click="triggerLocalUpload">
            <el-icon :size="22"><Plus /></el-icon>
            <span>上传本地图片（PNG/JPEG/GIF/WebP，≤5MB）</span>
          </div>
          <input ref="localFileInputRef" type="file" accept="image/png,image/jpeg,image/gif,image/webp" multiple style="display: none" @change="handleLocalFileChange" />
        </div>
      </template>
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
import { ref, reactive, computed, watch, onBeforeUnmount } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { Delete, Plus } from "@element-plus/icons-vue";
import ImageUpload from "@/components/common/ImageUpload.vue";

interface ProductFormData {
  name: string;
  description: string;
  category: string;
  hs_code: string;
  price_usd: number | undefined;
  moq: number | undefined;
  image_url: string;
  images: string[];
  is_active: boolean;
}

const props = withDefaults(
  defineProps<{
    initial?: Partial<ProductFormData>;
    saving?: boolean;
    showActive?: boolean;
    productId?: string;
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
      images: [] as string[],
      is_active: true,
    }),
    saving: false,
    showActive: false,
    productId: "",
  }
);

const emit = defineEmits<{
  submit: [data: Record<string, unknown>, files?: File[]];
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
  images: [],
  is_active: true,
});

const imageUrlInput = ref("");

// ── 本地文件预选（新建产品时使用，提交后批量上传）──
const pendingFiles = ref<File[]>([]);
const localPreviews = ref<string[]>([]);
const localFileInputRef = ref<HTMLInputElement>();

const totalImageCount = computed(() => form.images.length + localPreviews.value.length);

function triggerLocalUpload() {
  localFileInputRef.value?.click();
}

function handleLocalFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const files = input.files;
  if (!files || files.length === 0) return;

  const errors: string[] = [];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];

    if (!file.type.startsWith("image/")) {
      errors.push(`${file.name}: 请选择图片文件`);
      continue;
    }
    if (file.size > 5 * 1024 * 1024) {
      errors.push(`${file.name}: 图片大小超过 5MB`);
      continue;
    }

    pendingFiles.value.push(file);
    localPreviews.value.push(URL.createObjectURL(file));
  }

  // 重置 input 以允许重复选择同一文件
  if (input) input.value = "";

  if (errors.length > 0) {
    ElMessage.error(errors.slice(0, 3).join("；"));
  }
}

function removeLocalFile(idx: number) {
  pendingFiles.value.splice(idx, 1);
  URL.revokeObjectURL(localPreviews.value[idx]);
  localPreviews.value.splice(idx, 1);
}

function removeUrlImage(idx: number) {
  form.images.splice(idx, 1);
}

// 清理 blob URL 防止内存泄漏
onBeforeUnmount(() => {
  localPreviews.value.forEach((url) => URL.revokeObjectURL(url));
});

// 初始化表单数据
watch(
  () => props.initial,
  (val) => {
    const defaults: ProductFormData = {
      name: "", description: "", category: "", hs_code: "",
      price_usd: undefined, moq: undefined, image_url: "", images: [], is_active: true,
    };
    Object.assign(form, { ...defaults, ...val });
  },
  { immediate: true, deep: true }
);

function addImageUrl() {
  const url = imageUrlInput.value.trim();
  if (url && !form.images.includes(url)) {
    form.images.push(url);
  }
  imageUrlInput.value = "";
}

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
    images: form.images.length ? form.images : null,
  };

  if (props.showActive) {
    submitData.is_active = form.is_active;
  }

  // 清理空字符串
  Object.keys(submitData).forEach((key) => {
    if (submitData[key] === "") submitData[key] = null;
  });

  // 新建产品时附带本地文件，由父组件在创建后上传
  const files = props.productId ? undefined : pendingFiles.value.length > 0 ? [...pendingFiles.value] : undefined;
  emit("submit", submitData, files);
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

// ── 新建模式：本地图片 + URL 输入 ──
.images-create-mode {
  width: 100%;
}

.images-preview-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.images-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;

  &:hover .images-preview-actions {
    opacity: 1;
  }
}

.images-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.images-preview-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}

.images-create-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 10px 16px;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  color: #94a3b8;
  font-size: 13px;
  transition: all 0.15s;

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.04);
  }
}
</style>
