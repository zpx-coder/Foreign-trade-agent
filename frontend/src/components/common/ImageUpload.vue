<template>
  <div class="image-upload">
    <div class="image-upload__grid">
      <!-- 已上传图片 -->
      <div
        v-for="(url, idx) in modelValue"
        :key="url"
        class="image-upload__item"
      >
        <img :src="url" class="image-upload__img" />
        <div class="image-upload__actions">
          <el-button
            circle
            size="small"
            type="danger"
            :icon="Delete"
            @click="handleRemove(idx)"
          />
        </div>
      </div>

      <!-- 上传按钮 -->
      <div v-if="modelValue.length < max" class="image-upload__trigger" @click="triggerUpload">
        <el-icon :size="28"><Plus /></el-icon>
        <span class="trigger-text">上传{{ label }}</span>
      </div>
    </div>

    <input
      ref="fileInputRef"
      type="file"
      :accept="accept"
      multiple
      style="display: none"
      @change="handleFileChange"
    />

    <p v-if="hint" class="image-upload__hint">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { Plus, Delete } from "@element-plus/icons-vue";
import api from "@/api/client";

interface Props {
  modelValue: string[];
  uploadUrl: string; // 上传目标 API 路径，如 "/enterprise/photos?photo_type=factory"
  label?: string;
  max?: number;
  accept?: string;
  hint?: string;
}

const props = withDefaults(defineProps<Props>(), {
  label: "图片",
  max: 9,
  accept: "image/png,image/jpeg,image/gif,image/webp",
  hint: "",
});

const emit = defineEmits<{
  "update:modelValue": [value: string[]];
}>();

const fileInputRef = ref<HTMLInputElement>();
const uploading = ref(false);

function triggerUpload() {
  fileInputRef.value?.click();
}

async function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const files = input.files;
  if (!files || files.length === 0) return;

  uploading.value = true;
  const results: string[] = [];
  const errors: string[] = [];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];

    // 客户端预校验
    if (!file.type.startsWith("image/")) {
      errors.push(`${file.name}: 请选择图片文件`);
      continue;
    }
    if (file.size > 5 * 1024 * 1024) {
      errors.push(`${file.name}: 图片大小超过 5MB`);
      continue;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post(props.uploadUrl, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const newUrl = data.url || data.logo_url;
      if (newUrl) {
        results.push(newUrl);
      }
    } catch {
      errors.push(`${file.name}: 上传失败`);
    }
  }

  uploading.value = false;
  // 重置 input 以允许重复上传同一文件
  if (input) input.value = "";

  if (results.length > 0) {
    const updated = [...props.modelValue, ...results];
    emit("update:modelValue", updated);
  }

  if (errors.length > 0) {
    ElMessage.error(errors.slice(0, 3).join("；"));
  } else if (results.length > 0) {
    ElMessage.success(`已上传 ${results.length} 张图片`);
  }
}

function handleRemove(idx: number) {
  const updated = props.modelValue.filter((_, i) => i !== idx);
  emit("update:modelValue", updated);
}
</script>

<style scoped lang="scss">
.image-upload {
  &__grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  &__item {
    position: relative;
    width: 120px;
    height: 120px;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #e2e8f0;

    &:hover .image-upload__actions {
      opacity: 1;
    }
  }

  &__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  &__actions {
    position: absolute;
    top: 4px;
    right: 4px;
    opacity: 0;
    transition: opacity 0.15s;
  }

  &__trigger {
    width: 120px;
    height: 120px;
    border: 2px dashed #cbd5e1;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #94a3b8;
    transition: all 0.15s;

    &:hover {
      border-color: #3b82f6;
      color: #3b82f6;
      background: rgba(59, 130, 246, 0.04);
    }
  }

  .trigger-text {
    font-size: 12px;
    margin-top: 4px;
  }

  &__hint {
    margin: 6px 0 0;
    font-size: 12px;
    color: #94a3b8;
  }
}
</style>
