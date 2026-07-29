<template>
  <div class="page-admin-tenants">
    <div class="page-header">
      <h2>租户管理</h2>
      <p class="page-desc">管理平台所有租户账户</p>
    </div>

    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="12" align="middle">
        <el-col :span="8">
          <el-input v-model="search" placeholder="搜索租户名称..." clearable @keyup.enter="fetchData" @clear="fetchData" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="planFilter" placeholder="套餐筛选" clearable @change="fetchData" style="width:100%">
            <el-option label="全部" value="" />
            <el-option label="免费版" value="free" />
            <el-option label="专业版" value="pro" />
            <el-option label="企业版" value="enterprise" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="fetchData" style="width:100%">
            <el-option label="全部" value="" />
            <el-option label="正常" value="active" />
            <el-option label="已停用" value="suspended" />
            <el-option label="已注销" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="fetchData">搜索</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 列表 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="list" v-loading="loading" stripe @row-click="(row: TenantRow) => router.push(`/admin/tenants/${row.id}`)" style="cursor:pointer">
        <el-table-column prop="name" label="租户名称" min-width="180" />
        <el-table-column prop="plan_type" label="套餐" width="100">
          <template #default="{ row }">
            <el-tag :type="planTag(row.plan_type)" size="small">{{ planLabel(row.plan_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statTag(row.status)" size="small">{{ statLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="用户数" width="80" />
        <el-table-column prop="icp_count" label="画像数" width="80" />
        <el-table-column prop="customer_count" label="客户数" width="80" />
        <el-table-column prop="email_sent_count" label="已发邮件" width="90" />
        <el-table-column prop="created_at" label="入驻时间" width="180">
          <template #default="{ row }">{{ fmt(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click.stop="$router.push(`/admin/tenants/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import api from "@/api/client";

interface TenantRow {
  id: string;
  name: string;
  plan_type: string;
  status: string;
  user_count: number;
  icp_count: number;
  customer_count: number;
  email_sent_count: number;
  created_at: string;
}

const router = useRouter();
const list = ref<TenantRow[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(20);
const loading = ref(false);
const search = ref("");
const planFilter = ref("");
const statusFilter = ref("");

const planMap: Record<string, string> = { free: "免费版", pro: "专业版", enterprise: "企业版" };
const planTagMap: Record<string, string> = { free: "info", pro: "warning", enterprise: "success" };
const statMap: Record<string, string> = { active: "正常", suspended: "已停用", cancelled: "已注销" };
const statTagMap: Record<string, string> = { active: "success", suspended: "warning", cancelled: "danger" };

function planLabel(v: string) { return planMap[v] || v; }
function planTag(v: string) { return planTagMap[v] || "info"; }
function statLabel(v: string) { return statMap[v] || v; }
function statTag(v: string) { return statTagMap[v] || "info"; }
function fmt(d: string) { return d ? new Date(d).toLocaleDateString("zh-CN") : "-"; }

async function fetchData() {
  loading.value = true;
  try {
    const { data } = await api.get("/admin/tenants", {
      params: {
        page: page.value,
        page_size: pageSize.value,
        search: search.value || undefined,
        plan_type: planFilter.value || undefined,
        status: statusFilter.value || undefined,
      },
    });
    list.value = data.items;
    total.value = data.total;
  } catch {
    ElMessage.error("加载租户列表失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchData());
</script>

<style scoped>
.page-admin-tenants { padding: 0; }
.page-header { margin-bottom: 16px; }
.page-header h2 { margin: 0 0 4px; font-size: 22px; }
.page-desc { margin: 0; color: var(--el-text-color-secondary); font-size: 14px; }
.filter-card { margin-bottom: 16px; }
.table-card { border-radius: 8px; }
.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
