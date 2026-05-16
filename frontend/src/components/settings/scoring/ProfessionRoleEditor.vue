<template>
  <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-6 shadow-lg">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h4 class="flex items-center gap-2 text-lg font-semibold text-color">
          <i class="pi pi-sitemap text-primary-500" />
          职业定位管理
        </h4>
        <p class="text-sm text-color-secondary mt-1">
          管理各职业的默认定位划分，决定评分规则的应用范围
        </p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 text-sm">
          <span class="text-color-secondary">当前评分模式：</span>
          <BaseTag
            :value="scoringMode === 'role_based' ? '角色定位评分' : '职业评分'"
            :severity="scoringMode === 'role_based' ? 'info' : 'success'"
          />
        </div>
        <template v-if="isEditMode">
          <BaseButton
            label="取消"
            icon="pi pi-times"
            severity="secondary"
            outlined
            @click="emit('toggle-edit')"
          />
          <BaseButton
            label="保存更改"
            icon="pi pi-check"
            severity="success"
            @click="emit('save')"
          />
        </template>
        <BaseButton
          v-else-if="canWrite"
          label="编辑定位"
          icon="pi pi-pencil"
          severity="primary"
          outlined
          @click="emit('toggle-edit')"
        />
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div
        v-for="role in roleTypes"
        :key="role.type"
        class="rounded-xl border-2 p-4 transition-all"
        :style="{ borderColor: role.color + '40', background: role.color + '05' }"
      >
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center text-white"
            :style="{ background: role.color }"
          >
            <i :class="role.icon" />
          </div>
          <div>
            <h5 class="font-semibold text-color">
              {{ role.label }}
            </h5>
            <span class="text-xs text-color-secondary">
              {{ professionByRole[role.type]?.length || 0 }} 个职业
            </span>
          </div>
        </div>

        <div class="space-y-2">
          <div
            v-for="prof in professionByRole[role.type]"
            :key="prof.profession"
            class="bg-surface-0 dark:bg-surface-800 rounded-lg p-3 text-sm"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <i
                  :class="prof.icon"
                  class="text-sm"
                  :style="{ color: role.color }"
                />
                <span class="font-medium">{{ prof.profession }}</span>
              </div>
              <BaseSelect
                v-if="isEditMode"
                v-model="prof.currentRole"
                :options="roleOptions"
                option-label="label"
                option-value="type"
                size="small"
                class="w-28"
                @change="() => onProfessionRoleChange(prof)"
              />
            </div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="spec in prof.eliteSpecs.slice(0, 4)"
                :key="spec"
                class="inline-block px-2 py-0.5 rounded text-xs"
                :style="{ background: role.color + '20', color: role.color }"
              >
                {{ spec }}
              </span>
              <span
                v-if="prof.eliteSpecs.length > 4"
                class="inline-block px-2 py-0.5 rounded text-xs bg-surface-100 dark:bg-surface-700 text-color-secondary"
              >
                +{{ prof.eliteSpecs.length - 4 }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4 p-3 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
      <p class="text-xs text-color">
        <i class="pi pi-info-circle mr-1" />
        <strong>评分说明：</strong>
        <span v-if="scoringMode === 'role_based'">
          当前使用「角色定位评分」，所有职业按其默认定位（DPS/辅助/承伤）应用评分规则
        </span>
        <span v-else>
          当前使用「职业评分」，优先使用职业特定评分规则，无则回退到角色定位规则
        </span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseTag from '@/components/common/ui/display/BaseTag.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'

export interface RoleType {
  type: string
  label: string
  description: string
  icon: string
  color: string
}

export interface ProfessionMapping {
  profession: string
  role: string
  roleLabel: string
  icon: string
  eliteSpecs: string[]
  currentRole: string
}

interface Props {
  roleTypes: RoleType[]
  professionRoleMapping: ProfessionMapping[]
  isEditMode: boolean
  canWrite: boolean
  scoringMode: 'role_based' | 'profession_based'
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'toggle-edit': []
  save: []
  'profession-change': [profession: any]
}>()

const roleOptions = computed(() => props.roleTypes.map(r => ({ type: r.type, label: r.label })))

const professionByRole = computed(() => {
  const grouped: Record<string, any[]> = {}
  for (const mapping of props.professionRoleMapping) {
    const role = props.isEditMode ? mapping.currentRole : mapping.role
    if (!grouped[role]) {
      grouped[role] = []
    }
    const roleInfo = props.roleTypes.find(r => r.type === role)
    grouped[role].push({
      ...mapping,
      roleLabel: roleInfo?.label || role,
    })
  }
  return grouped
})

function onProfessionRoleChange(prof: any) {
  emit('profession-change', { ...prof, currentRole: prof.currentRole })
}
</script>

<script lang="ts">
import { computed } from 'vue'
export default {
  name: 'ProfessionRoleEditor',
}
</script>
