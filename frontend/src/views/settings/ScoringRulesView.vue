<template>
  <div class="scoring-rules-view">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient-orb bg-orb-1"></div>
      <div class="bg-gradient-orb bg-orb-2"></div>
      <div class="bg-grid"></div>
    </div>

    <div class="content-wrapper">
      <!-- 页面标题 -->
      <PageHeader
        title="评分规则配置"
        subtitle="为不同角色类型定制评分维度和权重"
        icon="pi pi-sliders-h"
        icon-gradient="bg-gradient-to-br from-primary via-ai to-secondary"
      />

      <!-- 角色类型选择卡片 -->
      <div class="role-cards-grid">
        <div
          v-for="role in roleTypes"
          :key="role.type"
          class="role-card"
          :class="{ 'role-card--active': activeRole === role.type }"
          @click="switchRole(role.type)"
        >
          <div class="role-card__glow" :class="`role-card__glow--${role.type}`"></div>
          <div class="role-card__content">
            <div class="role-card__icon" :class="`role-icon--${role.type}`">
              <i :class="role.icon"></i>
            </div>
            <div class="role-card__info">
              <h3 class="role-card__title">{{ role.label }}</h3>
              <p class="role-card__desc">{{ role.description }}</p>
            </div>
            <div class="role-card__meta">
              <span class="role-card__count">
                {{ currentRules[role.type]?.length || 0 }} 维度
              </span>
              <Tag
                v-if="hasUnsavedChanges(role.type)"
                value="待保存"
                class="role-card__tag"
              />
            </div>
          </div>
          <div class="role-card__progress" :class="`role-card__progress--${role.type}`">
            <div
              class="role-card__progress-bar"
              :style="{ width: `${getWeightProgress(role.type)}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- 规则配置区域 -->
      <div class="rules-panel">
        <div class="rules-panel__header">
          <div class="rules-panel__title-group">
            <div class="rules-panel__icon" :class="`role-icon--${activeRole}`">
              <i :class="activeRoleIcon"></i>
            </div>
            <div class="rules-panel__title-text">
              <h3 class="rules-panel__title">{{ activeRoleLabel }}评分规则</h3>
              <div class="rules-panel__weight-info">
                <span class="weight-label">权重总和</span>
                <div class="weight-display" :class="weightStatusClass">
                  <span class="weight-value">{{ totalWeight.toFixed(2) }}</span>
                  <span class="weight-target">/ 1.00</span>
                </div>
                <span
                  v-if="Math.abs(totalWeight - 1.0) > 0.01"
                  class="weight-warning"
                >
                  <i class="pi pi-exclamation-circle"></i>
                  建议调整为 1.0
                </span>
              </div>
            </div>
          </div>
          <div class="rules-panel__actions">
            <Button
              label="重置默认"
              icon="pi pi-refresh"
              severity="secondary"
              outlined
              class="btn-action btn-action--reset"
              :loading="resetting"
              @click="confirmReset"
            />
            <Button
              label="保存更改"
              icon="pi pi-save"
              severity="primary"
              class="btn-action btn-action--save"
              :loading="saving"
              :disabled="!hasUnsavedChanges(activeRole)"
              @click="saveChanges"
            />
          </div>
        </div>

        <!-- 权重可视化条 -->
        <div class="weight-visual-bar">
          <div
            class="weight-visual-bar__fill"
            :class="weightStatusClass"
            :style="{ width: `${Math.min(totalWeight * 100, 100)}%` }"
          ></div>
          <div class="weight-visual-bar__mark" style="left: 100%"></div>
        </div>

        <!-- 规则表格 -->
        <div class="rules-table-wrapper">
          <DataTable
            :value="editableRules"
            class="rules-table"
            :loading="loading"
            striped-rows
            row-hover
          >
            <template #empty>
              <div class="rules-empty">
                <i class="pi pi-inbox"></i>
                <p>暂无评分规则，请添加新规则</p>
              </div>
            </template>

            <Column
              field="sort_order"
              header="排序"
              style="width: 80px"
              class="col-sort"
            >
              <template #body="{ index }">
                <div class="sort-controls">
                  <Button
                    icon="pi pi-chevron-up"
                    text
                    rounded
                    size="small"
                    class="sort-btn"
                    :disabled="index === 0"
                    @click="moveUp(index)"
                  />
                  <span class="sort-index">{{ index + 1 }}</span>
                  <Button
                    icon="pi pi-chevron-down"
                    text
                    rounded
                    size="small"
                    class="sort-btn"
                    :disabled="index === editableRules.length - 1"
                    @click="moveDown(index)"
                  />
                </div>
              </template>
            </Column>

            <Column
              field="dimension"
              header="评分维度"
              style="width: 150px"
              class="col-dimension"
            >
              <template #body="{ data }">
                <div class="dimension-cell">
                  <div class="dimension-icon" :style="{ background: getDimensionColor(data.dimension) }">
                    <i :class="getDimensionIcon(data.dimension)"></i>
                  </div>
                  <span class="dimension-label">{{ getDimensionLabel(data.dimension) }}</span>
                </div>
              </template>
            </Column>

            <Column
              field="weight"
              header="权重分配"
              style="width: 280px"
              class="col-weight"
            >
              <template #body="{ index }">
                <div class="weight-cell">
                  <Slider
                    v-model="editableRules[index].weight"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    class="weight-slider"
                    :disabled="!canWrite"
                    @change="markChanged"
                  />
                  <div class="weight-input-wrapper">
                    <InputNumber
                      v-model="editableRules[index].weight"
                      :min="0"
                      :max="10"
                      :step="0.01"
                      :max-fraction-digits="2"
                      size="small"
                      class="weight-input"
                      :disabled="!canWrite"
                      @update:model-value="markChanged"
                    />
                    <span class="weight-unit">%</span>
                  </div>
                  <div
                    class="weight-bar-mini"
                    :style="{ width: `${editableRules[index].weight * 100}%` }"
                  ></div>
                </div>
              </template>
            </Column>

            <Column
              field="description"
              header="规则描述"
              class="col-description"
            >
              <template #body="{ index }">
                <InputText
                  v-model="editableRules[index].description"
                  size="small"
                  class="description-input"
                  placeholder="输入规则描述..."
                  :disabled="!canWrite"
                  @update:model-value="markChanged"
                />
              </template>
            </Column>

            <Column
              field="is_active"
              header="状态"
              style="width: 100px"
              class="col-status"
            >
              <template #body="{ index }">
                <div class="status-cell">
                  <ToggleSwitch
                    v-model="editableRules[index].is_active"
                    class="status-switch"
                    :disabled="!canWrite"
                    @update:model-value="markChanged"
                  />
                  <span
                    class="status-label"
                    :class="editableRules[index].is_active ? 'status-label--active' : 'status-label--inactive'"
                  >
                    {{ editableRules[index].is_active ? '启用' : '禁用' }}
                  </span>
                </div>
              </template>
            </Column>

            <Column
              header="操作"
              style="width: 80px"
              class="col-actions"
            >
              <template #body="{ index }">
                <Button
                  v-if="canWrite"
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  rounded
                  size="small"
                  class="delete-btn"
                  @click="removeRule(index)"
                />
              </template>
            </Column>
          </DataTable>
        </div>

        <!-- 添加规则区域（仅管理员可见） -->
        <div v-if="canWrite" class="add-rule-section">
          <div class="add-rule-card">
            <div class="add-rule-header">
              <i class="pi pi-plus-circle"></i>
              <span>添加新评分规则</span>
            </div>
            <div class="add-rule-form">
              <Dropdown
                v-model="newRuleDimension"
                :options="availableDimensions"
                option-label="label"
                option-value="key"
                placeholder="选择维度"
                class="add-dropdown"
              >
                <template #value="{ value }">
                  <div v-if="value" class="dimension-option-selected">
                    <div
                      class="dimension-icon dimension-icon--small"
                      :style="{ background: getDimensionColor(value) }"
                    >
                      <i :class="getDimensionIcon(value)"></i>
                    </div>
                    <span>{{ getDimensionLabel(value) }}</span>
                  </div>
                  <span v-else class="dimension-placeholder">选择维度</span>
                </template>
                <template #option="{ option }">
                  <div class="dimension-option">
                    <div
                      class="dimension-icon dimension-icon--small"
                      :style="{ background: getDimensionColor(option.key) }"
                    >
                      <i :class="getDimensionIcon(option.key)"></i>
                    </div>
                    <span>{{ option.label }}</span>
                  </div>
                </template>
              </Dropdown>
              <div class="weight-input-group">
                <label>权重</label>
                <InputNumber
                  v-model="newRuleWeight"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  size="small"
                  class="weight-input-new"
                />
                <span class="weight-unit">%</span>
              </div>
              <InputText
                v-model="newRuleDesc"
                placeholder="规则描述（可选）"
                class="desc-input"
              />
              <Button
                label="添加"
                icon="pi pi-plus"
                severity="success"
                class="add-btn"
                :disabled="!newRuleDimension"
                @click="addRule"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 评分等级说明卡片 -->
      <div class="grade-cards-section">
        <h4 class="section-title">
          <i class="pi pi-info-circle"></i>
          评分等级说明
        </h4>
        <div class="grade-cards-grid">
          <div class="grade-card grade-card--s">
            <div class="grade-card__score">S</div>
            <div class="grade-card__info">
              <span class="grade-card__range">≥90分</span>
              <span class="grade-card__desc">表现卓越，远超平均水平</span>
            </div>
            <div class="grade-card__glow"></div>
          </div>
          <div class="grade-card grade-card--a">
            <div class="grade-card__score">A</div>
            <div class="grade-card__info">
              <span class="grade-card__range">≥80分</span>
              <span class="grade-card__desc">表现优秀，高于平均水平</span>
            </div>
            <div class="grade-card__glow"></div>
          </div>
          <div class="grade-card grade-card--b">
            <div class="grade-card__score">B</div>
            <div class="grade-card__info">
              <span class="grade-card__range">≥70分</span>
              <span class="grade-card__desc">表现良好，达到平均水平</span>
            </div>
            <div class="grade-card__glow"></div>
          </div>
          <div class="grade-card grade-card--c">
            <div class="grade-card__score">C</div>
            <div class="grade-card__info">
              <span class="grade-card__range">≥60分</span>
              <span class="grade-card__desc">表现一般，略低于平均</span>
            </div>
            <div class="grade-card__glow"></div>
          </div>
          <div class="grade-card grade-card--d">
            <div class="grade-card__score">D</div>
            <div class="grade-card__info">
              <span class="grade-card__range">≥40分</span>
              <span class="grade-card__desc">表现较差，需要改进</span>
            </div>
            <div class="grade-card__glow"></div>
          </div>
          <div class="grade-card grade-card--f">
            <div class="grade-card__score">F</div>
            <div class="grade-card__info">
              <span class="grade-card__range">&lt;40分</span>
              <span class="grade-card__desc">表现很差，急需提升</span>
            </div>
            <div class="grade-card__glow"></div>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog />
    <Toast />
  </div>
</template>

<script setup lang="ts">
/**
 * 评分规则配置页面
 * 功能：按角色类型（输出/辅助/承伤）管理评分维度和权重
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import PageHeader from '@/components/common/PageHeader.vue'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import Tag from 'primevue/tag'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import { scoringRulesService, type ScoringRule, type DimensionInfo } from '@/services/scoring/scoringRulesService'
import { usePermission } from '@/composables/system/usePermission'

const confirm = useConfirm()
const toast = useToast()
const { can } = usePermission()
const canWrite = can('write')

// ============================================
// 角色类型定义
// ============================================
const roleTypes = [
  { type: 'dps', label: '输出', description: '以伤害输出为主要职责', icon: 'pi pi-bolt' },
  { type: 'support', label: '辅助', description: '以治疗和增益为主要职责', icon: 'pi pi-heart' },
  { type: 'tank', label: '承伤', description: '以吸收伤害和控制为主要职责', icon: 'pi pi-shield' },
]

const activeRole = ref('dps')

const activeRoleLabel = computed(() => roleTypes.find(r => r.type === activeRole.value)?.label || '')
const activeRoleIcon = computed(() => roleTypes.find(r => r.type === activeRole.value)?.icon || 'pi pi-star')

// ============================================
// 数据状态
// ============================================
const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)

const currentRules = ref<Record<string, ScoringRule[]>>({})
const editableRules = ref<ScoringRule[]>([])
const changedRoles = ref<Set<string>>(new Set())
const allDimensions = ref<DimensionInfo[]>([])

// 新规则表单
const newRuleDimension = ref('')
const newRuleWeight = ref(10)
const newRuleDesc = ref('')

const totalWeight = computed(() =>
  editableRules.value.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
)

const availableDimensions = computed(() => {
  const used = new Set(editableRules.value.map(r => r.dimension))
  return allDimensions.value.filter(d => !used.has(d.key))
})

const weightStatusClass = computed(() => {
  const diff = Math.abs(totalWeight.value - 1.0)
  if (diff < 0.01) return 'weight-status--optimal'
  if (diff < 0.1) return 'weight-status--warning'
  return 'weight-status--error'
})

function hasUnsavedChanges(role: string) {
  return changedRoles.value.has(role)
}

function getWeightProgress(role: string): number {
  const rules = currentRules.value[role] || []
  const total = rules.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
  return Math.min(total * 100, 100)
}

// ============================================
// 维度信息和图标映射
// ============================================
const dimensionIcons: Record<string, string> = {
  damage: 'pi pi-bolt',
  healing: 'pi pi-heart',
  protection: 'pi pi-shield',
  crowd_control: 'pi pi-lock',
  support: 'pi pi-star',
  survival: 'pi pi-users',
  objective: 'pi pi-flag',
  downstacks: 'pi pi-arrow-down',
}

const dimensionColors: Record<string, string> = {
  damage: '#FF4D6A',
  healing: '#00D68F',
  protection: '#165DFF',
  crowd_control: '#9D4EDD',
  support: '#FFAA00',
  survival: '#00B4FF',
  objective: '#4CAF50',
  downstacks: '#FF5722',
}

function getDimensionIcon(key: string): string {
  return dimensionIcons[key] || 'pi pi-circle'
}

function getDimensionColor(key: string): string {
  return dimensionColors[key] || '#888888'
}

function getDimensionLabel(key: string) {
  return allDimensions.value.find(d => d.key === key)?.label || key
}

// ============================================
// API 调用
// ============================================
async function fetchRules() {
  loading.value = true
  try {
    const data = await scoringRulesService.getRules()
    if (data) {
      for (const key of ['dps', 'support', 'tank']) {
        if (data[key]) {
          currentRules.value[key] = data[key].rules || []
        }
      }
    }
    syncEditableRules()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分规则失败', life: 5000 })
  } finally {
    loading.value = false
  }
}

async function fetchDimensions() {
  try {
    allDimensions.value = await scoringRulesService.getDimensions()
  } catch (e) {
    console.error('获取评分维度失败', e)
  }
}

function syncEditableRules() {
  const rules = currentRules.value[activeRole.value] || []
  editableRules.value = rules.map(r => ({ ...r }))
}

// ============================================
// 交互
// ============================================
function switchRole(role: string) {
  activeRole.value = role
  syncEditableRules()
}

function markChanged() {
  changedRoles.value.add(activeRole.value)
}

function moveUp(index: number) {
  if (index === 0) return
  const temp = editableRules.value[index]
  editableRules.value[index] = editableRules.value[index - 1]
  editableRules.value[index - 1] = temp
  markChanged()
}

function moveDown(index: number) {
  if (index >= editableRules.value.length - 1) return
  const temp = editableRules.value[index]
  editableRules.value[index] = editableRules.value[index + 1]
  editableRules.value[index + 1] = temp
  markChanged()
}

function removeRule(index: number) {
  editableRules.value.splice(index, 1)
  markChanged()
}

function addRule() {
  if (!newRuleDimension.value) return
  const dim = allDimensions.value.find(d => d.key === newRuleDimension.value)
  editableRules.value.push({
    id: 0,
    role_type: activeRole.value,
    dimension: newRuleDimension.value,
    weight: newRuleWeight.value / 100,
    is_active: true,
    description: newRuleDesc.value || dim?.label || '',
    sort_order: editableRules.value.length,
  })
  newRuleDimension.value = ''
  newRuleWeight.value = 10
  newRuleDesc.value = ''
  markChanged()
}

async function saveChanges() {
  saving.value = true
  try {
    const rulesToSave = editableRules.value.map((r, idx) => ({
      role_type: activeRole.value,
      dimension: r.dimension,
      weight: r.weight,
      is_active: r.is_active,
      description: r.description,
      sort_order: idx,
      min_value: r.min_value,
      max_value: r.max_value,
    }))

    await scoringRulesService.batchUpdate(activeRole.value, rulesToSave)
    changedRoles.value.delete(activeRole.value)

    const refreshed = await scoringRulesService.getRules(activeRole.value)
    if (refreshed && refreshed.rules) {
      currentRules.value[activeRole.value] = refreshed.rules
      syncEditableRules()
    }

    toast.add({ severity: 'success', summary: '保存成功', detail: `${activeRoleLabel.value}评分规则已更新`, life: 3000 })
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '保存失败', detail: e?.message || '更新评分规则失败', life: 5000 })
  } finally {
    saving.value = false
  }
}

function confirmReset() {
  confirm.require({
    message: `确定要将 ${activeRoleLabel.value} 的评分规则重置为系统默认吗？此操作不可撤销。`,
    header: '确认重置',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      resetting.value = true
      try {
        await scoringRulesService.resetDefault(activeRole.value)
        changedRoles.value.delete(activeRole.value)
        await fetchRules()
        toast.add({ severity: 'success', summary: '重置成功', detail: `${activeRoleLabel.value}评分规则已重置为默认`, life: 3000 })
      } catch (e: any) {
        toast.add({ severity: 'error', summary: '重置失败', detail: e?.message || '操作失败', life: 5000 })
      } finally {
        resetting.value = false
      }
    },
  })
}

// ============================================
// 生命周期
// ============================================
onMounted(() => {
  fetchRules()
  fetchDimensions()
})

watch(activeRole, () => {
  syncEditableRules()
})
</script>

<style scoped>
/* ============================================
   主容器
   ============================================ */
.scoring-rules-view {
  position: relative;
  min-height: 100vh;
  padding: var(--space-6);
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.bg-orb-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-ai));
  top: -200px;
  right: -100px;
  animation: float-orb 20s ease-in-out infinite;
}

.bg-orb-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, var(--color-secondary), var(--color-error));
  bottom: -100px;
  left: -100px;
  animation: float-orb 25s ease-in-out infinite reverse;
}

.bg-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(22, 93, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(22, 93, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

@keyframes float-orb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -30px) scale(1.1); }
}

/* 内容包装器 */
.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* ============================================
   角色卡片网格
   ============================================ */
.role-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-5);
}

.role-card {
  position: relative;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  cursor: pointer;
  transition: all var(--transition-normal);
  overflow: hidden;
}

.role-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--card-accent-color);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.role-card:hover {
  transform: translateY(-4px);
  border-color: var(--card-accent-color);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.4);
}

.role-card--active {
  border-color: var(--card-accent-color);
  box-shadow: 0 0 0 1px var(--card-accent-color), 0 20px 40px -12px rgba(0, 0, 0, 0.4);
}

.role-card--active::before {
  opacity: 1;
}

.role-card__glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, var(--card-accent-color) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-slow);
  pointer-events: none;
}

.role-card--active .role-card__glow {
  opacity: 0.05;
}

.role-card__glow--dps { --card-accent-color: #FF4D6A; }
.role-card__glow--support { --card-accent-color: #00D68F; }
.role-card__glow--tank { --card-accent-color: #9D4EDD; }

.role-card__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.role-card__icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  background: linear-gradient(135deg, var(--icon-color-1), var(--icon-color-2));
  box-shadow: 0 8px 24px -8px var(--icon-color-1);
}

.role-icon--dps {
  --icon-color-1: #FF4D6A;
  --icon-color-2: #FF8A65;
}

.role-icon--support {
  --icon-color-1: #00D68F;
  --icon-color-2: #00B4FF;
}

.role-icon--tank {
  --icon-color-1: #9D4EDD;
  --icon-color-2: #165DFF;
}

.role-card__info {
  flex: 1;
}

.role-card__title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-1);
}

.role-card__desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.role-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-2);
}

.role-card__count {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  padding: var(--space-1) var(--space-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
}

.role-card__tag {
  font-size: var(--font-size-xs);
  padding: var(--space-0-5) var(--space-2);
}

.role-card__progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--color-bg-secondary);
}

.role-card__progress-bar {
  height: 100%;
  background: var(--card-accent-color);
  transition: width var(--transition-normal);
}

.role-card__progress--dps { --card-accent-color: #FF4D6A; }
.role-card__progress--support { --card-accent-color: #00D68F; }
.role-card__progress--tank { --card-accent-color: #9D4EDD; }

/* ============================================
   规则配置面板
   ============================================ */
.rules-panel {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-6);
  box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.2);
}

.rules-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}

.rules-panel__title-group {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.rules-panel__icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
  background: linear-gradient(135deg, var(--icon-color-1), var(--icon-color-2));
  box-shadow: 0 8px 24px -8px var(--icon-color-1);
}

.rules-panel__title-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.rules-panel__title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.rules-panel__weight-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.weight-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.weight-display {
  display: flex;
  align-items: baseline;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--color-bg-secondary);
  transition: all var(--transition-normal);
}

.weight-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text);
}

.weight-target {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.weight-status--optimal .weight-display {
  background: rgba(0, 214, 143, 0.15);
}

.weight-status--optimal .weight-value {
  color: var(--color-success);
}

.weight-status--warning .weight-display {
  background: rgba(255, 170, 0, 0.15);
}

.weight-status--warning .weight-value {
  color: var(--color-warning);
}

.weight-status--error .weight-display {
  background: rgba(255, 77, 106, 0.15);
}

.weight-status--error .weight-value {
  color: var(--color-error);
}

.weight-warning {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-warning);
  animation: pulse-warning 2s ease-in-out infinite;
}

@keyframes pulse-warning {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.rules-panel__actions {
  display: flex;
  gap: var(--space-3);
}

.btn-action {
  font-weight: 500;
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);
}

.btn-action--reset {
  background: transparent;
  border: 1px solid var(--color-border);
}

.btn-action--reset:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-text-tertiary);
}

.btn-action--save {
  background: linear-gradient(135deg, var(--color-primary), #4080FF);
  border: none;
  box-shadow: 0 4px 12px -2px rgba(22, 93, 255, 0.4);
}

.btn-action--save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -4px rgba(22, 93, 255, 0.5);
}

.btn-action--save:disabled {
  opacity: 0.5;
  background: var(--color-bg-secondary);
  box-shadow: none;
}

/* 权重可视化条 */
.weight-visual-bar {
  position: relative;
  height: 8px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
  margin-bottom: var(--space-5);
  overflow: hidden;
}

.weight-visual-bar__fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-normal), background var(--transition-normal);
  background: linear-gradient(90deg, var(--color-primary), var(--color-ai));
}

.weight-status--optimal .weight-visual-bar__fill {
  background: linear-gradient(90deg, var(--color-success), #33E0A5);
}

.weight-status--warning .weight-visual-bar__fill {
  background: linear-gradient(90deg, var(--color-warning), #FFB347);
}

.weight-status--error .weight-visual-bar__fill {
  background: linear-gradient(90deg, var(--color-error), #FF8A80);
}

/* 规则表格 */
.rules-table-wrapper {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.rules-table {
  background: var(--color-bg-secondary);
}

.rules-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--color-text-tertiary);
}

.rules-empty i {
  font-size: 3rem;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

/* 列样式 */
.col-sort {
  background: var(--color-card);
}

.col-dimension {
  background: var(--color-card);
}

.col-weight {
  background: var(--color-card);
}

.col-description {
  background: var(--color-card);
}

.col-status {
  background: var(--color-card);
}

.col-actions {
  background: var(--color-card);
}

/* 排序控制 */
.sort-controls {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.sort-btn {
  width: 28px;
  height: 28px;
  color: var(--color-text-secondary);
}

.sort-btn:hover:not(:disabled) {
  color: var(--color-primary);
  background: var(--color-primary-alpha-10);
}

.sort-index {
  width: 24px;
  text-align: center;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text);
}

/* 维度单元格 */
.dimension-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dimension-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.dimension-icon--small {
  width: 24px;
  height: 24px;
  font-size: 0.75rem;
}

.dimension-label {
  font-weight: 500;
  color: var(--color-text);
}

/* 权重单元格 */
.weight-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
}

.weight-slider {
  flex: 1;
}

:deep(.p-slider) {
  background: var(--color-bg-secondary);
  height: 6px;
  border-radius: var(--radius-full);
}

:deep(.p-slider .p-slider-range) {
  background: linear-gradient(90deg, var(--color-primary), var(--color-ai));
  border-radius: var(--radius-full);
}

:deep(.p-slider .p-slider-handle) {
  width: 18px;
  height: 18px;
  background: white;
  border: 3px solid var(--color-primary);
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.4);
  transition: all var(--transition-fast);
}

:deep(.p-slider .p-slider-handle:hover) {
  transform: scale(1.2);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.5);
}

.weight-input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: var(--color-bg-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.weight-input {
  width: 60px;
}

:deep(.weight-input .p-inputnumber-input) {
  text-align: center;
  font-weight: 600;
  background: transparent;
  border: none;
  color: var(--color-text);
}

.weight-unit {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.weight-bar-mini {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: var(--color-primary);
  opacity: 0.3;
  transition: width var(--transition-fast);
}

/* 描述输入框 */
.description-input {
  width: 100%;
  background: var(--color-bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--color-text);
  transition: all var(--transition-fast);
}

.description-input:hover {
  border-color: var(--color-border);
}

.description-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-alpha-10);
}

/* 状态单元格 */
.status-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-switch {
  transform: scale(0.9);
}

:deep(.p-toggleswitch.p-toggleswitch-checked .p-toggleswitch-slider) {
  background: linear-gradient(90deg, var(--color-success), #33E0A5);
}

.status-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.status-label--active {
  color: var(--color-success);
}

.status-label--inactive {
  color: var(--color-text-tertiary);
}

/* 删除按钮 */
.delete-btn {
  width: 36px;
  height: 36px;
  color: var(--color-text-tertiary);
  transition: all var(--transition-fast);
}

.delete-btn:hover {
  color: var(--color-error);
  background: var(--color-error-alpha-10);
}

/* ============================================
   添加规则区域
   ============================================ */
.add-rule-section {
  margin-top: var(--space-5);
}

.add-rule-card {
  background: var(--color-bg-secondary);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  transition: all var(--transition-normal);
}

.add-rule-card:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-alpha-5);
}

.add-rule-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  font-weight: 600;
  color: var(--color-text-secondary);
}

.add-rule-header i {
  color: var(--color-primary);
}

.add-rule-form {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.add-dropdown {
  width: 200px;
}

:deep(.add-dropdown .p-dropdown) {
  background: var(--color-card);
  border-color: var(--color-border);
}

.dimension-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.dimension-option-selected {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.dimension-placeholder {
  color: var(--color-text-tertiary);
}

.weight-input-group {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.weight-input-group label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.weight-input-new {
  width: 100px;
}

.desc-input {
  flex: 1;
  min-width: 200px;
  background: var(--color-card);
  border-color: var(--color-border);
}

.add-btn {
  background: linear-gradient(135deg, var(--color-success), #00B894);
  border: none;
  font-weight: 500;
  box-shadow: 0 4px 12px -2px rgba(0, 214, 143, 0.4);
}

.add-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -4px rgba(0, 214, 143, 0.5);
}

.add-btn:disabled {
  opacity: 0.5;
  background: var(--color-bg-secondary);
  box-shadow: none;
}

/* ============================================
   评分等级说明
   ============================================ */
.grade-cards-section {
  margin-top: var(--space-4);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 var(--space-4);
}

.section-title i {
  color: var(--color-primary);
}

.grade-cards-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-4);
}

.grade-card {
  position: relative;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  text-align: center;
  overflow: hidden;
  transition: all var(--transition-normal);
}

.grade-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.3);
}

.grade-card__score {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--grade-color-1), var(--grade-color-2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: var(--space-2);
}

.grade-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.grade-card__range {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text);
}

.grade-card__desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.grade-card__glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, var(--grade-color-1) 0%, transparent 70%);
  opacity: 0.08;
  pointer-events: none;
}

/* 等级颜色 */
.grade-card--s {
  --grade-color-1: #FFD700;
  --grade-color-2: #FFA500;
  border-color: rgba(255, 215, 0, 0.3);
}

.grade-card--a {
  --grade-color-1: #00D68F;
  --grade-color-2: #00B4FF;
  border-color: rgba(0, 214, 143, 0.3);
}

.grade-card--b {
  --grade-color-1: #165DFF;
  --grade-color-2: #8B5CF6;
  border-color: rgba(22, 93, 255, 0.3);
}

.grade-card--c {
  --grade-color-1: #FFAA00;
  --grade-color-2: #FFB347;
  border-color: rgba(255, 170, 0, 0.3);
}

.grade-card--d {
  --grade-color-1: #FF8A65;
  --grade-color-2: #FF5722;
  border-color: rgba(255, 138, 101, 0.3);
}

.grade-card--f {
  --grade-color-1: #FF4D6A;
  --grade-color-2: #D93664;
  border-color: rgba(255, 77, 106, 0.3);
}

/* ============================================
   响应式设计
   ============================================ */
@media (max-width: 1200px) {
  .grade-cards-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .scoring-rules-view {
    padding: var(--space-4);
  }

  .role-cards-grid {
    grid-template-columns: 1fr;
  }

  .rules-panel__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-4);
  }

  .rules-panel__actions {
    width: 100%;
  }

  .rules-panel__actions .btn-action {
    flex: 1;
  }

  .add-rule-form {
    flex-direction: column;
    align-items: stretch;
  }

  .add-dropdown,
  .weight-input-group,
  .desc-input,
  .add-btn {
    width: 100%;
  }

  .grade-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>