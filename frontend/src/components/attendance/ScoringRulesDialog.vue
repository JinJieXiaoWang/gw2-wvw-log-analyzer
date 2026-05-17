<template>
  <Dialog
    v-model:visible="localVisible"
    :header="roleLabel ? '评分规则配置 — ' + roleLabel : '评分规则配置'"
    :style="{ width: '640px', maxWidth: '95vw' }"
    modal
    :draggable="false"
    class="scoring-rules-dialog"
  >
    <LoadingState
      v-if="loading"
      text="加载评分规则中..."
    />
    <div v-else>
      <TabView v-model:active-index="localActiveTab">
        <TabPanel
          v-for="tab in roleTabs"
          :key="tab.roleKey"
          :header="tab.label"
          :value="tab.roleKey"
        >
          <RuleList
            :rules="rulesData[tab.roleKey]?.rules || []"
            :empty-text="`暂无${tab.label}角色的评分规则`"
          />
        </TabPanel>
      </TabView>

      <div class="mt-4 pt-4 border-t border-neutral-border/30">
        <p class="text-xs text-neutral-text-secondary mb-2">
          评分等级说明
        </p>
        <div class="flex flex-wrap gap-2">
          <Tag
            value="S 级 (≥90)"
            severity="success"
            class="text-[10px]"
          />
          <Tag
            value="A 级 (≥80)"
            severity="info"
            class="text-[10px]"
          />
          <Tag
            value="B 级 (≥70)"
            severity="warn"
            class="text-[10px]"
          />
          <Tag
            value="C 级 (≥60)"
            severity="secondary"
            class="text-[10px]"
          />
          <Tag
            value="D 级 (≥40)"
            severity="danger"
            class="text-[10px]"
          />
          <Tag
            value="F 级 (<40)"
            severity="danger"
            class="text-[10px]"
          />
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-neutral-border/30 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <i class="pi pi-tag text-xs text-neutral-text-secondary" />
          <span class="text-xs text-neutral-text-secondary">
            当前规则版本: <span class="font-semibold text-primary">v{{ ruleVersion }}</span>
          </span>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 评分规则查看对话框组件
 * 功能：动态展示所有角色类型的评分规则配置
 */

import { RoleType } from '@/constants/dictValues'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Tag from 'primevue/tag'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import RuleList from './RuleList.vue'

const router = useRouter()

const props = defineProps<{
  visible: boolean
  loading: boolean
  rulesData: Record<string, any>
  ruleVersion: number
  activeTab: number
  roleType?: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'update:activeTab': [value: number]
}>()

const localVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
})

const localActiveTab = computed({
  get: () => props.activeTab,
  set: v => emit('update:activeTab', v)
})

/** 角色类型 → 中文标签 */
const ROLE_LABEL_MAP: Record<string, string> = {
  [RoleType.DPS]: '输出',
  [RoleType.SUPPORT]: '辅助',
  [RoleType.TANK]: '承伤',
  [RoleType.CONTROL]: '削控',
}

/** 动态生成 Tab 列表，仅包含 rulesData 中实际存在的角色 */
const roleTabs = computed(() => {
  const keys = Object.keys(props.rulesData || {}).filter(
    k => ROLE_LABEL_MAP[k]
  )
  // 保持固定顺序：输出 → 辅助 → 承伤 → 削控
  const order: string[] = [RoleType.DPS, RoleType.SUPPORT, RoleType.TANK, RoleType.CONTROL]
  const sortedKeys = keys.sort(
    (a, b) => order.indexOf(a) - order.indexOf(b)
  )
  return sortedKeys.map(roleKey => ({
    roleKey,
    label: ROLE_LABEL_MAP[roleKey],
  }))
})

const roleLabel = computed(() => {
  return props.roleType ? (ROLE_LABEL_MAP[props.roleType] || '输出') : ''
})

const goToRulesManagement = () => {
  router.push('/scoring-rules')
}
</script>
