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

    <!-- 客户画像维度统计（可点击筛选） -->
    <div class="icp-stats-bar">
      <div class="icp-stat-card" :class="{ active: !filters.icp_id && !filters.status }" @click="filterByIcp('', '')">
        <div class="icp-stat-card__header">
          <el-icon :size="18"><UserFilled /></el-icon>
          <span class="icp-stat-card__name">全部客户</span>
        </div>
        <span class="icp-stat-card__total">{{ store.total }}</span>
      </div>
      <div
        v-for="icp in icpStats"
        :key="icp.icp_id || '__unassigned__'"
        class="icp-stat-card"
        :class="{ active: filters.icp_id === icp.icp_id || (icp.icp_id === null && filters.icp_id === '__none__') }"
        @click="filterByIcp(icp.icp_id || '__none__', '')"
      >
        <div class="icp-stat-card__header">
          <span class="icp-stat-card__dot" :style="{ background: icp.icp_id ? '#3b82f6' : '#94a3b8' }"></span>
          <span class="icp-stat-card__name">{{ icp.icp_name }}</span>
        </div>
        <span class="icp-stat-card__total">{{ icp.total }}</span>
        <div class="icp-stat-card__statuses">
          <span v-if="icp.statuses?.new" class="status-dot status-new">{{ icp.statuses.new }}</span>
          <span v-if="icp.statuses?.contacted" class="status-dot status-contacted">{{ icp.statuses.contacted }}</span>
          <span v-if="icp.statuses?.qualified" class="status-dot status-qualified">{{ icp.statuses.qualified }}</span>
          <span v-if="icp.statuses?.negotiating" class="status-dot status-negotiating">{{ icp.statuses.negotiating }}</span>
          <span v-if="icp.statuses?.closed" class="status-dot status-closed">{{ icp.statuses.closed }}</span>
        </div>
      </div>
    </div>

    <!-- 后台搜索任务进度面板 -->
    <div v-if="searchTasks.length > 0" class="search-tasks-panel">
      <div class="search-tasks-header" @click="tasksExpanded = !tasksExpanded">
        <div class="search-tasks-title">
          <el-icon :size="16"><Clock /></el-icon>
          <span>后台任务</span>
          <el-tag v-if="activeTaskCount > 0" size="small" type="warning" round>{{ activeTaskCount }} 个进行中</el-tag>
        </div>
        <el-icon :class="{ rotated: tasksExpanded }"><ArrowDown /></el-icon>
      </div>
      <div v-show="tasksExpanded" class="search-tasks-body">
        <div v-for="task in searchTasks" :key="task.task_id" class="search-task-item"
          :class="`task-${task.status}`" @click="openTaskDetail(task)">
          <!-- 运行中/等待中 -->
          <template v-if="task.status === 'pending' || task.status === 'running'">
            <div class="task-item-header">
              <el-icon class="task-icon is-loading" :size="16"><Loading /></el-icon>
              <span class="task-icp-name">{{ task.icp_name }}</span>
              <span class="task-channels">{{ task.channels?.join(', ') }}</span>
            </div>
            <div class="task-item-progress">
              <span class="task-section">{{ sectionLabel(task.current_section) }}</span>
              <span class="task-message">{{ task.progress_message }}</span>
            </div>
            <div class="task-progress-bar">
              <div class="task-progress-fill" :style="{ width: progressPercent(task) + '%' }"></div>
            </div>
          </template>
          <!-- 已完成 -->
          <template v-else-if="task.status === 'completed'">
            <div class="task-item-header">
              <el-icon class="task-icon task-done" :size="16"><CircleCheckFilled /></el-icon>
              <span class="task-icp-name">{{ task.icp_name }}</span>
              <span class="task-result-text">
                保存 <strong>{{ task.result?.saved_count || 0 }}</strong> 个客户
                <template v-if="task.result?.contact_search_count || task.result?.enriched_count">
                  ，找到 <strong>{{ (task.result?.contact_search_count || 0) + (task.result?.enriched_count || 0) }}</strong> 个联系人
                </template>
              </span>
              <span class="task-time">{{ formatTimeAgo(task.updated_at) }}</span>
            </div>
          </template>
          <!-- 失败 -->
          <template v-else-if="task.status === 'failed'">
            <div class="task-item-header">
              <el-icon class="task-icon task-error" :size="16"><CircleCloseFilled /></el-icon>
              <span class="task-icp-name">{{ task.icp_name }}</span>
              <span class="task-error-text">搜索失败：{{ task.error || '未知错误' }}</span>
              <span class="task-time">{{ formatTimeAgo(task.updated_at) }}</span>
            </div>
          </template>
          <el-button v-if="task.status === 'completed' || task.status === 'failed'"
            class="task-dismiss-btn" link size="small" @click="dismissTask(task.task_id)">
            关闭
          </el-button>
        </div>
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
            <el-form-item label="客户画像" prop="icp_id">
              <el-select v-model="form.icp_id" placeholder="选择画像（可选）" clearable style="width: 100%">
                <el-option
                  v-for="icp in icpFilterOptions"
                  :key="icp.id"
                  :label="icp.name"
                  :value="icp.id"
                />
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
            <el-checkbox label="linkedin_people">LinkedIn 人物搜索</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="目标区域（可选）">
          <el-input v-model="searchDialog.region" placeholder="如：Germany, USA" :disabled="searching" />
        </el-form-item>
      </el-form>
      <div v-if="searching || searchDone" class="search-progress">
        <StreamingOutput
          :is-streaming="searching"
          :current-section="searchCurrentSection"
          :error="searchError"
          :done="searchDone"
          :section-list="searchSectionList"
          :thinking-texts="searchThinkingTexts"
          done-text="客户搜索完成"
        >
          <template #done>
            <div class="search-result-summary">
              <p v-if="savedCount > 0">
                成功保存 <strong>{{ savedCount }}</strong> 个客户
                <span v-if="contactSearchCount > 0">，定向搜索找到 <strong>{{ contactSearchCount }}</strong> 个联系人</span>
                <span v-if="enrichedCount > 0">，网站抓取 <strong>{{ enrichedCount }}</strong> 个联系人</span>
              </p>
              <p v-else>未找到可保存的客户数据</p>
              <el-button type="primary" @click="searchDialog.visible = false; loadData()">关闭并刷新列表</el-button>
            </div>
          </template>
        </StreamingOutput>
      </div>
      <template #footer>
        <el-button @click="searchDialog.visible = false">关闭</el-button>
        <el-button type="default" :disabled="!searchDialog.icpId || !searchDialog.channels.length"
          @click="startBackgroundSearch">
          后台执行
        </el-button>
        <el-button type="primary" :loading="searching"
          :disabled="!searchDialog.icpId || !searchDialog.channels.length" @click="startSearch">
          开始搜索
        </el-button>
      </template>
    </el-dialog>

    <!-- 搜索任务详情弹窗 -->
    <el-dialog v-model="taskDetailDialog.visible" title="搜索任务详情" width="520px" :close-on-click-modal="false">
      <template v-if="taskDetailDialog.task">
        <div class="task-detail">
          <div class="task-detail-row">
            <span class="task-detail-label">客户画像</span>
            <span class="task-detail-value">{{ taskDetailDialog.task.icp_name }}</span>
          </div>
          <div class="task-detail-row">
            <span class="task-detail-label">搜索渠道</span>
            <span class="task-detail-value">{{ taskDetailDialog.task.channels?.join(', ') }}</span>
          </div>
          <div class="task-detail-row">
            <span class="task-detail-label">状态</span>
            <el-tag v-if="taskDetailDialog.task.status === 'completed'" type="success" size="small">已完成</el-tag>
            <el-tag v-else-if="taskDetailDialog.task.status === 'failed'" type="danger" size="small">失败</el-tag>
            <el-tag v-else type="warning" size="small">进行中</el-tag>
          </div>
          <div class="task-detail-row">
            <span class="task-detail-label">创建时间</span>
            <span class="task-detail-value">{{ new Date(taskDetailDialog.task.created_at).toLocaleString('zh-CN') }}</span>
          </div>
          <template v-if="taskDetailDialog.task.status === 'completed'">
            <el-divider />
            <div class="task-detail-section-title">搜索统计</div>
            <div class="task-detail-stats">
              <div class="task-detail-stat">
                <span class="stat-num">{{ taskDetailDialog.task.result?.total_found || 0 }}</span>
                <span class="stat-label">搜索命中</span>
              </div>
              <div class="task-detail-stat">
                <span class="stat-num">{{ taskDetailDialog.task.result?.saved_count || 0 }}</span>
                <span class="stat-label">保存客户</span>
              </div>
              <div class="task-detail-stat">
                <span class="stat-num">{{ (taskDetailDialog.task.result?.contact_search_count || 0) + (taskDetailDialog.task.result?.enriched_count || 0) }}</span>
                <span class="stat-label">发现联系人</span>
              </div>
            </div>
            <el-divider />
            <div class="task-detail-section-title">联系人来源明细</div>
            <div class="task-detail-breakdown">
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background:#6366f1"></span>
                <span>定向搜索</span>
                <span class="breakdown-count">{{ taskDetailDialog.task.result?.contact_search_count || 0 }}</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-dot" style="background:#22c55e"></span>
                <span>网站抓取</span>
                <span class="breakdown-count">{{ taskDetailDialog.task.result?.enriched_count || 0 }}</span>
              </div>
            </div>
          </template>
          <template v-else-if="taskDetailDialog.task.status === 'running' || taskDetailDialog.task.status === 'pending'">
            <el-divider />
            <div class="task-detail-section-title">当前进度</div>
            <div class="task-detail-progress">
              <p>{{ taskDetailDialog.task.progress_message }}</p>
              <el-progress :percentage="progressPercent(taskDetailDialog.task)" :show-text="true" />
            </div>
          </template>
          <template v-else-if="taskDetailDialog.task.status === 'failed'">
            <el-divider />
            <div class="task-detail-section-title">错误信息</div>
            <el-alert type="error" :title="taskDetailDialog.task.error || '未知错误'" :closable="false" show-icon />
          </template>
        </div>
      </template>
      <template #footer>
        <el-button @click="taskDetailDialog.visible = false">关闭</el-button>
        <el-button v-if="taskDetailDialog.task?.status === 'completed' || taskDetailDialog.task?.status === 'failed'"
          type="primary" @click="dismissTask(taskDetailDialog.task?.task_id || ''); taskDetailDialog.visible = false">
          关闭并移除
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
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { Plus, Search, Download, UserFilled, Upload, Clock, ArrowDown, Loading, CircleCheckFilled, CircleCloseFilled } from "@element-plus/icons-vue";
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
interface IcpStat {
  icp_id: string | null;
  icp_name: string;
  total: number;
  statuses: Record<string, number>;
}
const icpStats = ref<IcpStat[]>([]);

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
async function loadIcpStats() {
  try {
    const { data } = await api.get("/dashboard/stats");
    icpStats.value = data.customer_icp_stats || [];
  } catch { /* */ }
}
function handleSearch() { pagination.page = 1; loadData(); }
function filterByIcp(icpId: string, status: string) {
  if (icpId === '__none__') {
    filters.icp_id = '__none__';  // 未关联画像
  } else {
    filters.icp_id = icpId;
  }
  filters.status = status;
  pagination.page = 1;
  loadData();
}
function filterByStatus(status: string) {
  filters.status = status;
  pagination.page = 1;
  loadData();
}
function handleReset() {
  filters.search = ""; filters.status = ""; filters.source = ""; filters.icp_id = "";
  pagination.page = 1; loadData(); loadIcpStats();
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
    selectedIds.value = []; batchStatus.value = ""; loadData(); loadIcpStats();
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
    loadIcpStats();
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
  company_size: "", description: "", source: "manual", status: "new", notes: "", icp_id: "",
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
      form.icp_id = detail.icp_id || "";
    } catch {
      // fallback to list item data
      form.name = row.name; form.industry = row.industry || "";
      form.country = row.country || ""; form.source = row.source; form.status = row.status;
      form.icp_id = row.icp_id || "";
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
const searchSectionList = [
  { key: "searching", label: "多渠道搜索" },
  { key: "deduping", label: "聚合去重" },
  { key: "saving", label: "AI 结构化提取 & 保存" },
  { key: "contact_search", label: "定向联系人搜索" },
  { key: "enriching", label: "抓取网站联系人" },
];
const searchThinkingTexts = [
  "正在多渠道搜索目标客户...",
  "正在聚合去重...",
  "正在 AI 结构化提取...",
  "正在定向搜索联系人...",
  "正在抓取网站联系人信息...",
];

const searching = ref(false);
const searchAbortController = ref<AbortController | null>(null);
const searchDone = ref(false);
const searchError = ref<string | null>(null);
const searchCurrentSection = ref<string | null>(null);
const savedCount = ref(0);
const enrichedCount = ref(0);
const contactSearchCount = ref(0);

// ── 后台任务 ──
interface SearchTask {
  task_id: string;
  tenant_id: string;
  icp_name: string;
  channels: string[];
  region: string | null;
  status: "pending" | "running" | "completed" | "failed";
  current_section: string | null;
  progress_message: string;
  result: {
    saved_count: number;
    enriched_count: number;
    contact_search_count: number;
    total_found: number;
  };
  error: string | null;
  created_at: string;
  updated_at: string;
}
const searchTasks = ref<SearchTask[]>([]);
const tasksExpanded = ref(true);
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null);
const taskDetailDialog = reactive({
  visible: false,
  task: null as SearchTask | null,
});

const activeTaskCount = computed(() =>
  searchTasks.value.filter((t) => t.status === "pending" || t.status === "running").length
);

const sectionLabels: Record<string, string> = {
  searching: "多渠道搜索",
  deduping: "聚合去重",
  saving: "AI 结构化提取 & 保存",
  contact_search: "定向联系人搜索",
  enriching: "抓取网站联系人",
};
function sectionLabel(section: string | null): string {
  if (!section) return "";
  return sectionLabels[section] || section;
}

function progressPercent(task: SearchTask): number {
  const order = ["searching", "deduping", "saving", "contact_search", "enriching"];
  const idx = order.indexOf(task.current_section || "");
  return idx >= 0 ? Math.round(((idx + 0.5) / order.length) * 100) : 10;
}

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const sec = Math.floor(diff / 1000);
  if (sec < 60) return `${sec} 秒前`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min} 分钟前`;
  const hr = Math.floor(min / 60);
  return `${hr} 小时前`;
}

async function openSearchDialog() {
  searchDialog.visible = true;
  searchDialog.icpId = ""; searchDialog.channels = ["duckduckgo"]; searchDialog.region = "";
  searchDone.value = false; searchError.value = null; searchCurrentSection.value = null;
  savedCount.value = 0; enrichedCount.value = 0; contactSearchCount.value = 0;
  try {
    const { data } = await api.get("/icps", { params: { page: 1, page_size: 50 } });
    icpOptions.value = data.items || [];
  } catch { icpOptions.value = []; }
}

// ── 后台搜索 ──
async function startBackgroundSearch() {
  if (!searchDialog.icpId || !searchDialog.channels.length) return;

  // 如果当前正在进行 SSE 搜索，先中止并转为后台执行
  const wasSearching = searching.value;
  if (wasSearching && searchAbortController.value) {
    searchAbortController.value.abort();
    searchAbortController.value = null;
    searching.value = false;
  }

  try {
    await api.post("/customers/search/background", {
      icp_id: searchDialog.icpId,
      channels: searchDialog.channels,
      region: searchDialog.region || null,
    });
    searchDialog.visible = false;
    tasksExpanded.value = true;
    ElMessage.success(wasSearching ? "搜索已转到后台执行" : "搜索任务已提交，可在页面顶部查看进度");
    fetchSearchTasks();
    startPolling();
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || "提交后台任务失败");
  }
}

async function fetchSearchTasks() {
  try {
    const { data } = await api.get("/customers/search/tasks");
    searchTasks.value = (data.tasks || []).slice(0, 10);
  } catch { /* ignore */ }
}

function startPolling() {
  stopPolling();
  pollingTimer.value = setInterval(() => {
    if (activeTaskCount.value > 0) {
      fetchSearchTasks();
    } else {
      stopPolling();
    }
  }, 3000);
}

function stopPolling() {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value);
    pollingTimer.value = null;
  }
}

function openTaskDetail(task: SearchTask) {
  taskDetailDialog.task = task;
  taskDetailDialog.visible = true;
}

function dismissTask(taskId: string) {
  searchTasks.value = searchTasks.value.filter((t) => t.task_id !== taskId);
  if (taskDetailDialog.task?.task_id === taskId) {
    taskDetailDialog.visible = false;
    taskDetailDialog.task = null;
  }
}

function startSearch() {
  if (!searchDialog.icpId || !searchDialog.channels.length) return;
  searching.value = true; searchDone.value = false; searchError.value = null; searchCurrentSection.value = null;
  savedCount.value = 0; enrichedCount.value = 0; contactSearchCount.value = 0;
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api/v1";
  const token = localStorage.getItem("access_token");
  const controller = new AbortController();
  searchAbortController.value = controller;
  fetch(`${baseUrl}/customers/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      icp_id: searchDialog.icpId, channels: searchDialog.channels,
      region: searchDialog.region || null,
    }),
    signal: controller.signal,
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
            if (event.type === "section") {
              searchCurrentSection.value = event.section || null;
            } else if (event.type === "complete") {
              savedCount.value = event.saved_count || 0;
              enrichedCount.value = event.enriched_count || 0;
              contactSearchCount.value = event.contact_search_count || 0;
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
    if (err.name === "AbortError") return; // 用户切换到后台执行，静默中止
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

onMounted(() => { loadData(); loadIcpOptions(); loadIcpStats(); fetchSearchTasks(); startPolling(); });
onUnmounted(() => { stopPolling(); });
</script>

<style scoped lang="scss">
.customer-list-page {
  // ── 数据概览条 ──
  // ── ICP 画像维度统计条 ──
  .icp-stats-bar {
    display: flex; gap: 12px; margin-bottom: 16px; overflow-x: auto; padding-bottom: 4px;
    &::-webkit-scrollbar { height: 4px; }
    &::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 2px; }

    .icp-stat-card {
      display: flex; flex-direction: column; gap: 6px;
      background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
      padding: 12px 16px; min-width: 140px; flex-shrink: 0;
      cursor: pointer; user-select: none;
      transition: all 0.2s;
      &:hover { border-color: #3b82f6; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1); }
      &.active { border-color: #3b82f6; background: #eff6ff; box-shadow: 0 0 0 1px #3b82f6; }
      &__header {
        display: flex; align-items: center; gap: 6px;
        color: #64748b; font-size: 12px;
      }
      &__dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
      &__name {
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 120px;
      }
      &__total { font-size: 24px; font-weight: 800; color: #1e293b; line-height: 1; }
      &__statuses {
        display: flex; gap: 6px; flex-wrap: wrap;
        .status-dot {
          font-size: 11px; font-weight: 600; padding: 1px 6px; border-radius: 8px;
          &.status-new { background: #eff6ff; color: #3b82f6; }
          &.status-contacted { background: #fef3c7; color: #d97706; }
          &.status-qualified { background: #ecfdf5; color: #059669; }
          &.status-negotiating { background: #eef2ff; color: #4f46e5; }
          &.status-closed { background: #e0f2fe; color: #0284c7; }
        }
      }
    }
  }
  // ── 后台任务进度面板 ──
  .search-tasks-panel {
    margin-bottom: 16px;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
    .search-tasks-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 10px 16px; cursor: pointer; user-select: none;
      background: #f8fafc; transition: background 0.15s;
      &:hover { background: #f1f5f9; }
      .search-tasks-title {
        display: flex; align-items: center; gap: 8px;
        font-size: 13px; font-weight: 600; color: #334155;
        .el-tag { font-size: 11px; }
      }
      .rotated { transform: rotate(180deg); }
      .el-icon { transition: transform 0.2s; color: #94a3b8; }
    }
    .search-tasks-body {
      padding: 8px 16px 12px;
    }
    .search-task-item {
      display: flex; align-items: center; gap: 8px;
      padding: 8px 0; border-bottom: 1px solid #f1f5f9;
      cursor: pointer; border-radius: 6px; transition: background 0.15s;
      &:hover { background: #f8fafc; }
      &:last-child { border-bottom: none; }
      .task-item-header {
        display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0;
        font-size: 13px;
        .task-icon {
          flex-shrink: 0;
          &.is-loading { color: #f59e0b; animation: rotating 2s linear infinite; }
          &.task-done { color: #22c55e; }
          &.task-error { color: #ef4444; }
        }
        .task-icp-name { font-weight: 600; color: #1e293b; white-space: nowrap; }
        .task-channels { font-size: 11px; color: #94a3b8; }
        .task-result-text { color: #475569; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .task-error-text { color: #ef4444; font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .task-time { font-size: 11px; color: #94a3b8; white-space: nowrap; margin-left: auto; }
      }
      .task-item-progress {
        display: none; // progress details shown in header for compactness
      }
      .task-progress-bar {
        width: 100px; height: 4px; background: #e2e8f0; border-radius: 2px; flex-shrink: 0; margin-left: auto;
        .task-progress-fill {
          height: 100%; background: linear-gradient(90deg, #3b82f6, #6366f1);
          border-radius: 2px; transition: width 0.5s ease;
        }
      }
      .task-dismiss-btn {
        flex-shrink: 0; padding: 2px 6px; font-size: 11px; color: #94a3b8;
        &:hover { color: #64748b; }
      }
      &.task-running, &.task-pending {
        background: #fffbeb; margin: 0 -16px; padding: 8px 16px;
      }
    }
  }
  @keyframes rotating { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

  // ── 任务详情弹窗 ──
  .task-detail {
    .task-detail-row {
      display: flex; align-items: center; gap: 12px; padding: 8px 0;
      .task-detail-label { font-size: 13px; color: #64748b; min-width: 80px; }
      .task-detail-value { font-size: 14px; color: #1e293b; font-weight: 500; }
    }
    .task-detail-section-title {
      font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 12px;
    }
    .task-detail-stats {
      display: flex; gap: 16px;
      .task-detail-stat {
        flex: 1; text-align: center; padding: 12px 8px;
        background: #f8fafc; border-radius: 8px;
        .stat-num { font-size: 24px; font-weight: 800; color: #1e293b; display: block; }
        .stat-label { font-size: 12px; color: #64748b; }
      }
    }
    .task-detail-breakdown {
      .breakdown-item {
        display: flex; align-items: center; gap: 8px; padding: 6px 0;
        font-size: 13px; color: #475569;
        .breakdown-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
        .breakdown-count { margin-left: auto; font-weight: 600; color: #1e293b; }
      }
    }
    .task-detail-progress {
      p { font-size: 13px; color: #475569; margin: 0 0 12px; }
    }
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
    &.status-new :deep(.el-input__wrapper) { background: #eff6ff; color: #3b82f6; .el-input__inner { color: #3b82f6; } }
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
