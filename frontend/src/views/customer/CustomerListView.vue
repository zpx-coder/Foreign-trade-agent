<template>
  <div class="customer-list-page">
    <PageHeader title="客户管理">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog()">
          <el-icon><Plus /></el-icon>添加客户
        </el-button>
        <el-button @click="openImportDialog">
          <el-icon><Upload /></el-icon>导入 Excel
        </el-button>
        <el-button type="success" @click="openSearchDialog">
          <el-icon><Search /></el-icon>搜索客户
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>导出 Excel
        </el-button>
      </template>
    </PageHeader>

    <!-- 数据概览 -->
    <div class="stats-bar">
      <div class="stat-item">
        <el-icon :size="22"><UserFilled /></el-icon>
        <span class="stat-val">{{ store.total }}</span>
        <span class="stat-lbl">全部客户</span>
      </div>
      <div class="stat-item stat-new">
        <span class="stat-dot"></span>
        <span class="stat-val">{{ statusCounts.new || 0 }}</span>
        <span class="stat-lbl">新客户</span>
      </div>
      <div class="stat-item stat-contacted">
        <span class="stat-dot"></span>
        <span class="stat-val">{{ statusCounts.contacted || 0 }}</span>
        <span class="stat-lbl">已联系</span>
      </div>
      <div class="stat-item stat-qualified">
        <span class="stat-dot"></span>
        <span class="stat-val">{{ statusCounts.qualified || 0 }}</span>
        <span class="stat-lbl">已确认意向</span>
      </div>
      <div class="stat-item stat-negotiating">
        <span class="stat-dot"></span>
        <span class="stat-val">{{ statusCounts.negotiating || 0 }}</span>
        <span class="stat-lbl">洽谈中</span>
      </div>
      <div class="stat-item stat-closed">
        <span class="stat-dot"></span>
        <span class="stat-val">{{ statusCounts.closed || 0 }}</span>
        <span class="stat-lbl">已成交</span>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="公司名/行业" clearable
            @clear="handleSearch" @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 140px" @change="handleSearch">
            <el-option label="新客户" value="new" />
            <el-option label="已联系" value="contacted" />
            <el-option label="已确认意向" value="qualified" />
            <el-option label="洽谈中" value="negotiating" />
            <el-option label="已成交" value="closed" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="filters.source" placeholder="全部" clearable style="width: 140px" @change="handleSearch">
            <el-option label="手动添加" value="manual" />
            <el-option label="手动导入" value="manual_import" />
            <el-option label="AI 搜索" value="ai_search" />
            <el-option label="AI 提取" value="ai_extraction" />
            <el-option label="Google 搜索" value="google_search" />
            <el-option label="LinkedIn 搜索" value="linkedin_search" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户画像">
          <el-select v-model="filters.icp_id" placeholder="全部" clearable style="width: 180px" @change="handleSearch">
            <el-option v-for="icp in icpFilterOptions" :key="icp.id" :label="icp.name" :value="icp.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 批量操作 -->
    <div v-if="selectedIds.length" class="batch-bar">
      <span class="batch-info">已选 {{ selectedIds.length }} 项</span>
      <el-select v-model="batchStatus" placeholder="批量修改状态" style="width: 160px" @change="handleBatchStatus">
        <el-option label="新客户" value="new" />
        <el-option label="已联系" value="contacted" />
        <el-option label="已确认意向" value="qualified" />
        <el-option label="洽谈中" value="negotiating" />
        <el-option label="已成交" value="closed" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
      <el-button @click="selectedIds = []">取消选择</el-button>
    </div>

    <!-- 表格 -->
    <el-card class="table-card">
      <LoadingSkeleton v-if="store.loading" variant="table" />
      <EmptyState v-else-if="!store.list.length" description="暂无客户数据"
        action-text="添加第一个客户" @action="openCreateDialog()" />
      <template v-else>
        <el-table :data="store.list" stripe @selection-change="handleSelection">
          <el-table-column type="selection" width="44" />
          <el-table-column prop="name" label="公司名称" min-width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="goDetail(row.id)">{{ row.name }}</el-button>
            </template>
          </el-table-column>
          <el-table-column prop="industry" label="行业" width="130">
            <template #default="{ row }">{{ row.industry || "—" }}</template>
          </el-table-column>
          <el-table-column prop="country" label="国家" width="100">
            <template #default="{ row }">{{ row.country || "—" }}</template>
          </el-table-column>
          <el-table-column prop="icp_name" label="客户画像" width="150" show-overflow-tooltip>
            <template #default="{ row }">{{ row.icp_name || "—" }}</template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="110" align="center">
            <template #default="{ row }"><StatusBadge :status="row.source" /></template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="140" align="center">
            <template #default="{ row }">
              <el-select
                :model-value="row.status"
                size="small"
                :class="`status-select status-${row.status}`"
                :disabled="updatingIds.has(row.id)"
                :loading="updatingIds.has(row.id)"
                @change="(val: string) => handleStatusChange(row, val)"
                @click.stop
              >
                <el-option label="新客户" value="new" />
                <el-option label="已联系" value="contacted" />
                <el-option label="已确认意向" value="qualified" />
                <el-option label="洽谈中" value="negotiating" />
                <el-option label="已成交" value="closed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="contacts_count" label="联系人" width="80" align="center" />
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString("zh-CN") }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="goDetail(row.id)">查看</el-button>
              <el-button link size="small" @click="openCreateDialog(row)">编辑</el-button>
              <el-button link type="danger" size="small" @click="confirmDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="store.total" :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="loadData" @size-change="loadData" />
        </div>
      </template>
    </el-card>

    <!-- 创建/编辑弹窗 -->
    <el-dialog v-model="formDialog.visible"
      :title="formDialog.isEdit ? '编辑客户' : '添加客户'"
      width="640px" :close-on-click-modal="false" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="公司名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入公司名称" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="行业" prop="industry">
              <el-input v-model="form.industry" placeholder="如：机械制造" maxlength="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="官网" prop="website">
              <el-input v-model="form.website" placeholder="https://..." maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="国家" prop="country">
              <el-input v-model="form.country" placeholder="国家" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="城市" prop="city">
              <el-input v-model="form.city" placeholder="城市" maxlength="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="规模" prop="company_size">
              <el-select v-model="form.company_size" placeholder="选择" clearable>
                <el-option label="1-50" value="1-50" />
                <el-option label="50-200" value="50-200" />
                <el-option label="200-1000" value="200-1000" />
                <el-option label="1000+" value="1000+" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="9">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="新客户" value="new" />
                <el-option label="已联系" value="contacted" />
                <el-option label="已确认意向" value="qualified" />
                <el-option label="洽谈中" value="negotiating" />
                <el-option label="已成交" value="closed" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="9">
            <el-form-item label="来源" prop="source">
              <el-select v-model="form.source" style="width: 100%">
                <el-option label="手动添加" value="manual" />
                <el-option label="手动导入" value="manual_import" />
                <el-option label="AI 提取" value="ai_extraction" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3"
            placeholder="公司业务描述" maxlength="2000" show-word-limit />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" :rows="2"
            placeholder="内部备注" maxlength="2000" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="formDialog.saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 搜索弹窗 -->
    <el-dialog v-model="searchDialog.visible" title="搜索客户" width="680px" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="选择客户画像">
          <el-select v-model="searchDialog.icpId" placeholder="选择画像（基于画像关键词搜索）"
            style="width: 100%" :disabled="searching">
            <el-option v-for="icp in icpOptions" :key="icp.id" :label="icp.name" :value="icp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索渠道">
          <el-checkbox-group v-model="searchDialog.channels" :disabled="searching">
            <el-checkbox label="ai">AI 智能搜索</el-checkbox>
            <el-checkbox label="duckduckgo">DuckDuckGo</el-checkbox>
            <el-checkbox label="google">Google</el-checkbox>
            <el-checkbox label="linkedin">LinkedIn</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="目标区域（可选）">
          <el-input v-model="searchDialog.region" placeholder="如：Germany, USA" :disabled="searching" />
        </el-form-item>
      </el-form>
      <div v-if="searching || searchDone" class="search-progress">
        <StreamingOutput :is-streaming="searching" :error="searchError" :done="searchDone">
          <template #done>
            <div class="search-result-summary">
              <p v-if="savedCount > 0">
                成功保存 <strong>{{ savedCount }}</strong> 个客户
                <span v-if="enrichedCount > 0">，其中 <strong>{{ enrichedCount }}</strong> 个已抓取到联系人信息</span>
              </p>
              <p v-else>未找到可保存的客户数据</p>
              <el-button type="primary" @click="searchDialog.visible = false; loadData()">关闭并刷新列表</el-button>
            </div>
          </template>
        </StreamingOutput>
      </div>
      <template #footer>
        <el-button @click="searchDialog.visible = false">关闭</el-button>
        <el-button type="primary" :loading="searching"
          :disabled="!searchDialog.icpId || !searchDialog.channels.length" @click="startSearch">
          开始搜索
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入弹窗 -->
    <el-dialog v-model="importDialog.visible" title="导入客户" width="520px" :close-on-click-modal="false"
      @closed="resetImport">
      <div class="import-body">
        <!-- 步骤 1：选择文件 -->
        <template v-if="!importDialog.done">
          <div class="import-upload-area">
            <el-upload
              ref="uploadRef"
              drag
              :auto-upload="false"
              :limit="1"
              accept=".xlsx,.xls"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="importDialog.fileList"
            >
              <el-icon class="el-icon--upload"><Upload /></el-icon>
              <div class="el-upload__text">
                将 Excel 文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  仅支持 .xlsx 格式，文件不超过 5MB，最多 1000 行
                </div>
              </template>
            </el-upload>
          </div>

          <!-- 格式说明 -->
          <el-alert type="info" :closable="false" style="margin-top: 16px">
            <template #title>
              <span>Excel 列要求：第一行为表头，必须有「公司名称」列</span>
            </template>
            <div style="font-size: 12px; color: #64748b; margin-top: 4px">
              可选列：行业、网站、国家、城市、规模、描述、备注、来源URL、状态<br />
              导入后来源自动标记为「手动导入」，状态默认为「新客户」
            </div>
          </el-alert>
        </template>

        <!-- 步骤 2：导入结果 -->
        <template v-else>
          <div class="import-result">
            <div class="import-result-icon" :class="importDialog.hasErrors ? 'has-errors' : 'all-success'">
              {{ importDialog.hasErrors ? '⚠️' : '✅' }}
            </div>
            <h3 class="import-result-title">
              {{ importDialog.hasErrors ? '导入完成（部分失败）' : '导入成功！' }}
            </h3>
            <div class="import-stats">
              <div class="import-stat created">
                <span class="stat-num">{{ importDialog.result.created }}</span>
                <span class="stat-label">已创建</span>
              </div>
              <div class="import-stat skipped">
                <span class="stat-num">{{ importDialog.result.skipped }}</span>
                <span class="stat-label">已跳过</span>
              </div>
            </div>
            <!-- 错误详情 -->
            <div v-if="importDialog.result.errors?.length" class="import-errors">
              <p class="import-errors-title">跳过详情：</p>
              <ul>
                <li v-for="(err, i) in importDialog.result.errors" :key="i">
                  第 {{ err.row }} 行：{{ err.message }}
                </li>
              </ul>
            </div>
          </div>
        </template>
      </div>

      <template #footer>
        <template v-if="!importDialog.done">
          <el-button link type="primary" @click="downloadTemplate" :loading="downloadingTemplate">
            下载模板
          </el-button>
          <div style="flex:1" />
          <el-button @click="importDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="importDialog.loading" :disabled="!importDialog.file"
            @click="handleImport">
            开始导入
          </el-button>
        </template>
        <template v-else>
          <el-button @click="importDialog.visible = false">关闭</el-button>
          <el-button type="primary" @click="importDialog.visible = false; loadData()">
            刷新列表
          </el-button>
        </template>
      </template>
    </el-dialog>

    <!-- 删除确认 -->
    <ConfirmDialog v-model:visible="deleteDialog.visible" title="删除客户"
      :message="`确定删除客户「${deleteDialog.name}」吗？关联的联系人也将被删除。`"
      confirm-type="danger" confirm-text="删除" :loading="deleting" @confirm="handleDelete" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { Plus, Search, Download, UserFilled, Upload } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import StreamingOutput from "@/components/ai/StreamingOutput.vue";
import { useCustomerStore, type CustomerListItem } from "@/stores/customer";
import api from "@/api/client";

const router = useRouter();
const store = useCustomerStore();

// ── 筛选 ──
const filters = reactive({ search: "", status: "", source: "", icp_id: "" });
const pagination = reactive({ page: 1, pageSize: 20 });
const icpFilterOptions = ref<{ id: string; name: string }[]>([]);
const statusCounts = ref<Record<string, number>>({});

function buildParams() {
  const params: Record<string, string | number> = {
    page: pagination.page, page_size: pagination.pageSize,
  };
  if (filters.search) params.search = filters.search;
  if (filters.status) params.status = filters.status;
  if (filters.source) params.source = filters.source;
  if (filters.icp_id) params.icp_id = filters.icp_id;
  return params;
}

async function loadData() { await store.fetchList(buildParams()); }
async function loadStatusCounts() {
  try {
    const { data } = await api.get("/dashboard/stats");
    statusCounts.value = data.customer_status_counts || {};
  } catch { /* */ }
}
function handleSearch() { pagination.page = 1; loadData(); }
function handleReset() {
  filters.search = ""; filters.status = ""; filters.source = ""; filters.icp_id = "";
  pagination.page = 1; loadData();
}

// ── 批量 ──
const selectedIds = ref<string[]>([]);
const batchStatus = ref("");
function handleSelection(rows: CustomerListItem[]) { selectedIds.value = rows.map((r) => r.id); }
async function handleBatchStatus() {
  if (!batchStatus.value || !selectedIds.value.length) return;
  try {
    await store.batchUpdateStatus(selectedIds.value, batchStatus.value);
    ElMessage.success(`已更新状态`);
    selectedIds.value = []; batchStatus.value = ""; loadData();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "批量更新失败"); }
}

// ── 行内状态快速切换 ──
const updatingIds = ref<Set<string>>(new Set());

async function handleStatusChange(row: CustomerListItem, newStatus: string) {
  const oldStatus = row.status;
  if (oldStatus === newStatus) return;
  updatingIds.value.add(row.id);
  row.status = newStatus; // 乐观更新
  try {
    await store.update(row.id, { status: newStatus });
    ElMessage.success("状态已更新");
  } catch (err: any) {
    row.status = oldStatus; // 回退
    ElMessage.error(err?.response?.data?.detail || "状态更新失败");
  } finally {
    updatingIds.value.delete(row.id);
  }
}

// ── 导出 ──
async function handleExport() {
  try { await store.exportData(buildParams()); ElMessage.success("导出成功"); }
  catch { ElMessage.error("导出失败"); }
}

// ── 创建/编辑 ──
const formRef = ref<FormInstance>();
const EMPTY_FORM = {
  name: "", industry: "", website: "", country: "", city: "",
  company_size: "", description: "", source: "manual", status: "new", notes: "",
};
const form = reactive({ ...EMPTY_FORM });
const formDialog = reactive({ visible: false, isEdit: false, editId: null as string | null, saving: false });
const formRules: FormRules = { name: [{ required: true, message: "请输入公司名称", trigger: "blur" }] };

async function openCreateDialog(row?: CustomerListItem) {
  if (row) {
    formDialog.isEdit = true; formDialog.editId = row.id;
    try {
      const detail = await store.fetchDetail(row.id);
      form.name = detail.name;
      form.industry = detail.industry || "";
      form.website = detail.website || "";
      form.country = detail.country || "";
      form.city = detail.city || "";
      form.company_size = detail.company_size || "";
      form.description = detail.description || "";
      form.source = detail.source;
      form.status = detail.status;
      form.notes = detail.notes || "";
    } catch {
      // fallback to list item data
      form.name = row.name; form.industry = row.industry || "";
      form.country = row.country || ""; form.source = row.source; form.status = row.status;
    }
  } else {
    formDialog.isEdit = false; formDialog.editId = null; resetForm();
  }
  formDialog.visible = true;
}

function resetForm() { Object.assign(form, { ...EMPTY_FORM }); formRef.value?.resetFields(); }

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  formDialog.saving = true;
  try {
    const payload: Record<string, unknown> = { ...form };
    Object.keys(payload).forEach((k) => { if (payload[k] === "") payload[k] = null; });
    if (formDialog.isEdit && formDialog.editId) {
      await store.update(formDialog.editId, payload); ElMessage.success("客户已更新");
    } else {
      await store.create(payload); ElMessage.success("客户已添加");
    }
    formDialog.visible = false; loadData();
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || "保存失败"); }
  finally { formDialog.saving = false; }
}

// ── 删除 ──
const deleting = ref(false);
const deleteDialog = reactive({ visible: false, id: "", name: "" });
function confirmDelete(row: CustomerListItem) {
  deleteDialog.id = row.id; deleteDialog.name = row.name; deleteDialog.visible = true;
}
async function handleDelete() {
  deleting.value = true;
  try { await store.remove(deleteDialog.id); ElMessage.success("已删除"); deleteDialog.visible = false; loadData(); }
  catch (err: any) { ElMessage.error(err?.response?.data?.detail || "删除失败"); }
  finally { deleting.value = false; }
}

// ── 搜索 ──
const searchDialog = reactive({
  visible: false, icpId: "", channels: ["ai"] as string[], region: "",
});
const icpOptions = ref<{ id: string; name: string }[]>([]);
const searching = ref(false);
const searchDone = ref(false);
const searchError = ref<string | null>(null);
const savedCount = ref(0);
const enrichedCount = ref(0);

async function openSearchDialog() {
  searchDialog.visible = true;
  searchDialog.icpId = ""; searchDialog.channels = ["duckduckgo"]; searchDialog.region = "";
  searchDone.value = false; searchError.value = null; savedCount.value = 0; enrichedCount.value = 0;
  try {
    const { data } = await api.get("/icps", { params: { page: 1, page_size: 50 } });
    icpOptions.value = data.items || [];
  } catch { icpOptions.value = []; }
}

function startSearch() {
  if (!searchDialog.icpId || !searchDialog.channels.length) return;
  searching.value = true; searchDone.value = false; searchError.value = null; savedCount.value = 0;
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";
  const token = localStorage.getItem("access_token");
  fetch(`${baseUrl}/customers/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      icp_id: searchDialog.icpId, channels: searchDialog.channels,
      region: searchDialog.region || null,
    }),
  }).then(async (response) => {
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      searchError.value = (errData as any).detail || "搜索请求失败";
      searching.value = false; searchDone.value = true; return;
    }
    const reader = response.body?.getReader();
    if (!reader) { searching.value = false; return; }
    const decoder = new TextDecoder(); let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n"); buffer = lines.pop() || "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === "complete") {
              savedCount.value = event.saved_count || 0;
              enrichedCount.value = event.enriched_count || 0;
              searching.value = false; searchDone.value = true;
            } else if (event.type === "error") {
              searchError.value = event.message;
              searching.value = false; searchDone.value = true;
            }
          } catch { /* skip */ }
        }
      }
    }
    searching.value = false; searchDone.value = true;
  }).catch((err) => {
    searchError.value = err.message || "搜索失败";
    searching.value = false; searchDone.value = true;
  });
}

// ── Excel 导入 ──
const importDialog = reactive({
  visible: false,
  file: null as File | null,
  fileList: [] as any[],
  loading: false,
  done: false,
  hasErrors: false,
  result: { created: 0, skipped: 0, errors: [] as { row: number; message: string }[] },
});
const downloadingTemplate = ref(false);

function openImportDialog() {
  importDialog.visible = true;
  resetImport();
}

function resetImport() {
  importDialog.file = null;
  importDialog.fileList = [];
  importDialog.loading = false;
  importDialog.done = false;
  importDialog.hasErrors = false;
  importDialog.result = { created: 0, skipped: 0, errors: [] };
}

function handleFileChange(file: any) {
  importDialog.file = file.raw;
  importDialog.fileList = [file];
}

function handleFileRemove() {
  importDialog.file = null;
  importDialog.fileList = [];
}

async function downloadTemplate() {
  downloadingTemplate.value = true;
  try {
    await store.downloadTemplate();
  } catch {
    ElMessage.error("模板下载失败");
  } finally {
    downloadingTemplate.value = false;
  }
}

async function handleImport() {
  if (!importDialog.file) {
    ElMessage.warning("请先选择 Excel 文件");
    return;
  }
  importDialog.loading = true;
  try {
    const result = await store.importExcel(importDialog.file);
    importDialog.result = result;
    importDialog.hasErrors = result.errors?.length > 0 || result.skipped > 0;
    importDialog.done = true;
    if (result.created > 0) {
      ElMessage.success(`成功导入 ${result.created} 个客户`);
    } else {
      ElMessage.warning("没有导入任何客户，请检查文件内容");
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "导入失败，请检查文件格式");
  } finally {
    importDialog.loading = false;
  }
}

function goDetail(id: string) { router.push(`/app/customers/${id}`); }
async function loadIcpOptions() {
  try { const { data } = await api.get("/icps", { params: { page_size: 50 } }); icpFilterOptions.value = data.items || []; } catch { /* */ }
}

onMounted(() => { loadData(); loadIcpOptions(); loadStatusCounts(); });
</script>

<style scoped lang="scss">
.customer-list-page {
  // ── 数据概览条 ──
  .stats-bar {
    display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;
    .stat-item {
      display: flex; align-items: center; gap: 8px;
      background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
      padding: 10px 16px; min-width: 100px;
      .stat-dot { width: 8px; height: 8px; border-radius: 50%; }
      .stat-val { font-size: 20px; font-weight: 700; color: #1e293b; }
      .stat-lbl { font-size: 12px; color: #94a3b8; }
    }
    .stat-new .stat-dot { background: #3b82f6; }
    .stat-contacted .stat-dot { background: #f59e0b; }
    .stat-qualified .stat-dot { background: #10b981; }
    .stat-negotiating .stat-dot { background: #6366f1; }
    .stat-closed .stat-dot { background: #059669; }
  }
  .filter-card { margin-bottom: 16px; border-radius: 8px; }
  .filter-form :deep(.el-form-item) { margin-bottom: 0; }
  .batch-bar {
    display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
    padding: 10px 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;
  }
  .batch-info { font-size: 13px; font-weight: 500; color: #1e40af; }
  .table-card { border-radius: 14px; border: 1px solid #e2e8f0; }
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
  .search-progress {
    margin-top: 16px; padding: 16px; background: #f8fafc;
    border-radius: 8px; border: 1px solid #e2e8f0;
  }
  .search-result-summary { text-align: center; p { margin: 0 0 12px 0; font-size: 14px; color: #334155; } }

  // ── 行内状态选择器 ──
  .status-select {
    width: 110px;
    :deep(.el-input__wrapper) {
      padding: 0 8px; border-radius: 10px; font-size: 12px; font-weight: 600;
      box-shadow: none;
    }
    :deep(.el-select__placeholder) { font-size: 12px; }
    &.status-new :deep(.el-input__wrapper) { background: #eff6ff; color: #2563eb; .el-input__inner { color: #2563eb; } }
    &.status-contacted :deep(.el-input__wrapper) { background: #fef3c7; color: #d97706; .el-input__inner { color: #d97706; } }
    &.status-qualified :deep(.el-input__wrapper) { background: #ecfdf5; color: #059669; .el-input__inner { color: #059669; } }
    &.status-negotiating :deep(.el-input__wrapper) { background: #eef2ff; color: #4f46e5; .el-input__inner { color: #4f46e5; } }
    &.status-closed :deep(.el-input__wrapper) { background: #e0f2fe; color: #0284c7; .el-input__inner { color: #0284c7; } }
    &.status-rejected :deep(.el-input__wrapper) { background: #fef2f2; color: #dc2626; .el-input__inner { color: #dc2626; } }
  }

  // ── 导入弹窗 ──
  .import-body {
    .import-upload-area {
      :deep(.el-upload-dragger) { padding: 32px 20px; }
    }
    .import-result {
      text-align: center; padding: 24px 16px;
      .import-result-icon { font-size: 48px; margin-bottom: 12px; }
      .import-result-title { margin: 0 0 20px; font-size: 18px; color: #1e293b; }
      .import-stats {
        display: flex; justify-content: center; gap: 24px; margin-bottom: 16px;
        .import-stat {
          display: flex; flex-direction: column; align-items: center;
          padding: 16px 32px; border-radius: 12px; min-width: 100px;
          .stat-num { font-size: 32px; font-weight: 800; }
          .stat-label { font-size: 13px; color: #64748b; margin-top: 4px; }
          &.created { background: #ecfdf5; .stat-num { color: #059669; } }
          &.skipped { background: #fef3c7; .stat-num { color: #d97706; } }
        }
      }
      .import-errors {
        text-align: left; margin-top: 12px; padding: 12px 16px;
        background: #fef2f2; border-radius: 8px; max-height: 180px; overflow-y: auto;
        .import-errors-title { margin: 0 0 8px; font-size: 13px; font-weight: 600; color: #dc2626; }
        ul { margin: 0; padding-left: 20px; font-size: 13px; color: #7f1d1d; line-height: 1.8; }
      }
    }
  }
}
</style>
