<template>
  <Dialog v-model:visible="localVisible" :header="`评分规则配置 - ${currentRoleLabel}`" :style="{ width: '640px', maxWidth: '95vw' }" :modal="true" :draggable="false" class="scoring-rules-dialog">
    <LoadingState v-if="loading" text="加载规则..." />
    <div v-else>
      <TabView v-model:active-index="activeTab">
        <TabPanel v-for="tab in ROLE_TABS" :key="tab.key" :value="tab.key" :header="tab.label">
          <div class="space-y-3">
            <div v-if="rulesData[tab.key]?.rules?.length" class="text-xs text-neutral-text-secondary mb-2">
              {{ rulesData[tab.key].rules.length }} 个人评分维度
            </div>
            <div v-for="rule in (rulesData[tab.key]?.rules || [])" :key="rule.id || rule.dimension" class="card p-3 rounded-lg border border-neutral-border/40" :class="rule.is_active ? '' : 'opacity-50'">
              <div class="flex items-center justify-between gap-3">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-semibold text-neutral-text">{{ rule.dimension }}</span>
                    <BaseTag v-if="!rule.is_active" value="已禁用" severity="secondary" class="text-[10px] px-1 py-0" />
                  </div>
                  <p v-if="rule.description" class="text-xs text-neutral-text-secondary truncate">{{ rule.description }}</p>
                </div>
                <div class="flex items-center gap-3 shrink-0">
                  <span class="text-lg font-bold text-primary">{{ (rule.weight * 100).toFixed(0) }}%</span>
                  <div class="w-24">
                    <div class="h-2 rounded-full bg-neutral-bg overflow-hidden">
                      <div class="h-full rounded-full bg-primary transition-all" :style="{ width: Math.min(rule.weight * 100, 100) + '%' }" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!rulesData[tab.key]?.rules?.length" class="text-center py-8 text-neutral-text-secondary text-sm">
              <i class="pi pi-info-circle text-lg mb-2 block" />暂无{{ tab.label }}角色的评分规则
            </div>
          </div>
        </TabPanel>
      </TabView>

      <div class="mt-4 pt-4 border-t border-neutral-border/30">
        <p class="text-xs text-neutral-text-secondary mb-2">评分等级说明</p>
        <div class="flex flex-wrap gap-2">
          <BaseTag value="S 绾?(>=90)" severity="success" class="text-[10px]" />
          <BaseTag value="A 绾?(>=80)" severity="info" class="text-[10px]" />
          <BaseTag value="B 绾?(>=70)" severity="warn" class="text-[10px]" />
          <BaseTag value="C 绾?(>=60)" severity="secondary" class="text-[10px]" />
          <BaseTag value="D 绾?(>=50)" severity="danger" class="text-[10px]" />
          <BaseTag value="F 绾?(<40)" severity="danger" class="text-[10px]" />
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-neutral-border/30 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <i class="pi pi-tag text-xs text-neutral-text-secondary" />
          <span class="text-xs text-neutral-text-secondary">当前规则版本: <span class="font-semibold text-primary">v{{ currentRuleVersion }}</span></span>
        </div>
        <BaseButton label="前往管理页面" icon="pi pi-external-link" size="small" text class="text-xs" @click="goManage" />
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import LoadingState from '@/components/common/ui/LoadingState.vue'
import BaseTag from '@/components/common/ui/BaseTag.vue'
import BaseButton from '@/components/common/ui/BaseButton.vue'

const ROLE_TABS = [
  { key: 'dps', label: '输出' },
  { key: 'support', label: '辅助' },
  { key: 'tank', label: '承伤' }
]

const props = defineProps<{
  visible: boolean
  loading: boolean
  rulesData: Record<string, any>
  currentRoleLabel: string
  currentRuleVersion: number
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const router = useRouter()
const activeTab = ref(0)

const localVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
})

function goManage() {
  router.push('/scoring-rules')
}
</script>
