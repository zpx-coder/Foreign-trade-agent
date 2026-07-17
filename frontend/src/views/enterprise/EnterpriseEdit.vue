<template>
  <div class="enterprise-edit-page">
    <PageHeader
      title="企业资料"
      :breadcrumb="[{ title: '企业资料' }]"
    >
      <template #actions>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存
        </el-button>
      </template>
    </PageHeader>

    <LoadingSkeleton v-if="loading" variant="form" />

    <template v-else>
      <el-card class="section-card">
        <template #header>
          <span class="section-title">基本信息</span>
        </template>
        <el-form
          ref="formRef"
          :model="form"
          :rules="formRules"
          label-width="130px"
          class="enterprise-form"
        >
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="企业名称" prop="company_name">
                <el-input v-model="form.company_name" maxlength="255" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属行业" prop="industry">
                <el-input v-model="form.industry" placeholder="如：家居用品、电子产品" maxlength="100" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="企业官网" prop="website">
                <el-input v-model="form.website" placeholder="https://www.example.com" maxlength="255" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所在城市" prop="city">
                <el-select
                  v-model="form.city"
                  filterable
                  clearable
                  placeholder="请选择城市"
                  style="width: 100%"
                >
                  <el-option
                    v-for="c in cities"
                    :key="c"
                    :label="c"
                    :value="c"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="详细地址" prop="address">
            <el-input v-model="form.address" placeholder="如：广东省深圳市南山区科技园路1号" maxlength="500" />
          </el-form-item>

          <el-form-item label="企业简介" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              maxlength="2000"
              show-word-limit
              placeholder="简要描述企业定位与主营业务"
            />
          </el-form-item>

          <!-- Logo -->
          <el-form-item label="企业 Logo">
            <div class="logo-section">
              <img v-if="form.logo_url" :src="form.logo_url" class="logo-preview" />
              <el-upload
                :show-file-list="false"
                :before-upload="handleLogoUpload"
                accept="image/png,image/jpeg,image/gif,image/webp"
              >
                <el-button size="small" :loading="logoUploading">
                  {{ form.logo_url ? '更换 Logo' : '上传 Logo' }}
                </el-button>
              </el-upload>
            </div>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 外贸信息 -->
      <el-card class="section-card">
        <template #header>
          <span class="section-title">外贸信息</span>
          <span class="section-subtitle">采购商关注的企业实力信息</span>
        </template>
        <el-form :model="form" label-width="130px" class="enterprise-form">
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="成立年份">
                <el-input-number v-model="form.year_established" :min="1900" :max="2100" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="员工人数">
                <el-input v-model="form.employee_count" placeholder="如：50-100人" maxlength="50" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="工厂面积">
                <el-input v-model="form.factory_area" placeholder="如：5000平方米" maxlength="100" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="年出口额">
                <el-input v-model="form.annual_export_volume" placeholder="如：500万美元" maxlength="100" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="OEM/ODM">
                <el-input v-model="form.oem_odm" placeholder="如：支持OEM贴牌代工，可定制包装" maxlength="255" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="主要出口市场">
            <el-select
              v-model="form.main_markets"
              multiple
              filterable
              allow-create
              placeholder="选择或输入目标市场"
              style="width: 100%"
            >
              <el-option label="北美" value="北美" />
              <el-option label="欧盟" value="欧盟" />
              <el-option label="东南亚" value="东南亚" />
              <el-option label="中东" value="中东" />
              <el-option label="南美" value="南美" />
              <el-option label="非洲" value="非洲" />
              <el-option label="东亚" value="东亚" />
              <el-option label="南亚" value="南亚" />
              <el-option label="大洋洲" value="大洋洲" />
              <el-option label="东欧" value="东欧" />
              <el-option label="中亚" value="中亚" />
            </el-select>
          </el-form-item>

          <el-form-item label="认证资质">
            <el-select
              v-model="form.certifications"
              multiple
              filterable
              allow-create
              placeholder="选择或输入认证资质"
              style="width: 100%"
            >
              <el-option label="ISO 9001" value="ISO 9001" />
              <el-option label="ISO 14001" value="ISO 14001" />
              <el-option label="ISO 13485" value="ISO 13485" />
              <el-option label="CE" value="CE" />
              <el-option label="FDA" value="FDA" />
              <el-option label="BSCI" value="BSCI" />
              <el-option label="SEDEX" value="SEDEX" />
              <el-option label="FSC" value="FSC" />
              <el-option label="RoHS" value="RoHS" />
              <el-option label="REACH" value="REACH" />
              <el-option label="GS" value="GS" />
              <el-option label="UL" value="UL" />
              <el-option label="CCC" value="CCC" />
            </el-select>
          </el-form-item>

          <el-form-item label="企业特色/优势">
            <el-input
              v-model="form.company_advantages"
              type="textarea"
              :rows="3"
              maxlength="2000"
              show-word-limit
              placeholder="如：20年行业经验、自有研发团队、快速打样3天出样等"
            />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 联系信息 -->
      <el-card class="section-card">
        <template #header>
          <span class="section-title">联系信息</span>
        </template>
        <el-form :model="form" label-width="130px" class="enterprise-form">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="联系人">
                <el-input v-model="form.contact_position" maxlength="100" placeholder="如：外贸经理" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系邮箱">
                <el-input v-model="form.contact_email" maxlength="255" type="email" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="联系电话">
                <el-input v-model="form.contact_phone" maxlength="50" placeholder="如：+86 755-12345678" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>

      <!-- 企业图片 -->
      <el-card class="section-card">
        <template #header>
          <span class="section-title">工厂实景</span>
          <span class="section-subtitle">展示生产环境、车间、仓库等</span>
        </template>
        <ImageUpload
          v-model="form.factory_photos"
          upload-url="/enterprise/photos?photo_type=factory"
          label="工厂实景"
          :max="9"
          hint="建议上传车间全景、生产线、仓库等照片，尺寸不超过 5MB"
        />
      </el-card>

      <el-card class="section-card">
        <template #header>
          <span class="section-title">资质证件</span>
          <span class="section-subtitle">展示认证证书、营业执照、专利等</span>
        </template>
        <ImageUpload
          v-model="form.certificate_photos"
          upload-url="/enterprise/photos?photo_type=certificate"
          label="资质证件"
          :max="9"
          hint="建议上传 ISO、CE、FDA 等认证证书，尺寸不超过 5MB"
        />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, type FormInstance, type FormRules, type UploadFile } from "element-plus";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import ImageUpload from "@/components/common/ImageUpload.vue";
import api from "@/api/client";
import cities from "@/data/cities.json";

// ── 企业表单 ──
const formRef = ref<FormInstance>();
const loading = ref(true);
const saving = ref(false);
const logoUploading = ref(false);

interface EnterpriseForm {
  company_name: string;
  logo_url: string;
  industry: string;
  website: string;
  city: string;
  address: string;
  description: string;
  contact_email: string;
  contact_phone: string;
  contact_position: string;
  year_established: number | undefined;
  employee_count: string;
  factory_area: string;
  annual_export_volume: string;
  main_markets: string[];
  certifications: string[];
  oem_odm: string;
  company_advantages: string;
  factory_photos: string[];
  certificate_photos: string[];
}

const defaultForm = (): EnterpriseForm => ({
  company_name: "",
  logo_url: "",
  industry: "",
  website: "",
  city: "",
  address: "",
  description: "",
  contact_email: "",
  contact_phone: "",
  contact_position: "",
  year_established: undefined,
  employee_count: "",
  factory_area: "",
  annual_export_volume: "",
  main_markets: [],
  certifications: [],
  oem_odm: "",
  company_advantages: "",
  factory_photos: [],
  certificate_photos: [],
});

const form = reactive<EnterpriseForm>(defaultForm());

const formRules: FormRules = {
  company_name: [{ required: true, message: "请输入企业名称", trigger: "blur" }],
  website: [
    {
      pattern: /^(https?:\/\/)?[\w.-]+(\.[a-z]{2,})+(:\d+)?(\/\S*)?$/i,
      message: "请输入有效的网址",
      trigger: "blur",
    },
  ],
};

async function loadProfile() {
  loading.value = true;
  try {
    const { data } = await api.get("/enterprise");
    Object.keys(defaultForm()).forEach((key) => {
      const val = data[key as keyof typeof data];
      if (val !== undefined && val !== null) {
        (form as any)[key] = val;
      }
    });
  } catch (err: any) {
    if (err?.response?.status !== 404) {
      // 404 表示尚未创建，使用默认空值即可
    }
  } finally {
    loading.value = false;
  }
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  saving.value = true;
  try {
    await api.put("/enterprise", { ...form, country: "中国" });
    ElMessage.success("企业资料已保存");
  } finally {
    saving.value = false;
  }
}

async function handleLogoUpload(file: UploadFile) {
  logoUploading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", file as any);
    const { data } = await api.post("/enterprise/logo", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    form.logo_url = data.logo_url || data.url;
    ElMessage.success("Logo 上传成功");
  } finally {
    logoUploading.value = false;
  }
  return false; // 阻止 el-upload 默认上传行为
}

onMounted(loadProfile);
</script>

<style scoped lang="scss">
.enterprise-edit-page {
  padding: 0;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 12px;

  :deep(.el-card__header) {
    padding: 16px 24px;
    border-bottom: 1px solid #f1f5f9;
  }
  :deep(.el-card__body) {
    padding: 24px;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.section-subtitle {
  font-size: 12px;
  color: #94a3b8;
  margin-left: 10px;
}

.enterprise-form {
  max-width: 100%;

  :deep(.el-select) {
    width: 100%;
  }
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-preview {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}
</style>
