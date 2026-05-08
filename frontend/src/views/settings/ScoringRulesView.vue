<template>
  <div class="relative min-h-screen p-6 overflow-hidden">
    <!-- 背景装饰 -->
    <div class="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      <div
        class="absolute rounded-full blur-[80px] opacity-15 animate-pulse"
        style="width: 600px; height: 600px; background: linear-gradient(135deg, var(--color-primary), var(--color-ai)); top: -200px; right: -100px;"
      />
      <div
        class="absolute rounded-full blur-[80px] opacity-15 animate-pulse"
        style="width: 400px; height: 400px; background: linear-gradient(135deg, var(--color-secondary), var(--color-error)); bottom: -100px; left: -100px; animation-delay: 1s;"
      />
      <div
        class="absolute inset-0"
        style="background-image: linear-gradient(rgba(22,93,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(22,93,255,0.03) 1px, transparent 1px); background-size: 50px 50px;"
      />
    </div>

    <div class="relative z-10 max-w-[1400px] mx-auto flex flex-col gap-6">
      <!-- 页面标题 -->
      <PageHeader
        title="评分规则配置"
        subtitle="为不同角色类型定制评分维度和权重"
        icon="pi pi-sliders-h"
        icon-gradient="bg-gradient-to-br from-primary via-ai to-secondary"
      />

      <!-- 评分自动计算说明 -->
      <Message severity="info" class="shadow-sm">
        <div class="flex items-start gap-3">
          <i class="pi pi-calculator mt-0.5 text-info-500" />
          <div class="text-sm leading-relaxed">
            <strong>评分自动计算机制：</strong>
            当日志导入完成后，系统会根据当前生效的评分规则版本，结合玩家的职业和角色定位，
            <strong>自动计算</strong>每个玩家的 AI 评分与等级。修改规则后，可通过"应用到历史数据"按钮重新计算历史日志。
          </div>
        </div>
      </Message>

      <!-- 角色类型选择卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div
          v-for="role in roleTypes"
          :key="role.type"
          class="relative rounded-xl p-5 cursor-pointer transition-all duration-300 overflow-hidden border"
          :class="activeRole === role.type
            ? 'border-primary-500 shadow-lg shadow-primary-500/20 -translate-y-1'
            : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 hover:-translate-y-1 hover:shadow-xl'"
          :style="{ '--accent': roleColors[role.type] }"
          @click="switchRole(role.type)"
        >
          <!-- 顶部高亮条 -->
          <div
            class="absolute top-0 left-0 right-0 h-[3px] transition-opacity duration-300"
            :class="activeRole === role.type ? 'opacity-100' : 'opacity-0'"
            :style="{ background: roleColors[role.type] }"
          />
          <!-- 背景光晕 -->
          <div
            class="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] rounded-full pointer-events-none transition-opacity duration-500"
            :class="activeRole === role.type ? 'opacity-[0.05]' : 'opacity-0'"
            :style="{ background: `radial-gradient(circle, ${roleColors[role.type]} 0%, transparent 70%)` }"
          />

          <div class="relative z-10 flex flex-col gap-3">
            <div class="flex items-center gap-4">
              <div
                class="w-14 h-14 rounded-lg flex items-center justify-center text-2xl text-white shrink-0 shadow-lg"
                :style="{ background: `linear-gradient(135deg, ${roleColors[role.type]}, ${roleGradients[role.type]})`, boxShadow: `0 8px 24px -8px ${roleColors[role.type]}` }"
              >
                <i :class="role.icon" />
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-xl font-semibold text-color">{{ role.label }}</h3>
                <p class="text-sm text-color-secondary">{{ role.description }}</p>
              </div>
            </div>
            <div class="flex items-center justify-between mt-1">
              <span class="text-xs text-color-secondary px-2 py-1 rounded-full bg-surface-100 dark:bg-surface-800">
                {{ currentRules[role.type]?.length || 0 }} 维度
              </span>
              <Tag
                v-if="hasUnsavedChanges(role.type)"
                value="待保存"
                severity="warning"
                class="text-xs"
              />
            </div>
          </div>

          <!-- 底部进度条 -->
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-surface-200 dark:bg-surface-700">
            <div
              class="h-full transition-all duration-300"
              :style="{ width: `${getWeightProgress(role.type)}%`, background: roleColors[role.type] }"
            />
          </div>
        </div>
      </div>

      <!-- 规则范围切换 -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4">
        <div class="flex bg-surface-100 dark:bg-surface-800 rounded-lg p-1">
          <button
            class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2"
            :class="ruleScope === 'generic'
              ? 'bg-primary-500 text-white shadow-sm'
              : 'text-color-secondary hover:text-color'"
            @click="switchScope('generic')"
          >
            <i class="pi pi-globe" />
            通用规则
          </button>
          <button
            class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2"
            :class="ruleScope === 'profession'
              ? 'bg-primary-500 text-white shadow-sm'
              : 'text-color-secondary hover:text-color'"
            @click="switchScope('profession')"
          >
            <i class="pi pi-id-card" />
            职业特定规则
          </button>
        </div>

        <!-- 级联选择器：职业 → 精英特长 -->
        <div
          v-if="ruleScope === 'profession'"
          class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto"
        >
          <Dropdown
            v-model="selectedBaseProfession"
            :options="cascadeProfessions"
            option-label="label"
            option-value="value"
            placeholder="选择职业"
            class="w-full sm:w-48"
            @change="onBaseProfessionChange"
          >
            <template #value="slotProps">
              <div
                v-if="slotProps.value"
                class="flex items-center gap-2"
              >
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ background: getProfessionColor(slotProps.value) }"
                />
                <span>{{ getProfessionLabel(slotProps.value) }}</span>
              </div>
              <span v-else class="text-color-secondary">选择职业</span>
            </template>
            <template #option="slotProps">
              <div class="flex items-center gap-2">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ background: slotProps.option.color }"
                />
                <span>{{ slotProps.option.label }}</span>
              </div>
            </template>
          </Dropdown>

          <Dropdown
            v-model="selectedProfession"
            :options="filteredEliteSpecs"
            option-label="label"
            option-value="value"
            placeholder="选择精英特长"
            class="w-full sm:w-56"
            :disabled="!selectedBaseProfession"
            @change="onProfessionChange"
          >
            <template #value="slotProps">
              <div
                v-if="slotProps.value"
                class="flex items-center gap-2"
              >
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ background: getSpecColor(slotProps.value) }"
                />
                <span>{{ getSpecLabel(slotProps.value) }}</span>
              </div>
              <span v-else class="text-color-secondary">选择精英特长</span>
            </template>
            <template #option="slotProps">
              <div class="flex items-center gap-2">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ background: slotProps.option.color }"
                />
                <span>{{ slotProps.option.label }}</span>
              </div>
            </template>
          </Dropdown>
        </div>
      </div>

      <!-- 规则配置区域 -->
      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-6 shadow-lg">
        <!-- 头部 -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-5">
          <div class="flex items-center gap-4">
            <div
              class="w-12 h-12 rounded-lg flex items-center justify-center text-xl text-white shadow-lg shrink-0"
              :style="{ background: `linear-gradient(135deg, ${roleColors[activeRole]}, ${roleGradients[activeRole]})`, boxShadow: `0 8px 24px -8px ${roleColors[activeRole]}` }"
            >
              <i :class="activeRoleIcon" />
            </div>
            <div>
              <h3 class="text-xl font-semibold text-color">
                {{ activeRoleLabel }}评分规则
                <span
                  v-if="ruleScope === 'profession' && selectedProfession"
                  class="text-sm font-normal text-color-secondary ml-2"
                >
                  — {{ selectedProfession }}
                </span>
              </h3>
              <div class="flex items-center gap-3 mt-1 flex-wrap">
                <span class="text-sm text-color-secondary">权重总和</span>
                <div
                  class="flex items-baseline gap-1 px-3 py-0.5 rounded-full text-sm font-bold transition-colors"
                  :class="weightStatusClass === 'optimal'
                    ? 'bg-green-500/10 text-green-500'
                    : weightStatusClass === 'warning'
                      ? 'bg-orange-500/10 text-orange-500'
                      : 'bg-red-500/10 text-red-500'"
                >
                  <span class="text-base">{{ totalWeight.toFixed(2) }}</span>
                  <span class="text-xs font-normal opacity-60">/ 1.00</span>
                </div>
                <span
                  v-if="weightStatusClass !== 'optimal'"
                  class="flex items-center gap-1 text-xs text-orange-500"
                >
                  <i class="pi pi-exclamation-circle" />
                  建议调整为 1.0
                </span>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <Button
              v-if="ruleScope === 'generic'"
              label="应用到历史数据"
              icon="pi pi-history"
              severity="info"
              outlined
              :loading="recalculating"
              :disabled="!canRecalculate"
              @click="confirmRecalculate"
            />
            <Button
              v-if="ruleScope === 'profession'"
              label="删除职业规则"
              icon="pi pi-trash"
              severity="danger"
              outlined
              :loading="deletingProfession"
              :disabled="!currentProfessionHasRules"
              @click="confirmDeleteProfessionRules"
            />
            <Button
              label="重置默认"
              icon="pi pi-refresh"
              severity="secondary"
              outlined
              :loading="resetting"
              @click="confirmReset"
            />
            <Button
              label="保存更改"
              icon="pi pi-save"
              severity="primary"
              :loading="saving"
              :disabled="!hasUnsavedChanges(activeRole)"
              @click="saveChanges"
            />
          </div>
        </div>

        <!-- 权重可视化条 -->
        <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full mb-5 overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-300"
            :class="weightStatusClass === 'optimal'
              ? 'bg-green-500'
              : weightStatusClass === 'warning'
                ? 'bg-orange-500'
                : 'bg-red-500'"
            :style="{ width: `${Math.min(totalWeight * 100, 100)}%` }"
          />
          <div class="absolute top-0 bottom-0 w-0.5 bg-white/50" style="left: 100%" />
        </div>

        <!-- 规则表格 -->
        <div class="rounded-lg overflow-hidden border border-surface-200 dark:border-surface-700">
          <DataTable
            :value="editableRules"
            :loading="loading"
            striped-rows
            row-hover
            class="text-sm"
          >
            <template #empty>
              <div class="flex flex-col items-center justify-center py-12 text-color-secondary">
                <i class="pi pi-inbox text-5xl mb-4 opacity-50" />
                <p>暂无评分规则，请添加新规则</p>
              </div>
            </template>

            <Column
              field="sort_order"
              header="排序"
              style="width: 80px"
            >
              <template #body="{ index }">
                <div class="flex items-center gap-1">
                  <Button
                    icon="pi pi-chevron-up"
                    text
                    rounded
                    size="small"
                    class="w-7 h-7"
                    :disabled="index === 0"
                    @click="moveUp(index)"
                  />
                  <span class="w-6 text-center text-sm font-semibold">{{ index + 1 }}</span>
                  <Button
                    icon="pi pi-chevron-down"
                    text
                    rounded
                    size="small"
                    class="w-7 h-7"
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
            >
              <template #body="{ data }">
                <div class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 rounded-md flex items-center justify-center text-white text-sm shrink-0"
                    :style="{ background: getDimensionColor(data.dimension) }"
                  >
                    <i :class="getDimensionIcon(data.dimension)" />
                  </div>
                  <span class="font-medium">{{ getDimensionLabel(data.dimension) }}</span>
                </div>
              </template>
            </Column>

            <Column
              field="weight"
              header="权重分配"
              style="min-width: 280px"
            >
              <template #body="{ index }">
                <div class="flex items-center gap-3 relative">
                  <Slider
                    v-model="editableRules[index].weight"
                    :min="0"
                    :max="1"
                    :step="0.01"
                    class="flex-1"
                    :disabled="!canWrite"
                    @change="markChanged"
                  />
                  <div class="flex items-center gap-1 bg-surface-100 dark:bg-surface-800 px-2 py-1 rounded-md border border-surface-200 dark:border-surface-700">
                    <InputNumber
                      v-model="editableRules[index].weight"
                      :min="0"
                      :max="10"
                      :step="0.01"
                      :max-fraction-digits="2"
                      size="small"
                      class="w-16"
                      :disabled="!canWrite"
                      @update:model-value="markChanged"
                    />
                    <span class="text-xs text-color-secondary">%</span>
                  </div>
                  <div
                    class="absolute bottom-0 left-0 h-0.5 bg-primary-500 opacity-30 transition-all"
                    :style="{ width: `${editableRules[index].weight * 100}%` }"
                  />
                </div>
              </template>
            </Column>

            <Column
              field="description"
              header="规则描述"
            >
              <template #body="{ index }">
                <InputText
                  v-model="editableRules[index].description"
                  size="small"
                  class="w-full"
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
            >
              <template #body="{ index }">
                <div class="flex items-center gap-2">
                  <ToggleSwitch
                    v-model="editableRules[index].is_active"
                    :disabled="!canWrite"
                    @update:model-value="markChanged"
                  />
                  <span
                    class="text-xs font-medium"
                    :class="editableRules[index].is_active ? 'text-green-500' : 'text-color-secondary'"
                  >
                    {{ editableRules[index].is_active ? '启用' : '禁用' }}
                  </span>
                </div>
              </template>
            </Column>

            <Column
              header="操作"
              style="width: 80px"
            >
              <template #body="{ index }">
                <Button
                  v-if="canWrite"
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  rounded
                  size="small"
                  class="w-9 h-9 text-color-secondary hover:text-red-500"
                  @click="removeRule(index)"
                />
              </template>
            </Column>
          </DataTable>
        </div>

        <!-- 添加规则区域（仅管理员可见） -->
        <div
          v-if="canWrite"
          class="mt-5"
        >
          <div class="bg-surface-100 dark:bg-surface-800 border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-xl p-5 transition-colors hover:border-primary-400 hover:bg-primary-500/5">
            <div class="flex items-center gap-2 mb-4 font-semibold text-color-secondary">
              <i class="pi pi-plus-circle text-primary-500" />
              <span>添加新评分规则</span>
            </div>
            <div class="flex flex-wrap items-center gap-4">
              <Dropdown
                v-model="newRuleDimension"
                :options="availableDimensions"
                option-label="label"
                option-value="key"
                placeholder="选择维度"
                class="w-52"
              >
                <template #value="{ value }">
                  <div
                    v-if="value"
                    class="flex items-center gap-2"
                  >
                    <div
                      class="w-6 h-6 rounded flex items-center justify-center text-white text-xs"
                      :style="{ background: getDimensionColor(value) }"
                    >
                      <i :class="getDimensionIcon(value)" />
                    </div>
                    <span>{{ getDimensionLabel(value) }}</span>
                  </div>
                  <span v-else class="text-color-secondary">选择维度</span>
                </template>
                <template #option="{ option }">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-6 h-6 rounded flex items-center justify-center text-white text-xs"
                      :style="{ background: getDimensionColor(option.key) }"
                    >
                      <i :class="getDimensionIcon(option.key)" />
                    </div>
                    <span>{{ option.label }}</span>
                  </div>
                </template>
              </Dropdown>
              <div class="flex items-center gap-2">
                <label class="text-sm text-color-secondary whitespace-nowrap">权重</label>
                <InputNumber
                  v-model="newRuleWeight"
                  :min="0"
                  :max="10"
                  :step="0.01"
                  size="small"
                  class="w-24"
                />
                <span class="text-xs text-color-secondary">%</span>
              </div>
              <InputText
                v-model="newRuleDesc"
                placeholder="规则描述（可选）"
                class="flex-1 min-w-[200px]"
              />
              <Button
                label="添加"
                icon="pi pi-plus"
                severity="success"
                :disabled="!newRuleDimension"
                @click="addRule"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 评分等级说明卡片 -->
      <div>
        <h4 class="flex items-center gap-2 text-lg font-semibold text-color mb-4">
          <i class="pi pi-info-circle text-primary-500" />
          评分等级说明
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div
            v-for="g in gradeList"
            :key="g.grade"
            class="relative bg-surface-0 dark:bg-surface-900 border rounded-xl p-4 text-center overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
            :style="{ borderColor: g.color + '40' }"
          >
            <div
              class="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] rounded-full pointer-events-none opacity-[0.08]"
              :style="{ background: `radial-gradient(circle, ${g.color} 0%, transparent 70%)` }"
            />
            <div
              class="text-4xl font-extrabold mb-2"
              :style="{ background: `linear-gradient(135deg, ${g.color}, ${g.color2})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }"
            >
              {{ g.grade }}
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-sm font-semibold text-color">{{ g.range }}</span>
              <span class="text-xs text-color-secondary">{{ g.desc }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 重算任务进度面板 -->
      <div
        v-if="recalcTask"
        class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5 shadow-lg"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <i
              v-if="recalcTask.status === 'processing'"
              class="pi pi-spinner pi-spin text-ai"
            />
            <i
              v-else-if="recalcTask.status === 'completed'"
              class="pi pi-check-circle text-green-500"
            />
            <i
              v-else-if="recalcTask.status === 'failed'"
              class="pi pi-times-circle text-red-500"
            />
            <i
              v-else
              class="pi pi-clock text-color-secondary"
            />
            <span class="font-medium">历史数据重算任务</span>
            <Tag
              :value="recalcTask.status"
              :severity="recalcStatusSeverity"
              class="text-xs"
            />
          </div>
          <Button
            v-if="recalcTask.status === 'completed' || recalcTask.status === 'failed'"
            icon="pi pi-times"
            text
            rounded
            size="small"
            @click="recalcTask = null"
          />
        </div>
        <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden mb-2">
          <div
            class="h-full rounded-full transition-all duration-300"
            :class="recalcTask.status === 'completed' ? 'bg-green-500' : recalcTask.status === 'failed' ? 'bg-red-500' : 'bg-primary-500'"
            :style="{ width: recalcTask.progress_percent + '%' }"
          />
        </div>
        <div class="flex justify-between text-xs text-color-secondary">
          <span>{{ recalcTask.updated_records }} / {{ recalcTask.total_records }} 条记录</span>
          <span>{{ recalcTask.progress_percent?.toFixed(1) || 0 }}%</span>
        </div>
      </div>

      <!-- 版本历史 -->
      <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5 shadow-lg">
        <h4 class="flex items-center gap-2 text-lg font-semibold text-color mb-4">
          <i class="pi pi-history text-primary-500" />
          规则版本历史
        </h4>
        <DataTable
          :value="versionHistory"
          size="small"
          striped-rows
          class="text-sm"
        >
          <Column
            field="version"
            header="版本号"
            style="width: 90px"
          >
            <template #body="{ data }">
              <span class="px-2 py-0.5 rounded-md bg-primary-500/10 text-primary-500 text-xs font-mono font-semibold">v{{ data.version }}</span>
            </template>
          </Column>
          <Column
            field="description"
            header="变更描述"
          />
          <Column
            field="status"
            header="状态"
            style="width: 100px"
          >
            <template #body="{ data }">
              <Tag
                :value="data.status"
                :severity="data.status === 'completed' ? 'success' : data.status === 'processing' ? 'warning' : data.status === 'failed' ? 'danger' : 'info'"
                class="text-xs"
              />
            </template>
          </Column>
          <Column
            header="进度"
            style="width: 140px"
          >
            <template #body="{ data }">
              <div
                v-if="data.total_records > 0"
                class="flex items-center gap-2"
              >
                <div class="flex-1 h-1.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-primary-500 rounded-full transition-all"
                    :style="{ width: (data.total_records ? (data.updated_records / data.total_records * 100) : 0) + '%' }"
                  />
                </div>
                <span class="text-xs text-color-secondary whitespace-nowrap">{{ data.updated_records }}/{{ data.total_records }}</span>
              </div>
              <span
                v-else
                class="text-color-secondary text-xs"
              >-</span>
            </template>
          </Column>
          <Column
            field="created_at"
            header="创建时间"
            style="width: 160px"
          >
            <template #body="{ data }">
              {{ formatDate(data.created_at) }}
            </template>
          </Column>
        </DataTable>
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

import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
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
import Message from 'primevue/message'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import { scoringRulesService, type ScoringRule, type DimensionInfo } from '@/services/scoring/scoringRulesService'
import { dictionaryService, type ProfessionCascade } from '@/services/system/dictionaryService'
import { usePermission } from '@/composables/system/usePermission'

const confirm = useConfirm()
const toast = useToast()
const { can } = usePermission()
const canWrite = can('write')

// ============================================
// 角色图标映射（UI 层，与字典表解耦）
// ============================================
const roleIconMap: Record<string, string> = {
  dps: 'pi pi-bolt',
  support: 'pi pi-heart',
  tank: 'pi pi-shield',
  condition: 'pi pi-fire',
  healing: 'pi pi-heart-fill',
  control: 'pi pi-lock',
  utility: 'pi pi-wrench',
}

// 预定义渐变色映射（新角色未定义时回退到主色）
const roleGradientMap: Record<string, string> = {
  dps: '#FF8A65',
  support: '#00B4FF',
  tank: '#165DFF',
  condition: '#FF6B35',
  healing: '#00E5A0',
  control: '#6366F1',
  utility: '#0EA5E9',
}

// ============================================
// 角色类型定义（从字典表动态获取）
// ============================================
const roleTypes = ref<{ type: string; label: string; description: string; icon: string; color: string }[]>([])

const roleColors = computed(() => {
  const map: Record<string, string> = {}
  for (const r of roleTypes.value) {
    map[r.type] = r.color || '#6b7280'
  }
  return map
})

const roleGradients = computed(() => {
  const map: Record<string, string> = {}
  for (const r of roleTypes.value) {
    map[r.type] = roleGradientMap[r.type] || r.color || '#6b7280'
  }
  return map
})

const activeRole = ref('')

const activeRoleLabel = computed(() => roleTypes.value.find(r => r.type === activeRole.value)?.label || '')
const activeRoleIcon = computed(() => roleTypes.value.find(r => r.type === activeRole.value)?.icon || 'pi pi-star')

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

// ============================================
// v3.0 新增：规则范围 + 职业特定规则
// ============================================
const ruleScope = ref<'generic' | 'profession'>('generic')
const selectedProfession = ref('')
const professionOptions = ref<{ label: string; value: string }[]>([])
const professionRulesMap = ref<Record<string, ScoringRule[]>>({})
const deletingProfession = ref(false)

// v3.1 新增：职业级联数据
const cascadeProfessions = ref<ProfessionCascade[]>([])
const selectedBaseProfession = ref('')

// v3.0 新增：重算任务
const recalculating = ref(false)
const recalcTask = ref<any>(null)
let recalcPollTimer: ReturnType<typeof setInterval> | null = null

// v3.0 新增：版本历史
const versionHistory = ref<any[]>([])

const canRecalculate = computed(() => {
  return ruleScope.value === 'generic' && !recalculating.value && !hasUnsavedChanges(activeRole.value)
})

const currentProfessionHasRules = computed(() => {
  return selectedProfession.value && (professionRulesMap.value[selectedProfession.value]?.length || 0) > 0
})

const recalcStatusSeverity = computed(() => {
  const s = recalcTask.value?.status
  if (s === 'completed') return 'success'
  if (s === 'processing') return 'warning'
  if (s === 'failed') return 'danger'
  return 'info'
})

const totalWeight = computed(() =>
  editableRules.value.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
)

const availableDimensions = computed(() => {
  const used = new Set(editableRules.value.map(r => r.dimension))
  return allDimensions.value.filter(d => !used.has(d.key))
})

const weightStatusClass = computed(() => {
  const diff = Math.abs(totalWeight.value - 1.0)
  if (diff < 0.01) return 'optimal'
  if (diff < 0.1) return 'warning'
  return 'error'
})

// 级联：根据选中的职业过滤精英特长
const filteredEliteSpecs = computed(() => {
  const prof = cascadeProfessions.value.find(p => p.value === selectedBaseProfession.value)
  return prof?.elite_specs || []
})

// 评分等级列表
const gradeList = [
  { grade: 'S', range: '≥90分', desc: '表现卓越，远超平均水平', color: '#FFD700', color2: '#FFA500' },
  { grade: 'A', range: '≥80分', desc: '表现优秀，高于平均水平', color: '#00D68F', color2: '#00B4FF' },
  { grade: 'B', range: '≥70分', desc: '表现良好，达到平均水平', color: '#165DFF', color2: '#4080FF' },
  { grade: 'C', range: '≥60分', desc: '表现一般，略低于平均', color: '#FFAA00', color2: '#FFB347' },
  { grade: 'D', range: '≥40分', desc: '表现较差，需要改进', color: '#FF6B35', color2: '#FF8A65' },
  { grade: 'F', range: '<40分', desc: '表现很差，急需提升', color: '#FF4D6A', color2: '#FF8A80' },
]

function hasUnsavedChanges(role: string) {
  return changedRoles.value.has(role)
}

function getWeightProgress(role: string): number {
  const rules = currentRules.value[role] || []
  const total = rules.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
  return Math.min(total * 100, 100)
}

// ============================================
// 级联选择器辅助函数
// ============================================
function getProfessionColor(value: string): string {
  const prof = cascadeProfessions.value.find(p => p.value === value)
  return prof?.color || '#6b7280'
}

function getProfessionLabel(value: string): string {
  const prof = cascadeProfessions.value.find(p => p.value === value)
  return prof?.label || value
}

function getSpecColor(value: string): string {
  for (const prof of cascadeProfessions.value) {
    const spec = prof.elite_specs.find(s => s.value === value)
    if (spec) return spec.color
  }
  return '#6b7280'
}

function getSpecLabel(value: string): string {
  for (const prof of cascadeProfessions.value) {
    const spec = prof.elite_specs.find(s => s.value === value)
    if (spec) return spec.label
  }
  return value
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
    if (ruleScope.value === 'profession' && selectedProfession.value) {
      const data = await scoringRulesService.getRules(activeRole.value, selectedProfession.value)
      if (data && data.rules) {
        professionRulesMap.value[selectedProfession.value] = data.rules
      }
    } else {
      const data = await scoringRulesService.getRules()
      if (data) {
        for (const key of ['dps', 'support', 'tank']) {
          if (data[key]) {
            currentRules.value[key] = data[key].rules || []
          }
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
  let rules: ScoringRule[] = []
  if (ruleScope.value === 'profession' && selectedProfession.value) {
    rules = professionRulesMap.value[selectedProfession.value] || []
  } else {
    rules = currentRules.value[activeRole.value] || []
  }
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

    if (ruleScope.value === 'profession' && selectedProfession.value) {
      await scoringRulesService.upsertProfessionRules(selectedProfession.value, activeRole.value, rulesToSave)
      const refreshed = await scoringRulesService.getRules(activeRole.value, selectedProfession.value)
      if (refreshed && refreshed.rules) {
        professionRulesMap.value[selectedProfession.value] = refreshed.rules
      }
      toast.add({ severity: 'success', summary: '保存成功', detail: `${selectedProfession.value} 职业特定规则已更新`, life: 3000 })
    } else {
      await scoringRulesService.batchUpdate(activeRole.value, rulesToSave)
      const refreshed = await scoringRulesService.getRules(activeRole.value)
      if (refreshed && refreshed.rules) {
        currentRules.value[activeRole.value] = refreshed.rules
      }
      toast.add({ severity: 'success', summary: '保存成功', detail: `${activeRoleLabel.value}通用评分规则已更新`, life: 3000 })
    }

    changedRoles.value.delete(activeRole.value)
    syncEditableRules()
    await fetchVersions()
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
// v3.0 新增：规则范围切换
// ============================================
function switchScope(scope: 'generic' | 'profession') {
  ruleScope.value = scope
  if (scope === 'profession' && cascadeProfessions.value.length === 0) {
    fetchProfessions()
  }
  syncEditableRules()
}

function onBaseProfessionChange() {
  selectedProfession.value = ''
  editableRules.value = []
}

function onProfessionChange() {
  if (selectedProfession.value) {
    fetchRules()
  } else {
    editableRules.value = []
  }
}

async function fetchProfessions() {
  try {
    const data = await dictionaryService.getProfessionSpecsCascade()
    if (data && data.professions) {
      cascadeProfessions.value = data.professions
      // 同时保持旧的 professionOptions 兼容
      professionOptions.value = []
      for (const prof of data.professions) {
        for (const spec of prof.elite_specs) {
          professionOptions.value.push({
            label: `${spec.label} (${prof.label})`,
            value: spec.value,
          })
        }
      }
    }
  } catch (e) {
    console.error('获取职业级联数据失败', e)
    toast.add({ severity: 'warn', summary: '提示', detail: '获取职业列表失败，请刷新字典缓存', life: 3000 })
  }
}

async function fetchVersions() {
  try {
    versionHistory.value = await scoringRulesService.getVersions(0, 10)
  } catch (e) {
    console.error('获取版本历史失败', e)
  }
}

// ============================================
// v3.0 新增：重算任务
// ============================================
function confirmRecalculate() {
  confirm.require({
    message: '确定要将当前规则应用到所有历史数据吗？此操作将在后台异步执行，可能需要一段时间。',
    header: '确认应用到历史数据',
    icon: 'pi pi-history',
    accept: async () => {
      await startRecalculation()
    },
  })
}

async function startRecalculation() {
  recalculating.value = true
  try {
    const result = await scoringRulesService.triggerRecalculation(
      {},
      `${activeRoleLabel.value}通用规则更新后的历史数据重算`
    )
    if (result) {
      recalcTask.value = {
        version_id: result.version_id,
        version: result.version,
        status: result.status,
        total_records: 0,
        updated_records: 0,
        progress_percent: 0,
      }
      toast.add({ severity: 'info', summary: '重算任务已创建', detail: `版本 v${result.version}，正在后台执行`, life: 5000 })
      pollRecalcStatus(result.version_id)
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '重算任务创建失败', detail: e?.message || '操作失败', life: 5000 })
  } finally {
    recalculating.value = false
  }
}

function pollRecalcStatus(versionId: number) {
  if (recalcPollTimer) {
    clearInterval(recalcPollTimer)
    recalcPollTimer = null
  }

  recalcPollTimer = setInterval(async () => {
    try {
      const status = await scoringRulesService.getRecalculationStatus(versionId)
      if (status) {
        recalcTask.value = status
        if (status.status === 'completed' || status.status === 'failed') {
          if (recalcPollTimer) {
            clearInterval(recalcPollTimer)
            recalcPollTimer = null
          }
          if (status.status === 'completed') {
            toast.add({ severity: 'success', summary: '重算完成', detail: `已更新 ${status.updated_records} 条记录`, life: 5000 })
          }
          await fetchVersions()
        }
      }
    } catch (e) {
      console.error('轮询重算状态失败', e)
    }
  }, 3000)
}

// ============================================
// v3.0 新增：删除职业特定规则
// ============================================
function confirmDeleteProfessionRules() {
  confirm.require({
    message: `确定要删除 ${selectedProfession.value} 的职业特定规则吗？删除后将回退到通用规则。`,
    header: '确认删除职业规则',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      deletingProfession.value = true
      try {
        await scoringRulesService.deleteProfessionRules(selectedProfession.value)
        professionRulesMap.value[selectedProfession.value] = []
        syncEditableRules()
        toast.add({ severity: 'success', summary: '删除成功', detail: `${selectedProfession.value} 职业特定规则已删除`, life: 3000 })
      } catch (e: any) {
        toast.add({ severity: 'error', summary: '删除失败', detail: e?.message || '操作失败', life: 5000 })
      } finally {
        deletingProfession.value = false
      }
    },
  })
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// ============================================
// 生命周期
// ============================================
async function fetchRoleTypes() {
  try {
    const data = await scoringRulesService.getRoleTypes()
    if (data && data.length > 0) {
      roleTypes.value = data.map((r: any) => ({
        type: r.type,
        label: r.label,
        description: r.description || '',
        icon: roleIconMap[r.type] || 'pi pi-star',
        color: r.color || '#6b7280',
      }))
      if (!activeRole.value) {
        activeRole.value = data[0].type
      }
    }
  } catch (e) {
    console.error('获取角色类型失败', e)
    // 回退到硬编码默认值
    roleTypes.value = [
      { type: 'dps', label: '输出', description: '以伤害输出为主要职责', icon: 'pi pi-bolt', color: '#FF4D6A' },
      { type: 'support', label: '辅助', description: '以治疗和增益为主要职责', icon: 'pi pi-heart', color: '#00D68F' },
      { type: 'tank', label: '承伤', description: '以吸收伤害和控制为主要职责', icon: 'pi pi-shield', color: '#9D4EDD' },
    ]
    activeRole.value = 'dps'
  }
}

onMounted(async () => {
  await fetchRoleTypes()
  await fetchRules()
  await fetchDimensions()
  await fetchVersions()
})

watch(activeRole, () => {
  syncEditableRules()
})

watch(ruleScope, () => {
  syncEditableRules()
})

onUnmounted(() => {
  if (recalcPollTimer) {
    clearInterval(recalcPollTimer)
  }
})
</script>

<style scoped>
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

:deep(.p-inputnumber-input) {
  text-align: center;
  font-weight: 600;
  background: transparent;
  border: none;
  color: var(--color-text);
}

:deep(.p-toggleswitch.p-toggleswitch-checked .p-toggleswitch-slider) {
  background: linear-gradient(90deg, var(--color-success), #33E0A5);
}
</style>
