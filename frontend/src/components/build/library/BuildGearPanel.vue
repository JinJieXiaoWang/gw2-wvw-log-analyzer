<template>
  <Panel :header="$t('buildParser.equipment')" toggleable>
    <div class="space-y-3">
      <!-- 古物 + 符文 -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium mb-1">{{ $t('buildParser.relic') }}</label>
          <BaseSelect
            v-model="selectedRelics"
            :options="relicOptions"
            option-label="name"
            option-value="name"
            :placeholder="$t('buildParser.relic')"
            class="w-full"
            filter
            show-clear
            multiple
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">{{ $t('buildParser.runes') }}</label>
          <BaseSelect
            v-model="localForm.rune"
            :options="runeOptions"
            option-label="name"
            option-value="name"
            :placeholder="$t('buildParser.runes')"
            class="w-full"
            filter
            show-clear
          />
        </div>
      </div>
      <!-- 食物 + 扳手 -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium mb-1">{{ $t('buildParser.food') }}</label>
          <BaseSelect
            v-model="localForm.food"
            :options="foodOptions"
            option-label="name"
            option-value="name"
            :placeholder="$t('buildParser.food')"
            class="w-full"
            filter
            show-clear
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">{{ $t('buildParser.wrench') }}</label>
          <BaseSelect
            v-model="localForm.wrench"
            :options="utilityOptions"
            option-label="name"
            option-value="name"
            :placeholder="$t('buildParser.wrench')"
            class="w-full"
            filter
            show-clear
          />
        </div>
      </div>
      <!-- 护甲类型 -->
      <div>
        <label class="block text-sm font-medium mb-1">{{ $t('buildParser.armorType') }}</label>
        <BaseInput
          v-model="localForm.armorType"
          class="w-full"
          :placeholder="$t('buildParser.armorType')"
        />
      </div>
      <!-- 灌注 -->
      <div>
        <label class="block text-sm font-medium mb-1">{{ $t('buildParser.infusion') }}</label>
        <BaseInput
          v-model="localForm.infusion"
          class="w-full"
          :placeholder="$t('buildParser.infusion')"
        />
      </div>
      <!-- 武器配置 -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm font-medium">{{ $t('buildParser.weaponConfig') }}</label>
          <BaseButton
            icon="pi pi-plus"
            :label="$t('buildParser.addWeapon')"
            size="small"
            text
            @click="emit('add-weapon')"
          />
        </div>
        <div
          v-for="(w, idx) in localForm.weapons"
          :key="idx"
          class="flex items-start gap-2 mb-2"
        >
          <div class="flex-1 grid grid-cols-3 gap-2">
            <BaseInput
              v-model="w.name"
              placeholder="武器名称"
              class="w-full"
            />
            <BaseInput
              :model-value="w.sigils.join(',')"
              placeholder="法印（逗号分隔）"
              class="w-full col-span-2"
              @update:model-value="v => w.sigils = (v || '').split(',').map(s => s.trim()).filter(Boolean)"
            />
          </div>
          <BaseButton
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            @click="emit('remove-weapon', idx)"
          />
        </div>
      </div>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import type { BuildCreateDto } from '@/types/buildLibrary'
import { refDataService } from '@/services/game/refDataService'
import Panel from 'primevue/panel'
import { computed, onMounted, reactive, ref, watch } from 'vue'

interface RefItem {
  id: string
  name: string
  icon?: string
}

const props = defineProps<{
  form: BuildCreateDto
}>()

const emit = defineEmits<{
  'add-weapon': []
  'remove-weapon': [idx: number]
  'update:form': [form: BuildCreateDto]
}>()

const localForm = reactive<BuildCreateDto>({ ...props.form })

const relicOptions = ref<RefItem[]>([])
const runeOptions = ref<RefItem[]>([])
const foodOptions = ref<RefItem[]>([])
const utilityOptions = ref<RefItem[]>([])

/** 古物多选：字符串 <-> 数组 转换 */
const selectedRelics = computed<string[]>({
  get: () => {
    const r = localForm.relic
    return typeof r === 'string' && r ? r.split('/').map(s => s.trim()).filter(Boolean) : []
  },
  set: (val) => {
    localForm.relic = val.length ? val.join(' / ') : ''
  },
})

watch(
  () => props.form,
  (val) => {
    Object.assign(localForm, val)
    localForm.weapons = val.weapons ? [...val.weapons] : []
  },
  { deep: true }
)

watch(
  localForm,
  (val) => {
    emit('update:form', { ...val })
  },
  { deep: true }
)

async function loadRefData() {
  try {
    const [relicsRes, runesRes, foodsRes, utilsRes] = await Promise.all([
      refDataService.getRelics(),
      refDataService.getRunes(),
      refDataService.getFoods(),
      refDataService.getUtilities(),
    ])
    if (relicsRes.success && relicsRes.data) relicOptions.value = relicsRes.data.items
    if (runesRes.success && runesRes.data) runeOptions.value = runesRes.data.items
    if (foodsRes.success && foodsRes.data) foodOptions.value = foodsRes.data.items
    if (utilsRes.success && utilsRes.data) utilityOptions.value = utilsRes.data.items
  } catch (e) {
    console.error('加载参考数据失败:', e)
  }
}

onMounted(() => {
  loadRefData()
})
</script>
