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
          header="输出"
          value="0"
        >
          <RuleList
            :rules="rulesData.dps?.rules || []"
            empty-text="暂无输出角色的评分规则"
          />
        </TabPanel>
        <TabPanel
          header="辅助"
          value="1"
        >
          <RuleList
            :rules="rulesData.support?.rules || []"
            empty-text="暂无辅助角色的评分规则"
          />
        </TabPanel>
        <TabPanel
          header="承伤"
          value="2"
        >
          <RuleList
            :rules="rulesData.tank?.rules || []"
            empty-text="暂无承伤角色的评分规则"
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
        <BaseButton
          label="前往管理"
          icon="pi pi-external-link"
          size="small"
          text
          @click="goToRulesManagement"
        />
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
/**
 * 评分规则查看对话框组件
 * 功能：展示输出/辅助/承伤三种角色的评分规则配置
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

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    [RoleType.DPS]: '输出',
    [RoleType.SUPPORT]: '辅助',
    [RoleType.TANK]: '承伤'
  }
  return props.roleType ? (map[props.roleType] || '输出') : ''
})

const goToRulesManagement = () => {
  router.push('/scoring-rules')
}
</script>
