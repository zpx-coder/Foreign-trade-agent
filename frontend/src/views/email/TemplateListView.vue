<template>
  <div class="template-list-page">
    <PageHeader title="邮件模板">
      <template #actions>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新建模板
        </el-button>
      </template>
    </PageHeader>

    <el-card class="table-card">
      <LoadingSkeleton v-if="store.templatesLoading" variant="table" />
      <EmptyState v-else-if="!store.templates.length" description="暂无邮件模板"
        action-text="创建第一个模板" @action="openCreate" />
      <template v-else>
        <el-table :data="store.templates" stripe>
          <el-table-column prop="name" label="模板名称" min-width="180">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEdit(row.id)">{{ row.name }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="subject" label="邮件主题" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">{{ row.subject || "—" }}</template>
          </el-table-column>
          <el-table-column prop="tone" label="语气" width="90" align="center">
            <template #default="{ row }">{{ toneLabel(row.tone) }}</template>
          </el-table-column>
          <el-table-column prop="spam_score" label="垃圾评分" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.spam_score" :type="row.spam_score <= 3 ? 'success' : row.spam_score <= 6 ? 'warning' : 'danger'" size="small">{{ row.spam_score }}/10</el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90" align="center">
            <template #default="{ row }"><StatusBadge :status="row.status" /></template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建" width="160">
            <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString("zh-CN") }}</template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="openEdit(row.id)">编辑</el-button>
              <el-button link type="danger" size="small" @click="confirmDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
            :total="store.templatesTotal" :page-sizes="[10, 20]" layout="total, prev, pager, next"
            @current-change="loadData" @size-change="loadData" />
        </div>
      </template>
    </el-card>

    <!-- 创建/编辑弹窗 -->
    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑模板' : '新建模板'"
      width="960px" :close-on-click-modal="false" @closed="resetDialog" top="3vh">
      <!-- 表单区 -->
      <el-form ref="formRef" :model="form" label-position="top" :disabled="genLoading">
        <el-form-item label="模板名称" required>
          <el-input v-model="form.name" placeholder="如：德国机械客户开发信" maxlength="255" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="关联画像">
              <el-select v-model="form.icp_id" placeholder="选择" clearable style="width:100%">
                <el-option v-for="icp in icpOptions" :key="icp.id" :label="icp.name" :value="icp.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="关联产品">
              <el-select v-model="form.product_id" placeholder="选择" clearable style="width:100%">
                <el-option v-for="p in productOptions" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="语气">
              <el-select v-model="form.tone" style="width:100%">
                <el-option label="正式" value="formal" />
                <el-option label="友好" value="friendly" />
                <el-option label="简洁" value="concise" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="CTA">
              <el-select v-model="form.cta_type" style="width:100%">
                <el-option label="回复" value="reply" />
                <el-option label="会议" value="meeting" />
                <el-option label="网站" value="website" />
                <el-option label="目录" value="catalog" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="关键卖点">
              <el-input v-model="form.key_points" type="textarea" :rows="2" placeholder="ISO 认证、欧盟合规、20年经验..." />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参考邮件样例（可选）">
              <el-input v-model="form.reference_email" type="textarea" :rows="2" placeholder="粘贴效果好的开发信..." />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <!-- AI 生成中 -->
      <div v-if="generating" class="gen-panel">
        <div class="gen-header">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>AI 正在撰写邮件...</span>
        </div>
        <div v-if="streamText" class="stream-content">
          <pre>{{ streamText }}</pre>
        </div>
      </div>

      <!-- 生成结果 -->
      <div v-if="generated && genOutput" class="gen-result">
        <el-divider content-position="left">生成结果</el-divider>

        <!-- 主题选择 -->
        <div v-if="genOutput.subjects?.length" class="subject-select">
          <span class="section-title">选择邮件主题：</span>
          <el-radio-group v-model="selectedSubjectIndex" @change="onSubjectChange">
            <div v-for="(s, i) in genOutput.subjects" :key="i" class="subject-radio">
              <el-radio :label="i">{{ s }}</el-radio>
            </div>
          </el-radio-group>
        </div>

        <!-- 评分标签 -->
        <div class="score-row">
          <el-tag v-if="genOutput.spam_score" :type="genOutput.spam_score <= 3 ? 'success' : genOutput.spam_score <= 6 ? 'warning' : 'danger'" size="small">
            垃圾风险: {{ genOutput.spam_score }}/10
          </el-tag>
          <el-tag v-if="genOutput.read_time_seconds" type="info" size="small">
            预计阅读: {{ genOutput.read_time_seconds }}秒
          </el-tag>
        </div>

        <!-- 邮件预览 + 编辑 -->
        <el-tabs v-model="previewTab" style="margin-top:12px">
          <el-tab-pane label="邮件预览" name="preview">
            <div class="email-preview" v-html="editedBodyHtml || genHtmlBody"></div>
          </el-tab-pane>
          <el-tab-pane label="HTML 源码" name="html">
            <el-input v-model="editedBodyHtml" type="textarea" :rows="14"
              :placeholder="genHtmlBody" />
          </el-tab-pane>
          <el-tab-pane label="纯文本" name="text">
            <el-input v-model="editedBodyText" type="textarea" :rows="14"
              :placeholder="genOutput.body_text || ''" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 错误 -->
      <el-alert v-if="genError" :title="genError" type="error" show-icon :closable="false" style="margin-top:12px" />

      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="success" :loading="genLoading" @click="handleGenerate" :disabled="!form.name">
          <el-icon><MagicStick /></el-icon>{{ generated ? '重新生成' : 'AI 生成并预览' }}
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveAndClose" :disabled="!generated">
          保存并关闭
        </el-button>
      </template>
    </el-dialog>

    <ConfirmDialog v-model:visible="delDialog.visible" title="删除模板"
      :message="`确定删除「${delDialog.name}」吗？`"
      confirm-type="danger" confirm-text="删除" :loading="deleting" @confirm="handleDelete" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Plus, MagicStick, Loading } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import { useEmailStore, type EmailTemplateItem } from "@/stores/email";
import api from "@/api/client";

const store = useEmailStore();
const page = ref(1); const pageSize = ref(20);
function loadData() { store.fetchTemplates({ page: page.value, page_size: pageSize.value }); }
function toneLabel(t: string | null) { const m: Record<string, string> = { formal: "正式", friendly: "友好", concise: "简洁" }; return t ? m[t] || t : "—"; }

const formRef = ref();
const EMPTY = { name: "", icp_id: "", product_id: "", tone: "friendly", cta_type: "reply", key_points: "", reference_email: "" };
const form = reactive({ ...EMPTY });
const dialog = reactive({ visible: false, isEdit: false });
const currentId = ref<string | null>(null);
const saving = ref(false);
const icpOptions = ref<{ id: string; name: string }[]>([]);
const productOptions = ref<{ id: string; name: string }[]>([]);

// 生成状态
const generating = ref(false);
const generated = ref(false);
const genLoading = ref(false);
const genError = ref<string | null>(null);
const genOutput = ref<Record<string, any> | null>(null);
const streamText = ref("");
const selectedSubjectIndex = ref(0);
const editedBodyHtml = ref("");
const editedBodyText = ref("");
const previewTab = ref("preview");

// 计算当前选中的 HTML 预览
const genHtmlBody = computed(() => {
  let raw = editedBodyHtml.value || genOutput.value?.body_html || "";
  // 图片占位符：替换为可视化占位框
  raw = raw.replace(/\{\{\s*企业Logo\s*\}\}/g,
    '<div style="text-align:center;padding:12px;margin:8px 0;background:#f0f9ff;border:2px dashed #bae6fd;border-radius:8px">'
    + '<span style="color:#0369a1;font-size:12px">📷 企业 Logo（发送时自动替换）</span></div>');
  raw = raw.replace(/\{\{\s*产品图片\s*\}\}/g,
    '<div style="text-align:center;padding:16px;margin:8px 0;background:#fefce8;border:2px dashed #fde68a;border-radius:8px">'
    + '<span style="color:#a16207;font-size:12px">📦 产品图片（发送时自动替换）</span></div>');
  // 其他变量高亮
  raw = raw.replace(/\{\{\s*(.+?)\s*\}\}/g,
    '<span style="background:#dbeafe;color:#1d4ed8;padding:0 3px;border-radius:2px">{{ $1 }}</span>');
  return raw;
});

async function loadOptions() {
  try { const { data } = await api.get("/icps", { params: { page_size: 50 } }); icpOptions.value = data.items || []; } catch { /* */ }
  try { const { data } = await api.get("/products", { params: { page_size: 50 } }); productOptions.value = data.items || []; } catch { /* */ }
}

async function openCreate() {
  dialog.isEdit = false; currentId.value = null;
  Object.assign(form, { ...EMPTY });
  resetGenState();
  dialog.visible = true; await loadOptions();
}

async function openEdit(id: string) {
  dialog.isEdit = true; currentId.value = id;
  resetGenState();
  try {
    const d = await store.fetchTemplate(id);
    form.name = d.name; form.icp_id = d.icp_id || ""; form.product_id = d.product_id || "";
    form.tone = d.tone || "friendly"; form.cta_type = d.cta_type || "reply";
    form.key_points = d.key_points || ""; form.reference_email = "";
    if (d.status === "ready" && d.output_data) {
      genOutput.value = d.output_data as any;
      generated.value = true;
      if ((d.output_data as any).body_html) editedBodyHtml.value = (d.output_data as any).body_html;
      if ((d.output_data as any).body_text) editedBodyText.value = (d.output_data as any).body_text;
    }
  } catch { /* */ }
  dialog.visible = true; await loadOptions();
}

function resetGenState() {
  generating.value = false; generated.value = false; genError.value = null;
  genOutput.value = null; streamText.value = ""; selectedSubjectIndex.value = 0;
  editedBodyHtml.value = ""; editedBodyText.value = ""; previewTab.value = "preview";
}

function resetDialog() { Object.assign(form, { ...EMPTY }); resetGenState(); }

function buildPayload(): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(form)) {
    if (k === "reference_email") continue;
    if (v !== "" && v !== null) payload[k] = v;
  }
  if (genOutput.value?.subjects?.length && selectedSubjectIndex.value >= 0) {
    payload.subject = genOutput.value.subjects[selectedSubjectIndex.value];
  }
  if (editedBodyHtml.value) payload.body_html = editedBodyHtml.value;
  if (editedBodyText.value) payload.body_text = editedBodyText.value;
  return payload;
}

async function handleSaveAndClose() {
  if (!currentId.value) return;
  saving.value = true;
  try {
    await store.updateTemplate(currentId.value, buildPayload());
    ElMessage.success("模板已保存");
    dialog.visible = false;
    loadData();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "保存失败"); }
  finally { saving.value = false; }
}

async function handleGenerate() {
  if (!form.name) { ElMessage.warning("请输入模板名称"); return; }
  genLoading.value = true; genError.value = null;

  try {
    // 如果还没创建草稿，先创建
    if (!currentId.value) {
      const payload: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(form)) {
        if (k === "reference_email") continue;
        if (v !== "" && v !== null) payload[k] = v;
      }
      const created = await store.createTemplate(payload);
      currentId.value = created.id;
      dialog.isEdit = true;
    }

    // 开始 SSE 生成
    generating.value = true; generated.value = false;
    streamText.value = "";
    const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";
    const token = localStorage.getItem("access_token");
    const resp = await fetch(`${baseUrl}/email-templates/${currentId.value}/generate`, {
      method: "POST", headers: { Authorization: `Bearer ${token}` },
    });
    if (!resp.ok) { const e = await resp.json().catch(() => ({})); throw new Error((e as any).detail || "生成失败"); }
    const reader = resp.body?.getReader(); if (!reader) return;
    const decoder = new TextDecoder(); let buf = "";
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split("\n"); buf = lines.pop() || "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const evt = JSON.parse(line.slice(6));
            if (evt.type === "text") {
              streamText.value += evt.content || "";
            } else if (evt.type === "complete") {
              genOutput.value = evt;
              generated.value = true; generating.value = false;
              if (genOutput.value?.body_html) editedBodyHtml.value = genOutput.value.body_html;
              if (genOutput.value?.body_text) editedBodyText.value = genOutput.value.body_text;
            } else if (evt.type === "error") {
              genError.value = evt.message; generating.value = false;
            }
          } catch { /* */ }
        }
      }
    }
    generating.value = false;
  } catch (err: any) { genError.value = err.message || "生成失败"; generating.value = false; }
  finally { genLoading.value = false; loadData(); }
}

const deleting = ref(false);
const delDialog = reactive({ visible: false, id: "", name: "" });
function confirmDelete(row: EmailTemplateItem) { delDialog.id = row.id; delDialog.name = row.name; delDialog.visible = true; }
async function handleDelete() {
  deleting.value = true;
  try { await store.removeTemplate(delDialog.id); ElMessage.success("已删除"); delDialog.visible = false; loadData(); }
  catch { ElMessage.error("删除失败"); } finally { deleting.value = false; }
}

onMounted(loadData);
</script>

<style scoped lang="scss">
.template-list-page {
  .table-card { border-radius: 14px; border: 1px solid #e2e8f0; }
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
}

.gen-panel {
  margin-top: 12px; padding: 16px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;
  .gen-header { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #3b82f6; margin-bottom: 12px; }
  .stream-content {
    max-height: 200px; overflow-y: auto; background: #fff; border-radius: 6px; padding: 12px;
    font-size: 12px; font-family: monospace; white-space: pre-wrap; color: #475569; border: 1px solid #e2e8f0;
  }
}

.gen-result {
  margin-top: 8px;
  .section-title { font-size: 13px; font-weight: 600; color: #475569; display: block; margin-bottom: 8px; }
  .subject-select { margin-bottom: 12px; }
  .subject-radio { padding: 4px 0; :deep(.el-radio__label) { font-size: 13px; } }
  .score-row { display: flex; gap: 8px; margin-bottom: 4px; }

  .email-preview {
    min-height: 200px; max-height: 400px; overflow-y: auto; padding: 16px;
    border: 1px solid #e2e8f0; border-radius: 8px; background: #fff;
    font-size: 14px; line-height: 1.7; color: #334155;
    :deep(p) { margin: 0 0 8px 0; }
    :deep(b) { color: #1e293b; }
  }
}
</style>
