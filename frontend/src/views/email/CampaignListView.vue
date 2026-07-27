<template>
  <div class="campaign-list-page">
    <PageHeader title="发送任务">
      <template #actions>
        <el-button type="primary" @click="openCreateWizard">
          <el-icon><Plus /></el-icon>新建发送任务
        </el-button>
      </template>
    </PageHeader>

    <el-card class="table-card">
      <LoadingSkeleton v-if="store.campaignsLoading" variant="table" />
      <EmptyState v-else-if="!store.campaigns.length" description="暂无发送任务"
        action-text="创建第一个任务" @action="openCreateWizard" />
      <template v-else>
        <el-table :data="store.campaigns" stripe @row-click="(r: CampaignItem) => goDetail(r.id)" style="cursor:pointer">
          <el-table-column prop="name" label="任务名称" min-width="160" />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }"><StatusBadge :status="row.status" /></template>
          </el-table-column>
          <el-table-column label="进度" width="180" align="center">
            <template #default="{ row }">
              <template v-if="row.total_recipients > 0">
                <el-progress :percentage="Math.round(row.sent_count / row.total_recipients * 100)"
                  :status="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'exception' : undefined"
                  :stroke-width="14" />
                <small style="color:#94a3b8">{{ row.sent_count }}/{{ row.total_recipients }}</small>
              </template>
              <span v-else style="color:#94a3b8">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="opened_count" label="已打开" width="80" align="center" />
          <el-table-column prop="created_at" label="创建" width="160">
            <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString("zh-CN") }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click.stop="goDetail(row.id)">详情</el-button>
              <el-button v-if="row.status === 'draft'" link type="success" size="small" @click.stop="startSend(row.id)">发送</el-button>
              <el-button link type="danger" size="small" @click.stop="confirmDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination v-model:current-page="page" v-model:page-size="pageSize"
            :total="store.campaignsTotal" :page-sizes="[10, 20]" layout="total, prev, pager, next"
            @current-change="loadData" @size-change="loadData" />
        </div>
      </template>
    </el-card>

    <!-- ============ 创建向导弹窗 ============ -->
    <el-dialog v-model="wizard.visible" title="新建发送任务" width="760px"
      :close-on-click-modal="false" @closed="resetWizard">
      <!-- 步骤条 -->
      <el-steps :active="wizard.step" finish-status="success" align-center style="margin-bottom:28px">
        <el-step title="选择模板" />
        <el-step title="选择客户" />
        <el-step title="配置发送" />
      </el-steps>

      <!-- 加载模板 -->
      <div v-if="wizard.tplLoading" v-loading="true" style="min-height:160px" />

      <!-- Step 0: 选择模板 — 卡片式 -->
      <div v-show="wizard.step === 0 && !wizard.tplLoading" class="wizard-step-body">
        <el-alert v-if="wizard.tplError" :title="wizard.tplError" type="error" show-icon style="margin-bottom:16px" />
        <template v-if="tplOptions.length === 0">
          <EmptyState description="暂无可用模板"
            action-text="去创建模板" @action="$router.push('/app/email/templates')" />
        </template>
        <div v-else class="tpl-card-list">
          <div
            v-for="tpl in tplOptions"
            :key="tpl.id"
            :class="['tpl-card', { selected: wizard.templateId === tpl.id }]"
            @click="wizard.templateId = tpl.id"
          >
            <div class="tpl-card-radio">
              <span :class="['radio-dot', { on: wizard.templateId === tpl.id }]" />
            </div>
            <div class="tpl-card-body">
              <div class="tpl-card-name">{{ tpl.name }}</div>
              <div class="tpl-card-subject">{{ tpl.subject || '（无主题）' }}</div>
              <div class="tpl-card-meta">
                <el-tag size="small" :type="tpl.tone === 'formal' ? 'primary' : 'success'">
                  {{ tpl.tone === 'formal' ? '正式' : '友好' }}
                </el-tag>
                <span class="tpl-card-status">状态：<StatusBadge :status="tpl.status" /></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 1: 选择客户 -->
      <div v-show="wizard.step === 1" class="wizard-step-body">
        <!-- 加载中 -->
        <div v-if="wizard.custLoading" v-loading="true" style="min-height:160px" />

        <template v-else>
          <div class="cust-toolbar">
            <el-input v-model="customerSearch" placeholder="搜索公司名/行业" clearable style="width:200px" />
            <el-select v-model="icpFilter" placeholder="客户画像" clearable style="width:160px">
              <el-option v-for="icp in icpFilterOptions" :key="icp.id" :label="icp.name" :value="icp.id" />
            </el-select>
            <el-select v-model="customerFilter" placeholder="国家筛选" clearable style="width:130px" @change="() => {}">
              <el-option v-for="c in countryOptions" :key="c" :label="c" :value="c" />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="添加时间起"
              end-placeholder="添加时间止"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width:240px"
              clearable
            />
            <span class="cust-count">
              共 {{ filteredCustomers.length }} 个可选客户（已选 {{ wizard.customerIds.length }} 个）
              <template v-if="customers.length > 0">
                · 总计 {{ customers.length }} 个客户，
                <span style="color:#f59e0b">{{ customers.length - customers.filter(c => c.contacts_with_email_count > 0).length }} 个</span> 无邮箱联系人暂不可选
              </template>
            </span>
          </div>

          <el-alert v-if="customersLoaded && customers.length === 0"
            title="暂无客户数据，请先添加客户" type="info" show-icon
            style="margin-bottom:12px" />

          <el-table v-if="filteredCustomers.length > 0"
            :data="filteredCustomers" stripe
            @selection-change="(rows: any) => wizard.customerIds = rows.map((r: any) => r.id)"
            ref="customerTable" max-height="300">
            <el-table-column type="selection" width="44" />
            <el-table-column prop="name" label="公司名称" min-width="160" />
            <el-table-column prop="country" label="国家" width="100">
              <template #default="{ row }">{{ row.country || "—" }}</template>
            </el-table-column>
            <el-table-column label="有邮箱联系人" width="120" align="center">
                <template #default="{ row }">
                  <span :style="{ color: row.contacts_with_email_count > 0 ? '#10b981' : '#ef4444' }">
                    {{ row.contacts_with_email_count }}/{{ row.contacts_count }}
                  </span>
                </template>
              </el-table-column>
          </el-table>
          <EmptyState v-else-if="customersLoaded && customers.length === 0"
            description="暂无客户数据，请先在客户管理中搜索并添加客户" />
          <EmptyState v-else-if="customersLoaded && filteredCustomers.length === 0"
            description="所有客户均无邮箱联系人，无法发送邮件。请在客户详情页为相关客户添加联系人邮箱" />
        </template>
      </div>

      <!-- Step 2: 配置发送 -->
      <div v-show="wizard.step === 2" class="wizard-step-body">
        <!-- 说明提示 -->
        <el-alert type="info" :closable="false" style="margin-bottom:20px">
          <template #title>
            请填写<strong>用于发送邮件的外部邮箱</strong>的 SMTP 连接信息，并非您当前登录账号的密码
          </template>
          <template #default>
            常用邮箱 SMTP 配置参考：
            Gmail：smtp.gmail.com，端口 465（SSL），需使用「应用专用密码」；
            QQ 邮箱：smtp.qq.com，端口 465（SSL），需使用「授权码」；
            163 邮箱：smtp.163.com，端口 465（SSL），需使用「授权码」
          </template>
        </el-alert>

        <el-form ref="smtpFormRef" :model="wizard.smtp" :rules="smtpRules" label-position="top" label-width="auto">
          <!-- 服务器配置 -->
          <div class="form-section-title">邮件服务器</div>
          <el-row :gutter="16">
            <el-col :span="14">
              <el-form-item label="SMTP 服务器地址" prop="host">
                <el-input v-model="wizard.smtp.host" placeholder="smtp.gmail.com" />
              </el-form-item>
            </el-col>
            <el-col :span="4">
              <el-form-item label="端口" prop="port">
                <el-input-number v-model="wizard.smtp.port" :min="1" :max="65535" />
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 发件邮箱认证 -->
          <div class="form-section-title">发件邮箱认证</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="发件邮箱地址" prop="username">
                <el-input v-model="wizard.smtp.username" placeholder="your-email@gmail.com" />
                <div class="form-extra">用于登录 SMTP 服务器的邮箱账号</div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱授权码">
                <el-input
                  v-model="wizard.smtp.password"
                  type="password" show-password
                  :placeholder="wizard.smtpPrefilled ? '留空将使用系统设置中保存的授权码' : '邮箱服务商生成的授权码，非登录密码'"
                />
                <div class="form-extra">
                  <template v-if="wizard.smtpPrefilled">
                    留空将自动使用<a href="/app/settings" target="_blank">系统设置</a>中已保存的授权码
                  </template>
                  <template v-else>不是邮箱登录密码，是 SMTP 专用授权码</template>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <!-- 发件人显示信息 -->
          <div class="form-section-title">发件人显示信息</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="发件人名称">
                <el-input v-model="wizard.smtp.from_name" placeholder="如：张三 / ABC Company" />
                <div class="form-extra">收件人看到的发件人名称，发件邮箱即为认证邮箱地址</div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <!-- 发送摘要 -->
        <el-alert v-if="wizard.templateId && wizard.customerIds.length" type="success" :closable="false" style="margin-top:16px">
          <template #title>
            发送摘要：向 <strong>{{ wizard.customerIds.length }}</strong> 个客户的联系人发送邮件
          </template>
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="wizard.visible = false">取消</el-button>
        <el-button v-if="wizard.step > 0" @click="wizard.step--">上一步</el-button>
        <el-button v-if="wizard.step < 2" type="primary" @click="nextStep"
          :loading="wizard.step === 0 && wizard.tplLoading">
          {{ wizard.step === 0 ? '下一步：选择客户' : '下一步：配置发送' }}
        </el-button>
        <el-button v-if="wizard.step === 2" type="primary" :loading="creating" @click="handleCreate">
          创建并发送
        </el-button>
      </template>
    </el-dialog>

    <ConfirmDialog v-model:visible="delDialog.visible" title="删除任务"
      :message="`确定删除「${delDialog.name}」吗？`"
      confirm-type="danger" confirm-text="删除" :loading="deleting" @confirm="handleDelete" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import PageHeader from "@/components/common/PageHeader.vue";
import LoadingSkeleton from "@/components/common/LoadingSkeleton.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import StatusBadge from "@/components/common/StatusBadge.vue";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";
import { useEmailStore, type CampaignItem, type EmailTemplateItem } from "@/stores/email";
import { useCustomerStore, type CustomerListItem } from "@/stores/customer";
import api from "@/api/client";

const router = useRouter();
const store = useEmailStore();
const customerStore = useCustomerStore();
const page = ref(1); const pageSize = ref(20);

function loadData() { store.fetchCampaigns({ page: page.value, page_size: pageSize.value }); }
function goDetail(id: string) { router.push(`/app/email/campaigns/${id}`); }

// ── 自动轮询：有发送中的任务时每 3 秒刷新进度 ──
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null);
const hasSending = computed(() => store.campaigns.some(c => c.status === "sending"));

function startPolling() {
  if (pollingTimer.value) return;
  pollingTimer.value = setInterval(() => {
    if (!hasSending.value) { stopPolling(); return; }
    loadData();
  }, 3000);
}

function stopPolling() {
  if (pollingTimer.value) { clearInterval(pollingTimer.value); pollingTimer.value = null; }
}

watch(hasSending, (val) => { if (val) startPolling(); else stopPolling(); });
onBeforeUnmount(stopPolling);

// ── 创建向导 ──
const tplOptions = ref<EmailTemplateItem[]>([]);
const customers = ref<CustomerListItem[]>([]);
const customersLoaded = ref(false);
const customerSearch = ref("");
const customerFilter = ref("");
const icpFilter = ref("");
const dateRange = ref<[string, string] | null>(null);
const icpFilterOptions = ref<{ id: string; name: string }[]>([]);
const customerTable = ref();
const smtpFormRef = ref<FormInstance>();
const creating = ref(false);

// SMTP 表单校验规则（密码非必填：留空则使用系统设置中保存的授权码）
const smtpRules: FormRules = {
  host: [
    { required: true, message: "请填写 SMTP 服务器地址", trigger: "blur" },
  ],
  port: [
    { required: true, message: "请填写端口号", trigger: "blur" },
  ],
  username: [
    { required: true, message: "请填写发件邮箱地址", trigger: "blur" },
  ],
};

const wizard = reactive({
  visible: false, step: 0,
  templateId: "" as string | null,
  customerIds: [] as string[],
  tplLoading: false,
  tplError: "",
  custLoading: false,
  smtpPrefilled: false,  // 是否已从系统设置预填（预填后密码非必填）
  smtp: {
    host: "smtp.gmail.com", port: 465,
    username: "", password: "",
    from_name: "",
  },
});

// 国家去重选项
const countryOptions = computed(() => {
  const set = new Set<string>();
  customers.value.forEach(c => { if (c.country) set.add(c.country); });
  return Array.from(set).sort();
});

// 筛选客户（必须有联系人邮箱）
const filteredCustomers = computed(() => {
  let list = customers.value.filter(c => c.contacts_with_email_count > 0);
  if (customerSearch.value) {
    const q = customerSearch.value.toLowerCase();
    list = list.filter(c => c.name.toLowerCase().includes(q) || (c.industry || "").toLowerCase().includes(q));
  }
  if (icpFilter.value) {
    list = list.filter(c => c.icp_id === icpFilter.value);
  }
  if (customerFilter.value) {
    list = list.filter(c => c.country === customerFilter.value);
  }
  if (dateRange.value) {
    const [start, end] = dateRange.value;
    const startDate = new Date(start);
    const endDate = new Date(end + "T23:59:59");
    list = list.filter(c => {
      const d = new Date(c.created_at);
      return d >= startDate && d <= endDate;
    });
  }
  return list;
});

async function openCreateWizard() {
  wizard.visible = true;
  wizard.step = 0;
  wizard.templateId = "";
  wizard.customerIds = [];
  wizard.tplLoading = true;
  wizard.tplError = "";
  try {
    const { data } = await api.get("/email-templates", { params: { page_size: 50, status: "ready" } });
    tplOptions.value = data.items || [];
    if (tplOptions.value.length === 0) {
      wizard.tplError = "暂无状态为「就绪」的模板，请先在模板管理中创建并审核通过";
    }
  } catch (err: any) {
    wizard.tplError = err?.response?.data?.detail || "加载模板失败，请稍后重试";
    tplOptions.value = [];
  } finally {
    wizard.tplLoading = false;
  }
}

async function loadCustomers() {
  wizard.custLoading = true;
  customersLoaded.value = false;
  icpFilter.value = "";
  dateRange.value = null;
  try {
    await customerStore.fetchList({ page_size: 500 });
    customers.value = customerStore.list;
    customersLoaded.value = true;
    // 加载 ICP 列表供筛选
    try {
      const { data } = await api.get("/icps", { params: { page: 1, page_size: 50 } });
      icpFilterOptions.value = data.items || [];
    } catch { icpFilterOptions.value = []; }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "加载客户列表失败");
    customers.value = [];
    customersLoaded.value = true;
  } finally {
    wizard.custLoading = false;
  }
}

async function nextStep() {
  if (wizard.step === 0) {
    if (!wizard.templateId) { ElMessage.warning("请先选择一个模板"); return; }
    wizard.step = 1;
    await loadCustomers();
    return;
  }
  if (wizard.step === 1) {
    if (!wizard.customerIds.length) { ElMessage.warning("请选择至少一个客户"); return; }
    wizard.step = 2;
    // 从系统设置预填 SMTP 配置（密码不会返回，留空则后端自动使用已保存的授权码）
    try {
      const { data } = await api.get("/settings/smtp");
      if (data && data.host) {
        wizard.smtp.host = data.host;
        wizard.smtp.port = data.port || 465;
        wizard.smtp.username = data.username || "";
        wizard.smtp.from_name = data.from_name || "";
        wizard.smtp.password = "";  // 密码由后端从租户配置自动获取
        wizard.smtpPrefilled = true;
      }
    } catch { /* 无默认配置则使用表单填写的值 */ }
    return;
  }
}

async function handleCreate() {
  // 校验 SMTP 表单 — 未通过时自动滚动到第一个错误字段并标红
  if (!smtpFormRef.value) return;
  try {
    await smtpFormRef.value.validate();
  } catch {
    // Element Plus 表单校验失败时 reject，各字段已自动标红并显示中文错误信息
    return;
  }
  creating.value = true;
  try {
    const selectedTpl = tplOptions.value.find(t => t.id === wizard.templateId);
    const tplName = selectedTpl?.name || "未命名模板";
    const now = new Date();
    const timeStr = `${now.toLocaleDateString("zh-CN")} ${now.toTimeString().slice(0, 5)}`;
    const payload = {
      name: `${tplName} — ${timeStr}`,
      template_id: wizard.templateId,
      customer_ids: wizard.customerIds,
      smtp_config: { ...wizard.smtp },
    };
    const campaign = await store.createCampaign(payload);
    wizard.visible = false;
    ElMessage.success("发送任务已创建，正在启动发送...");
    loadData();
    // 创建后直接发送，无需到列表页再操作
    try {
      await store.sendCampaign(campaign.id);
      ElMessage.success("发送已启动");
      loadData();
    } catch {
      // sendCampaign 错误已由拦截器处理
    }
  } catch {
    // 错误提示已由 API 拦截器统一翻译并展示，此处仅恢复按钮状态
  } finally {
    creating.value = false;
  }
}

function resetWizard() {
  wizard.step = 0;
  wizard.templateId = "";
  wizard.customerIds = [];
  wizard.tplError = "";
  wizard.smtpPrefilled = false;
  wizard.smtp = { host: "smtp.gmail.com", port: 465, username: "", password: "", from_name: "" };
  tplOptions.value = [];
  customers.value = [];
  customersLoaded.value = false;
  smtpFormRef.value?.resetFields();
}

// ── 发送 ──
async function startSend(id: string) {
  try {
    await store.sendCampaign(id);
    ElMessage.success("发送已启动");
    loadData();
  } catch {
    // 错误提示已由 API 拦截器统一处理
  }
}

// ── 删除 ──
const deleting = ref(false);
const delDialog = reactive({ visible: false, id: "", name: "" });
function confirmDelete(row: CampaignItem) { delDialog.id = row.id; delDialog.name = row.name; delDialog.visible = true; }
async function handleDelete() {
  deleting.value = true;
  try { await store.removeCampaign(delDialog.id); ElMessage.success("已删除"); delDialog.visible = false; loadData(); }
  catch { ElMessage.error("删除失败"); } finally { deleting.value = false; }
}

onMounted(loadData);
</script>

<style scoped lang="scss">
.campaign-list-page {
  .table-card { border-radius: 14px; border: 1px solid #e2e8f0; }
  .pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
}

// ── 向导通用 ──
.wizard-step-body {
  min-height: 200px;
}

// ── 模板卡片 ──
.tpl-card-list {
  display: flex; flex-direction: column; gap: 10px;
}
.tpl-card {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 16px 18px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  &:hover { border-color: #93c5fd; background: #f8faff; }
  &.selected {
    border-color: #3b82f6;
    background: #eff6ff;
    box-shadow: 0 0 0 3px rgba(59,130,246,.12);
  }
}
.tpl-card-radio {
  padding-top: 2px;
  .radio-dot {
    display: block; width: 20px; height: 20px;
    border-radius: 50%; border: 2px solid #cbd5e1;
    background: #fff; transition: all 0.2s;
    &.on {
      border-color: #3b82f6; background: #3b82f6;
      box-shadow: inset 0 0 0 4px #fff;
    }
  }
}
.tpl-card-body { flex: 1; min-width: 0; }
.tpl-card-name { font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.tpl-card-subject { font-size: 13px; color: #64748b; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tpl-card-meta { display: flex; align-items: center; gap: 10px; }
.tpl-card-status { font-size: 12px; color: #94a3b8; }

// ── 发送配置 ──
.form-section-title {
  font-size: 14px; font-weight: 600; color: #334155;
  margin: 16px 0 10px 0; padding-bottom: 6px;
  border-bottom: 1px solid #e2e8f0;
  &:first-child { margin-top: 0; }
}
.form-extra {
  font-size: 12px; color: #94a3b8;
}

// ── 客户选择 ──
.cust-toolbar {
  display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap;
}
.cust-count {
  font-size: 13px; color: #64748b; margin-left: auto;
  strong { color: #1e293b; }
}
</style>
