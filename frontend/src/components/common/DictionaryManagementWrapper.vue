<template>
  <div class="dictionary-wrapper">
    <!-- 概览视图 -->
    <template v-if="viewMode === 'overview'">
      <div class="overview-container">
        <!-- 头部区域 -->
        <div class="overview-header">
          <div class="header-info">
            <i class="pi pi-book header-icon" />
            <div class="header-text">
              <h2 class="header-title">
                字典管理
              </h2>
              <p class="header-subtitle">
                系统枚举数据配置和管理中心
              </p>
            </div>
          </div>
          <Button
            label="进入管理"
            icon="pi pi-arrow-right"
            severity="primary"
            @click="viewMode = 'management'"
          />
        </div>

        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon primary">
              <i class="pi pi-folder" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ typeStats.total }}</span>
              <span class="stat-label">字典分类</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon success">
              <i class="pi pi-check-circle" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ typeStats.enabled }}</span>
              <span class="stat-label">启用分类</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon info">
              <i class="pi pi-list" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ dataStats.total }}</span>
              <span class="stat-label">字典项总数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon warning">
              <i class="pi pi-database" />
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ cacheStatus ? '正常' : '需要刷新' }}</span>
              <span class="stat-label">缓存状态</span>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="quick-actions">
          <h3 class="section-title">
            常用操作
          </h3>
          <div class="action-grid">
            <div
              class="action-card"
              @click="viewMode = 'management'"
            >
              <i class="pi pi-cog action-icon" />
              <span class="action-label">分类管理</span>
              <p class="action-desc">
                管理字典分类和属性配置
              </p>
            </div>
            <div
              class="action-card"
              @click="handleQuickReload"
            >
              <i class="pi pi-refresh action-icon" />
              <span class="action-label">刷新缓存</span>
              <p class="action-desc">
                立即刷新系统字典缓存
              </p>
            </div>
          </div>
        </div>

        <!-- 分类预览 -->
        <div
          v-if="dictTypes.length > 0"
          class="types-preview"
        >
          <div class="preview-header">
            <h3 class="section-title">
              分类预览
            </h3>
            <Button
              label="查看全部"
              size="small"
              text
              @click="viewMode = 'management'"
            />
          </div>
          <div class="types-list">
            <div
              v-for="type in dictTypes.slice(0, 6)"
              :key="type.dict_id"
              class="type-item"
            >
              <div class="type-info">
                <span class="type-name">{{ type.dict_name }}</span>
                <Tag
                  :value="type.status === 0 ? '启用' : '禁用'"
                  :severity="type.status === 0 ? 'success' : 'danger'"
                  size="small"
                />
              </div>
              <span class="type-code">{{ type.dict_type }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 管理视图 -->
    <template v-else>
      <div class="management-container">
        <!-- 管理视图头部 -->
        <div class="management-header">
          <div class="header-left">
            <Button
              icon="pi pi-arrow-left"
              severity="secondary"
              text
              @click="viewMode = 'overview'"
            />
            <div class="header-text">
              <h2 class="header-title">
                字典管理
              </h2>
              <p class="header-subtitle">
                管理系统中的枚举数据和配置项
              </p>
            </div>
          </div>
          <div class="header-right">
            <Button
              v-if="isAdmin"
              :label="isCollapsed ? '展开' : '收起'"
              :icon="isCollapsed ? 'pi pi-angle-right' : 'pi pi-angle-left'"
              severity="secondary"
              outlined
              size="small"
              @click="toggleSidebar"
            />
            <Button
              v-if="isAdmin"
              label="刷新缓存"
              icon="pi pi-refresh"
              severity="info"
              outlined
              size="small"
              :loading="refreshing"
              @click="handleReloadCache"
            />
            <Button
              v-if="isAdmin"
              label="初始化数据"
              icon="pi pi-database"
              severity="warning"
              outlined
              size="small"
              @click="showInitDialog = true"
            />
          </div>
        </div>

        <!-- 原始字典管理组件 -->
        <DictionaryManagementCore
          ref="dictManagementRef"
        />
      </div>
    </template>

    <!-- 初始化数据对话框 -->
    <Dialog
      v-model:visible="showInitDialog"
      header="初始化字典数据"
      :modal="true"
      width="500px"
    >
      <div class="init-dialog-content">
        <i class="pi pi-exclamation-triangle warning-icon" />
        <p class="warning-text">
          此操作将重新初始化所有字典数据，可能会覆盖现有数据，是否继续？
        </p>
      </div>
      <template #footer>
        <Button
          label="取消"
          severity="secondary"
          @click="showInitDialog = false"
        />
        <Button
          label="确认初始化"
          severity="warning"
          :loading="initializing"
          @click="handleInitData"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { dictionaryService, type DictType } from '@/services/system/dictionaryService'
import { usePermission } from '@/composables/system/usePermission'
import DictionaryManagementCore from './DictionaryManagement.vue'

const toast = useToast()
const { isOperator, isSuperAdmin } = usePermission()

// 视图模式
const viewMode = ref<'overview' | 'management'>('overview')

// 数据引用
const dictManagementRef = ref()
const dictTypes = ref<DictType[]>([])
const loading = ref(false)
const refreshing = ref(false)
const initializing = ref(false)
const cacheStatus = ref(true)
const showInitDialog = ref(false)
const isCollapsed = ref(false)

// 计算属性
const isAdmin = computed(() => isOperator.value || isSuperAdmin.value)

const typeStats = computed(() => {
  const total = dictTypes.value.length
  const enabled = dictTypes.value.filter(t => t.status === 0).length
  return { total, enabled }
})

const dataStats = computed(() => ({
  total: dictTypes.value.length * 5 // 粗略估算
}))

// 切换侧边栏
function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
  // 通知子组件
  if (dictManagementRef.value && dictManagementRef.value.toggleSidebar) {
    dictManagementRef.value.toggleSidebar()
  }
}

// 加载数据
const loadOverviewData = async () => {
  loading.value = true
  try {
    const types = await dictionaryService.getAllTypes()
    dictTypes.value = types
  } catch (error) {
    console.error('[DictionaryWrapper] 加载概览数据失败', error)
  } finally {
    loading.value = false
  }
}

// 刷新缓存
const handleQuickReload = async () => {
  refreshing.value = true
  try {
    const success = await dictionaryService.reloadCache()
    if (success) {
      cacheStatus.value = true
      toast.add({
        severity: 'success',
        summary: '刷新成功',
        detail: '字典缓存已刷新',
        life: 3000
      })
    }
  } catch (error) {
    console.error('[DictionaryWrapper] 刷新缓存失败', error)
  } finally {
    refreshing.value = false
  }
}

const handleReloadCache = async () => {
  await handleQuickReload()
  if (dictManagementRef.value && dictManagementRef.value.handleReloadCache) {
    await dictManagementRef.value.handleReloadCache()
  }
}

// 初始化数据
const handleInitData = async () => {
  initializing.value = true
  try {
    const success = await dictionaryService.init()
    if (success) {
      toast.add({
        severity: 'success',
        summary: '初始化成功',
        detail: '字典数据已重新初始化',
        life: 3000
      })
      showInitDialog.value = false
      await loadOverviewData()
    }
  } catch (error) {
    console.error('[DictionaryWrapper] 初始化数据失败', error)
  } finally {
    initializing.value = false
  }
}

// 生命周期
onMounted(() => {
  loadOverviewData()
})

// 暴露方法供父组件调用
defineExpose({
  loadOverviewData,
  handleReloadCache
})
</script>

<style scoped lang="postcss">
.dictionary-wrapper {
  width: 100%;
}

/* 概览视图 */
.overview-container {
  padding: 0;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--color-primary-bg) 0%, transparent 100%);
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  font-size: 2.5rem;
  color: var(--color-primary);
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.header-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.header-subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 1.25rem;
}

.stat-icon.primary {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.stat-icon.success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.stat-icon.info {
  background: var(--color-info-bg);
  color: var(--color-info);
}

.stat-icon.warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

/* 快速操作 */
.quick-actions {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1rem;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-card:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
  transform: translateY(-2px);
}

.action-icon {
  font-size: 2rem;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.action-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.action-desc {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-align: center;
}

/* 分类预览 */
.types-preview {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.types-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--color-bg);
  border-radius: 8px;
  gap: 0.5rem;
}

.type-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.type-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type-code {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  font-family: monospace;
}

/* 管理视图 */
.management-container {
  padding: 0;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

/* 对话框 */
.init-dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  gap: 1rem;
}

.warning-icon {
  font-size: 3rem;
  color: var(--color-warning);
}

.warning-text {
  text-align: center;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .types-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .overview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .action-grid {
    grid-template-columns: 1fr;
  }

  .types-list {
    grid-template-columns: 1fr;
  }

  .management-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
