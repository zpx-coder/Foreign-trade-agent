<template>
  <div class="customer-detail-page">
    <PageHeader
      :title="customer?.name || '客户详情'"
      :breadcrumb="[
        { title: '客户管理', path: '/app/customers' },
        { title: customer?.name || '客户详情' },
      ]"
    >
      <template #actions>
        <el-button @click="$router.push('/app/customers')">返回列表</el-button>
        <el-button type="success" :loading="enriching" :disabled="!customer?.website" @click="handleEnrich">
          <el-icon><MagicStick /></el-icon>补全信息
        </el-button>
        <el-button type="danger" @click="handleDelete">删除客户</el-button>
      </template>
    </PageHeader>

    <LoadingSkeleton v-if="loading" variant="detail" />
    <el-alert v-else-if="loadError" :title="loadError" type="error" show-icon />

    <template v-else-if="customer">
      <!-- 元信息卡片 -->
      <el-card class="meta-card">
        <div class="meta-row">
          <div class="meta-left">
            <StatusBadge :status="customer.status" size="default" />
            <StatusBadge :status="customer.source" size="default" />
            <el-tag v-if="customer.icp_id" type="info" size="default">关联画像</el-tag>
          </div>
          <div class="meta-right">
            <a v-if="customer.website" :href="customer.website" target="_blank" class="website-link">
              <el-icon><Link /></el-icon> {{ customer.website }}
            </a>
            <span class="date">创建于 {{ new Date(customer.created_at).toLocaleString("zh-CN") }}</span>
          </div>
        </div>
      </el-card>

      <!-- 补全进度 -->
      <el-card v-if="enriching || enrichResult" class="enrich-card">
        <StreamingOutput
          :is-streaming="enriching"
          :error="enrichError"
          :done="enrichDone"
        >
          <template #done>
            <div class="enrich-result">
              <p v-if="enrichStats.contacts_added > 0">
                新增 <strong>{{ enrichStats.contacts_added }}</strong> 个联系人
              </p>
              <p v-if="enrichStats.filled_fields?.length">
                补充字段：{{ enrichStats.filled_fields.join("、") }}
              </p>
              <p v-if="enrichStats.contacts_added === 0 && !enrichStats.filled_fields?.length">
                未发现新的可补全信息
              </p>
              <el-button type="primary" size="small" @click="enrichResult = false; loadData()">
                刷新页面
              </el-button>
            </div>
          </template>
        </StreamingOutput>
      </el-card>

      <!-- 两栏布局 -->
      <div class="detail-grid">
        <!-- 左：公司信息 -->
        <el-card class="section-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">公司信息</span>
              <el-button size="small" @click="showEditDialog = true">编辑</el-button>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="行业">{{ customer.industry || "—" }}</el-descriptions-item>
            <el-descriptions-item label="国家">{{ customer.country || "—" }}</el-descriptions-item>
            <el-descriptions-item label="城市">{{ customer.city || "—" }}</el-descriptions-item>
            <el-descriptions-item label="规模">{{ customer.company_size || "—" }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <StatusBadge :status="customer.status" />
            </el-descriptions-item>
            <el-descriptions-item label="来源">
              <StatusBadge :status="customer.source" />
            </el-descriptions-item>
            <el-descriptions-item label="来源 URL" v-if="customer.source_url">
              <a :href="customer.source_url" target="_blank">{{ customer.source_url }}</a>
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="customer.ai_summary" class="ai-summary-block">
            <h4 class="block-title">AI 摘要</h4>
            <p>{{ customer.ai_summary }}</p>
          </div>

          <div v-if="customer.description" class="desc-block">
            <h4 class="block-title">业务描述</h4>
            <p>{{ customer.description }}</p>
          </div>

          <div v-if="customer.notes" class="notes-block">
            <h4 class="block-title">备注</h4>
            <p>{{ customer.notes }}</p>
          </div>
        </el-card>

        <!-- 右：联系人 -->
        <el-card class="section-card">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">联系人 ({{ contacts.length }})</span>
              <div class="card-header-actions">
                <el-button size="small" type="success" :loading="aiSearching" @click="handleAISearchContacts">
                  <el-icon><MagicStick /></el-icon>AI 搜联系人
                </el-button>
                <el-button size="small" type="primary" @click="openContactDialog()">
                  <el-icon><Plus /></el-icon>添加
                </el-button>
              </div>
            </div>
          </template>
          <!-- AI 搜索进度 -->
          <div v-if="aiSearching || aiSearchResult" class="ai-search-progress">
            <StreamingOutput
              :is-streaming="aiSearching"
              :current-section="aiCurrentSection"
              :error="aiSearchError"
              :done="aiSearchDone"
              :section-list="aiSearchSectionList"
              :thinking-texts="aiSearchThinkingTexts"
              done-text="AI 联系人搜索完成"
            >
              <template #done>
                <div class="ai-search-summary">
                  <p v-if="aiStats.total > 0">
                    共发现 <strong>{{ aiStats.total }}</strong> 个联系人线索：
                    <span v-if="aiStats.linkedin_found > 0">LinkedIn {{ aiStats.linkedin_found }}</span>
                    <span v-if="aiStats.contact_search_found > 0">定向搜索 {{ aiStats.contact_search_found }}</span>
                    <span v-if="aiStats.scraped_found > 0">网站抓取 {{ aiStats.scraped_found }}</span>
                  </p>
                  <p v-else>未发现新的联系人信息</p>
                  <el-button type="primary" size="small" @click="aiSearchResult = false; loadData()">
                    刷新联系人
                  </el-button>
                </div>
              </template>
            </StreamingOutput>
          </div>

          <EmptyState v-if="!contacts.length && !aiSearchResult" description="暂无联系人" action-text="添加联系人" @action="openContactDialog()" />
          <div v-else-if="contacts.length" class="contact-list">
            <div v-for="c in contacts" :key="c.id" class="contact-card">
              <div class="contact-header">
                <span class="contact-name">{{ c.name }}</span>
                <el-tag v-if="c.is_primary" type="warning" size="small" effect="light">主要联系人</el-tag>
                <el-tag v-if="c.contact_type === 'ai_suggested'" type="success" size="small" effect="light">AI 发现</el-tag>
                <el-tag v-else-if="c.contact_type === 'inferred'" type="info" size="small" effect="light">推测</el-tag>
                <el-tag v-if="c.confidence === 'low'" type="warning" size="small" effect="plain">待验证</el-tag>
              </div>
              <div v-if="c.title" class="contact-line">{{ c.title }}</div>
              <div v-if="c.email" class="contact-line">
                <el-icon><Message /></el-icon>
                <a :href="'mailto:' + c.email">{{ c.email }}</a>
              </div>
              <div v-if="c.phone" class="contact-line">
                <el-icon><Phone /></el-icon> {{ c.phone }}
              </div>
              <div v-if="c.linkedin_url" class="contact-line">
                <el-icon><Link /></el-icon>
                <a :href="c.linkedin_url" target="_blank">LinkedIn</a>
              </div>
              <div v-if="c.notes" class="contact-notes">{{ c.notes }}</div>
              <div class="contact-actions">
                <el-button link type="primary" size="small" @click="openContactDialog(c)">编辑</el-button>
                <el-button link type="danger" size="small" @click="handleDeleteContact(c.id)">删除</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 活动记录占位 -->
      <el-card class="section-card activity-card">
        <template #header><span class="card-title">活动记录</span></template>
        <EmptyState description="活动记录将在后续 Phase 上线" />
      </el-card>

      <!-- 原始数据（可折叠） -->
      <el-card v-if="customer.source_data" class="section-card">
        <template #header>
          <span class="card-title" style="cursor: pointer" @click="showSourceData = !showSourceData">
            原始提取数据 {{ showSourceData ? '▾' : '▸' }}
          </span>
        </template>
        <pre v-if="showSourceData" class="source-json">{{ JSON.stringify(customer.source_data, null, 2) }}</pre>
      </el-card>
    </template>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑客户" width="600px" :close-on-click-modal="false">
      <el-form ref="editFormRef" :model="editForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="公司名称" prop="name">
              <el-input v-model="editForm.name" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="行业" prop="industry">
              <el-input v-model="editForm.industry" maxlength="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="官网" prop="website">
              <el-input v-model="editForm.website" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="国家"><el-input v-model="editForm.country" maxlength="100" /></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="城市"><el-input v-model="editForm.city" maxlength="100" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="规模">
              <el-select v-model="editForm.company_size" clearable>
                <el-option label="1-50" value="1-50" />
                <el-option label="50-200" value="50-200" />
                <el-option label="200-1000" value="200-1000" />
                <el-option label="1000+" value="1000+" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="editForm.status">
                <el-option label="新客户" value="new" />
                <el-option label="已联系" value="contacted" />
                <el-option label="已确认意向" value="qualified" />
                <el-option label="洽谈中" value="negotiating" />
                <el-option label="已成交" value="closed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.notes" type="textarea" :rows="2" maxlength="2000" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 联系人弹窗 -->
    <el-dialog v-model="contactDialog.visible"
      :title="contactDialog.isEdit ? '编辑联系人' : '添加联系人'"
      width="480px" :close-on-click-modal="false">
      <el-form ref="contactFormRef" :model="contactForm" :rules="contactRules" label-position="top">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="contactForm.name" placeholder="联系人姓名" maxlength="255" />
        </el-form-item>
        <el-form-item label="职位" prop="title">
          <el-input v-model="contactForm.title" placeholder="如：采购经理" maxlength="255" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="contactForm.email" placeholder="email@example.com" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="contactForm.phone" placeholder="电话号码" maxlength="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="LinkedIn URL" prop="linkedin_url">
          <el-input v-model="contactForm.linkedin_url" placeholder="https://linkedin.com/in/..." maxlength="512" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="contactForm.notes" type="textarea" :rows="2" maxlength="2000" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="contactForm.is_primary">设为主要联系人</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="contactDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="contactDialog.saving" @click="handleSaveContact">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { Plus, Link, Message, Phone, MagicStick } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import StreamingOutput from "@/components/ai/StreamingOutput.vue";
import { useCustomerStore, type ContactItem } from "@/stores/customer";

const route = useRoute();
const router = useRouter();
const store = useCustomerStore();

const loading = ref(true);
const loadError = ref("");
const saving = ref(false);
const showSourceData = ref(false);

// ── 信息补全 ──
const enriching = ref(false);
const enrichDone = ref(false);
const enrichError = ref<string | null>(null);
const enrichResult = ref(false);
const enrichStats = ref<{ contacts_added: number; filled_fields: string[] }>({
  contacts_added: 0,
  filled_fields: [],
});

// ── AI 搜联系人 ──
const aiSearching = ref(false);
const aiSearchDone = ref(false);
const aiSearchError = ref<string | null>(null);
const aiSearchResult = ref(false);
const aiCurrentSection = ref<string | null>(null);
const aiStats = ref({
  linkedin_found: 0,
  contact_search_found: 0,
  scraped_found: 0,
  total: 0,
});
const aiSearchSectionList = [
  { key: "linkedin_people", label: "LinkedIn 人物搜索" },
  { key: "contact_search", label: "定向联系人搜索" },
  { key: "scraping", label: "网站抓取" },
];
const aiSearchThinkingTexts = [
  "正在 LinkedIn 搜索相关人物...",
  "正在定向搜索联系人...",
  "正在抓取网站信息...",
];

async function handleEnrich() {
  if (!customer.value?.id) return;
  enriching.value = true;
  enrichDone.value = false;
  enrichError.value = null;
  enrichResult.value = true;
  enrichStats.value = { contacts_added: 0, filled_fields: [] };

  const token = localStorage.getItem("access_token");
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";

  try {
    const resp = await fetch(`${baseUrl}/customers/${customer.value.id}/enrich`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: "请求失败" }));
      throw new Error(err.detail || "补全请求失败");
    }

    const reader = resp.body?.getReader();
    if (!reader) throw new Error("无法读取响应流");
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === "complete") {
              enrichStats.value = {
                contacts_added: event.contacts_added || 0,
                filled_fields: event.filled_fields || [],
              };
              enrichDone.value = true;
            } else if (event.type === "error") {
              enrichError.value = event.message;
              enrichDone.value = true;
            }
          } catch { /* parse skip */ }
        }
      }
    }
  } catch (err: any) {
    enrichError.value = err.message || "补全失败";
    enrichDone.value = true;
  } finally {
    enriching.value = false;
  }
}

async function handleAISearchContacts() {
  if (!customer.value?.id) return;
  aiSearching.value = true;
  aiSearchDone.value = false;
  aiSearchError.value = null;
  aiSearchResult.value = true;
  aiCurrentSection.value = null;
  aiStats.value = { linkedin_found: 0, contact_search_found: 0, scraped_found: 0, total: 0 };

  const token = localStorage.getItem("access_token");
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";

  try {
    const resp = await fetch(`${baseUrl}/customers/${customer.value.id}/ai-search-contacts`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: "请求失败" }));
      throw new Error(err.detail || "AI 搜索请求失败");
    }

    const reader = resp.body?.getReader();
    if (!reader) throw new Error("无法读取响应流");
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === "section") {
              aiCurrentSection.value = event.section;
            } else if (event.type === "complete") {
              aiStats.value = {
                linkedin_found: event.linkedin_found || 0,
                contact_search_found: event.contact_search_found || 0,
                scraped_found: event.scraped_found || 0,
                total: event.total || 0,
              };
              aiSearchDone.value = true;
            } else if (event.type === "error") {
              aiSearchError.value = event.message;
              aiSearchDone.value = true;
            }
          } catch { /* parse skip */ }
        }
      }
    }
  } catch (err: any) {
    aiSearchError.value = err.message || "AI 搜索失败";
    aiSearchDone.value = true;
  } finally {
    aiSearching.value = false;
  }
}

const customer = computed(() => store.current);
const contacts = computed(() => store.current?.contacts || []);

async function loadData() {
  loading.value = true; loadError.value = "";
  try {
    await store.fetchDetail(route.params.id as string);
  } catch (err: any) {
    loadError.value = err?.response?.data?.detail || "加载客户信息失败";
  } finally { loading.value = false; }
}

// ── 编辑客户 ──
const showEditDialog = ref(false);
const editFormRef = ref<FormInstance>();
const editForm = reactive({
  name: "", industry: "", website: "", country: "", city: "",
  company_size: "", description: "", status: "", notes: "",
});

// watch for customer load
import { watch } from "vue";
watch(customer, (c) => {
  if (c) {
    editForm.name = c.name; editForm.industry = c.industry || "";
    editForm.website = c.website || ""; editForm.country = c.country || "";
    editForm.city = c.city || ""; editForm.company_size = c.company_size || "";
    editForm.description = c.description || ""; editForm.status = c.status;
    editForm.notes = c.notes || "";
  }
});

async function handleSaveEdit() {
  saving.value = true;
  try {
    const payload: Record<string, unknown> = { ...editForm };
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = null; });
    await store.update(route.params.id as string, payload);
    ElMessage.success("客户信息已更新");
    showEditDialog.value = false;
    loadData();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "更新失败"); }
  finally { saving.value = false; }
}

// ── 删除客户 ──
async function handleDelete() {
  try {
    await ElMessageBox.confirm(`确定删除客户「${customer.value?.name}」？关联的联系人也将被删除。`, "删除客户", {
      confirmButtonText: "删除", cancelButtonText: "取消", type: "warning",
    });
    await store.remove(route.params.id as string);
    ElMessage.success("已删除");
    router.push("/app/customers");
  } catch { /* cancelled */ }
}

// ── 联系人弹窗 ──
const contactFormRef = ref<FormInstance>();
const EMPTY_CONTACT = {
  name: "", title: "", email: "", phone: "", linkedin_url: "", notes: "", is_primary: false,
};
const contactForm = reactive({ ...EMPTY_CONTACT });
const contactDialog = reactive({
  visible: false, isEdit: false, editId: null as string | null, saving: false,
});
const contactRules: FormRules = {
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
};

function openContactDialog(row?: ContactItem) {
  if (row) {
    contactDialog.isEdit = true; contactDialog.editId = row.id;
    contactForm.name = row.name; contactForm.title = row.title || "";
    contactForm.email = row.email || ""; contactForm.phone = row.phone || "";
    contactForm.linkedin_url = row.linkedin_url || "";
    contactForm.notes = row.notes || ""; contactForm.is_primary = row.is_primary;
  } else {
    contactDialog.isEdit = false; contactDialog.editId = null;
    Object.assign(contactForm, { ...EMPTY_CONTACT });
    contactFormRef.value?.resetFields();
  }
  contactDialog.visible = true;
}

async function handleSaveContact() {
  const valid = await contactFormRef.value?.validate().catch(() => false);
  if (!valid) return;
  contactDialog.saving = true;
  try {
    const payload: Record<string, unknown> = { ...contactForm };
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = null; });

    if (contactDialog.isEdit && contactDialog.editId) {
      await store.updateContact(route.params.id as string, contactDialog.editId, payload);
      ElMessage.success("联系人已更新");
    } else {
      await store.addContact(route.params.id as string, payload);
      ElMessage.success("联系人已添加");
    }
    contactDialog.visible = false;
    loadData();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "保存失败"); }
  finally { contactDialog.saving = false; }
}

async function handleDeleteContact(contactId: string) {
  try {
    await ElMessageBox.confirm("确定删除此联系人？", "删除联系人", {
      confirmButtonText: "删除", cancelButtonText: "取消", type: "warning",
    });
    await store.removeContact(route.params.id as string, contactId);
    ElMessage.success("已删除");
    loadData();
  } catch { /* cancelled */ }
}

onMounted(loadData);
</script>

<style scoped lang="scss">
.customer-detail-page {
  .meta-card {
    margin-bottom: 24px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    :deep(.el-card__body) { padding: 16px 24px; }
  }
  .meta-row {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
  }
  .meta-left { display: flex; align-items: center; gap: 8px; }
  .meta-right { display: flex; align-items: center; gap: 16px; }
  .website-link { display: flex; align-items: center; gap: 4px; color: #3b82f6; font-size: 14px; }
  .date { color: #94a3b8; font-size: 13px; }

  .detail-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start;
    margin-bottom: 24px;
    @media (max-width: 1000px) { grid-template-columns: 1fr; }
  }
  .section-card {
    border-radius: 14px; border: 1px solid #e2e8f0;
    :deep(.el-card__header) { padding: 16px 24px; }
    :deep(.el-card__body) { padding: 20px 24px; }
  }
  .card-header-row { display: flex; align-items: center; justify-content: space-between; }
  .card-header-actions { display: flex; align-items: center; gap: 8px; }
  .card-title { font-size: 16px; font-weight: 700; color: #0f172a; }
  .block-title { margin: 20px 0 8px 0; font-size: 14px; font-weight: 600; color: #475569; }
  .ai-summary-block p, .desc-block p, .notes-block p { margin: 0; font-size: 14px; color: #334155; line-height: 1.7; }
  .activity-card { margin-bottom: 24px; }
  .source-json { margin: 0; font-size: 12px; color: #64748b; white-space: pre-wrap; word-break: break-all; background: #f8fafc; padding: 12px; border-radius: 6px; }
  .enrich-card {
    margin-bottom: 24px; border-radius: 14px; border: 1px solid #d1fae5;
    :deep(.el-card__body) { padding: 20px 24px; }
  }
  .enrich-result { text-align: center; p { margin: 0 0 12px 0; font-size: 14px; color: #334155; } }

  .ai-search-progress {
    padding: 16px 0;
    margin-bottom: 12px;
    border-bottom: 1px solid #e2e8f0;
  }
  .ai-search-summary { text-align: center;
    p { margin: 0 0 12px 0; font-size: 14px; color: #334155;
      span { margin-left: 8px; color: #64748b; font-size: 13px; }
    }
  }

  .contact-list { display: flex; flex-direction: column; gap: 12px; }
  .contact-card {
    padding: 14px; border: 1px solid #e2e8f0; border-radius: 10px;
    transition: border-color 0.15s;
    &:hover { border-color: #93c5fd; }
  }
  .contact-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  .contact-name { font-weight: 600; color: #1e293b; }
  .contact-line { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #64748b; margin-top: 4px;
    a { color: #3b82f6; }
  }
  .contact-notes { margin-top: 6px; font-size: 12px; color: #94a3b8; }
  .contact-actions { margin-top: 8px; display: flex; gap: 8px; }
}
</style>
