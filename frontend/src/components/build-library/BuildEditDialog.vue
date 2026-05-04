<template>
  <Dialog
    v-model:visible="localVisible"
    :header="isEdit ? '编辑配置' : '新增配置'"
    :style="{ width: '720px', maxWidth: '95vw' }"
    :modal="true"
    :closable="!submitting"
    :close-on-escape="!submitting"
    @hide="onHide"
  >
    <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
      <!-- 基本信息 -->
      <Panel header="基本信息" toggleable :collapsed="false">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">配置标题 <span class="text-red-400">*</span></label>
            <InputText v-model="form.title" class="w-full" placeholder="输入配置标题" />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">职业 <span class="text-red-400">*</span></label>
            <Select v-model="form.profession" :options="professionOptions" option-label="label" option-value="value"
              class="w-full" placeholder="选择职业" />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">精英特长</label>
            <InputText v-model="form.eliteSpec" class="w-full" placeholder="如：全息、燃火" />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">角色类型 <span class="text-red-400">*</span></label>
            <Select v-model="form.role" :options="roleOptions" option-label="label" option-value="value"
              class="w-full" placeholder="选择角色" />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">子角色</label>
            <div class="flex flex-wrap gap-2">
              <Button v-for="sr in subRoleOptions" :key="sr.value"
                :severity="form.subRoles.includes(sr.value) ? 'primary' : 'secondary'"
                :outlined="!form.subRoles.includes(sr.value)" size="small" @click="toggleSubRole(sr.value)">
                {{ sr.label }}
              </Button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">护甲类型</label>
            <InputText v-model="form.armorType" class="w-full" placeholder="如：狂战士、吟游诗人" />
          </div>

          <div class="flex items-center gap-3">
            <label class="text-sm font-medium">META 配置</label>
            <InputSwitch v-model="form.isMeta" />
          </div>
        </div>
      </Panel>

      <!-- 配装 -->
      <Panel header="配装" toggleable>
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium mb-1">Relic</label>
              <InputText v-model="form.relic" class="w-full" placeholder="古物名称" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">符文</label>
              <InputText v-model="form.rune" class="w-full" placeholder="符文名称" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">食物</label>
              <InputText v-model="form.food" class="w-full" placeholder="食物名称" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">扳手</label>
              <InputText v-model="form.wrench" class="w-full" placeholder="扳手/保养油" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">灌注</label>
            <InputText v-model="form.infusion" class="w-full" placeholder="灌注类型" />
          </div>

          <!-- 武器 -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium">武器配置</label>
              <Button icon="pi pi-plus" label="添加武器" size="small" text @click="addWeapon" />
            </div>
            <div v-for="(w, idx) in form.weapons" :key="idx" class="flex items-start gap-2 mb-2">
              <div class="flex-1 grid grid-cols-3 gap-2">
                <InputText v-model="w.name" placeholder="武器名称" class="w-full" />
                <InputText v-model="sigilsText[idx]" placeholder="法印（逗号分隔）" class="w-full col-span-2" />
              </div>
              <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeWeapon(idx)" />
            </div>
          </div>
        </div>
      </Panel>

      <!-- Build 代码 -->
      <Panel header="Build 代码" toggleable :collapsed="false">
        <div>
          <label class="block text-sm font-medium mb-1">BD Code <span class="text-red-400">*</span></label>
          <div class="flex gap-2">
            <Textarea v-model="form.bdCode" class="w-full font-mono flex-1" rows="2" placeholder="[&...]" />
            <Button icon="pi pi-bolt" label="解析" severity="help" :loading="parsing"
              :disabled="!form.bdCode.trim().startsWith('[&')" @click="parseBDCode" />
          </div>
          <p class="text-xs text-surface-500 mt-1">输入 BD Code 后点击「解析」可自动填充职业、特性线等数据</p>
        </div>
      </Panel>

      <!-- 特性线 -->
      <Panel header="特性线" toggleable>
        <div class="space-y-2">
          <div v-for="(t, idx) in form.traitLines" :key="idx" class="flex items-center gap-2">
            <InputText v-model="t.name" placeholder="特性线名称" class="flex-1" />
            <div class="flex gap-1">
              <Select v-for="cIdx in [0, 1, 2]" :key="cIdx" v-model="t.choices[cIdx]"
                :options="[1, 2, 3]" class="w-14" />
            </div>
            <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeTraitLine(idx)" />
          </div>
          <Button icon="pi pi-plus" label="添加特性线" size="small" text @click="addTraitLine" />
        </div>
      </Panel>

      <!-- 循环指令 -->
      <Panel header="指挥口令" toggleable>
        <div class="space-y-2">
          <div v-for="(c, idx) in form.rotationCommands" :key="idx" class="grid grid-cols-[1fr_2fr_auto] gap-2 items-center">
            <InputText v-model="c.callout" placeholder="口令" />
            <InputText v-model="c.action" placeholder="操作说明" />
            <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeRotationCommand(idx)" />
          </div>
          <Button icon="pi pi-plus" label="添加口令" size="small" text @click="addRotationCommand" />
        </div>
      </Panel>

      <!-- 机制说明 -->
      <Panel header="关键机制" toggleable>
        <div class="space-y-2">
          <div v-for="(m, idx) in form.mechanics" :key="idx" class="space-y-2 p-3 rounded-lg bg-surface-900 border border-surface-700">
            <div class="flex items-center gap-2">
              <InputText v-model="m.name" placeholder="机制名称" class="flex-1" />
              <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeMechanic(idx)" />
            </div>
            <div v-for="(_, sIdx) in m.sources" :key="sIdx" class="flex items-center gap-2">
              <InputText v-model="m.sources[sIdx]" placeholder="来源说明" class="flex-1" />
              <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeMechanicSource(idx, sIdx)" />
            </div>
            <Button icon="pi pi-plus" label="添加来源" size="small" text @click="addMechanicSource(idx)" />
          </div>
          <Button icon="pi pi-plus" label="添加机制" size="small" text @click="addMechanic" />
        </div>
      </Panel>

      <!-- 视频链接 -->
      <Panel header="参考视频" toggleable>
        <div class="space-y-2">
          <div v-for="(v, idx) in form.videos" :key="idx" class="grid grid-cols-[1fr_1fr_auto] gap-2 items-center">
            <InputText v-model="v.title" placeholder="视频标题" />
            <InputText v-model="v.url" placeholder="视频链接" />
            <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeVideo(idx)" />
          </div>
          <Button icon="pi pi-plus" label="添加视频" size="small" text @click="addVideo" />
        </div>
      </Panel>

      <!-- 属性要求 -->
      <Panel header="属性要求" toggleable>
        <div class="space-y-2">
          <div v-for="(_, idx) in form.attrRequirements" :key="idx" class="flex items-center gap-2">
            <InputText v-model="form.attrRequirements[idx]" placeholder="属性要求说明" class="flex-1" />
            <Button icon="pi pi-trash" severity="danger" text size="small" @click="removeAttrRequirement(idx)" />
          </div>
          <Button icon="pi pi-plus" label="添加要求" size="small" text @click="addAttrRequirement" />
        </div>
      </Panel>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button label="取消" severity="secondary" outlined :disabled="submitting" @click="localVisible = false" />
        <Button :label="isEdit ? '保存修改' : '创建配置'" severity="primary" :loading="submitting"
          :disabled="!isValid" @click="onSubmit" />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Panel from 'primevue/panel'
import InputSwitch from 'primevue/inputswitch'
import type { BuildEntry, BuildCreateDto } from '@/types/buildLibrary'
import { VALID_PROFESSIONS } from '@/types/buildLibrary'
import { useBuildLibraryStore } from '@/store/build/buildLibrary'
import { useToast } from 'primevue/usetoast'
import { bdCodeService } from '@/services/build/bdCodeService'

interface Props {
  visible: boolean
  editingBuild?: BuildEntry | null
}

const props = withDefaults(defineProps<Props>(), {
  editingBuild: null
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  saved: [build: BuildEntry]
}>()

const store = useBuildLibraryStore()
const toast = useToast()

const localVisible = computed({
  get: () => props.visible,
  set: (v) => emit('update:visible', v)
})

const isEdit = computed(() => !!props.editingBuild)
const submitting = ref(false)

const professionOptions = VALID_PROFESSIONS.map(p => ({ label: p, value: p }))
const roleOptions = [
  { label: '输出 (DPS)', value: 'dps' },
  { label: '辅助 (Support)', value: 'support' }
]
type SubRoleType = 'boon' | 'heal' | 'tank' | 'cc'
const subRoleOptions: { label: string; value: SubRoleType }[] = [
  { label: '增益', value: 'boon' },
  { label: '治疗', value: 'heal' },
  { label: '承伤', value: 'tank' },
  { label: '削控', value: 'cc' }
]

function createEmptyForm(): BuildCreateDto {
  return {
    title: '',
    profession: 'Elementalist',
    eliteSpec: null,
    role: 'dps',
    subRoles: [],
    armorType: '',
    weapons: [],
    relic: '',
    rune: '',
    food: '',
    wrench: '',
    infusion: '',
    attrRequirements: [],
    bdCode: '',
    traitLines: [],
    rotationCommands: [],
    mechanics: [],
    videos: [],
    author: ''
  }
}

const form = ref<BuildCreateDto>(createEmptyForm())

// 用于武器法印编辑的临时文本
const sigilsText = computed({
  get: () => form.value.weapons.map(w => w.sigils.join(',')),
  set: (vals: string[]) => {
    form.value.weapons.forEach((w, i) => {
      w.sigils = vals[i] ? vals[i].split(',').map(s => s.trim()).filter(Boolean) : []
    })
  }
})

const parsing = ref(false)

const isValid = computed(() => {
  return form.value.title.trim().length >= 2 &&
    form.value.profession.length > 0 &&
    form.value.role.length > 0 &&
    /^\[&[A-Za-z0-9+/=]+\]$/.test(form.value.bdCode.trim())
})

function toggleSubRole(role: SubRoleType) {
  const idx = form.value.subRoles.indexOf(role)
  if (idx >= 0) {
    form.value.subRoles.splice(idx, 1)
  } else {
    form.value.subRoles.push(role)
  }
}

// 武器
function addWeapon() {
  form.value.weapons.push({ set: form.value.weapons.length + 1, name: '', sigils: [] })
}
function removeWeapon(idx: number) {
  form.value.weapons.splice(idx, 1)
}

// 特性线
function addTraitLine() {
  form.value.traitLines.push({ name: '', choices: [1, 1, 1] })
}
function removeTraitLine(idx: number) {
  form.value.traitLines.splice(idx, 1)
}

// 循环指令
function addRotationCommand() {
  form.value.rotationCommands.push({ callout: '', action: '', note: '' })
}
function removeRotationCommand(idx: number) {
  form.value.rotationCommands.splice(idx, 1)
}

// 机制
function addMechanic() {
  form.value.mechanics.push({ name: '', sources: [] })
}
function removeMechanic(idx: number) {
  form.value.mechanics.splice(idx, 1)
}
function addMechanicSource(mechIdx: number) {
  form.value.mechanics[mechIdx].sources.push('')
}
function removeMechanicSource(mechIdx: number, srcIdx: number) {
  form.value.mechanics[mechIdx].sources.splice(srcIdx, 1)
}

// 视频
function addVideo() {
  form.value.videos.push({ title: '', url: '', author: undefined })
}
function removeVideo(idx: number) {
  form.value.videos.splice(idx, 1)
}

// 属性要求
function addAttrRequirement() {
  form.value.attrRequirements.push('')
}
function removeAttrRequirement(idx: number) {
  form.value.attrRequirements.splice(idx, 1)
}

// 回填
watch(() => props.editingBuild, (build) => {
  if (build) {
    form.value = {
      title: build.title,
      profession: build.profession,
      eliteSpec: build.eliteSpec,
      role: build.role,
      subRoles: [...build.subRoles],
      armorType: build.armorType,
      weapons: build.weapons.map(w => ({ ...w })),
      relic: build.relic,
      rune: build.rune,
      food: build.food,
      wrench: build.wrench,
      infusion: build.infusion,
      attrRequirements: [...build.attrRequirements],
      bdCode: build.bdCode,
      traitLines: build.traitLines.map(t => ({ name: t.name, choices: [...t.choices] })),
      rotationCommands: build.rotationCommands.map(c => ({ ...c })),
      mechanics: build.mechanics.map(m => ({ name: m.name, sources: [...m.sources] })),
      videos: build.videos.map(v => ({ ...v })),
      author: build.author
    }
  } else {
    form.value = createEmptyForm()
  }
}, { immediate: true })

function onHide() {
  if (!submitting.value) {
    form.value = createEmptyForm()
  }
}

async function parseBDCode() {
  const code = form.value.bdCode.trim()
  if (!code.startsWith('[&')) {
    toast.add({ severity: 'warn', summary: '格式错误', detail: 'BD Code 必须以 [& 开头', life: 3000 })
    return
  }
  parsing.value = true
  try {
    const response = await bdCodeService.parseBDCode({ bd_code: code })
    const data = response.data
    if (!data) {
      toast.add({ severity: 'error', summary: '解析失败', detail: '无法解析该 BD Code', life: 3000 })
      return
    }

    // 填充职业
    if (data.profession) {
      const profMap: Record<string, string> = {
        'Guardian': 'Guardian',
        'Revenant': 'Revenant',
        'Warrior': 'Warrior',
        'Engineer': 'Engineer',
        'Ranger': 'Ranger',
        'Thief': 'Thief',
        'Elementalist': 'Elementalist',
        'Mesmer': 'Mesmer',
        'Necromancer': 'Necromancer',
      }
      const prof = profMap[data.profession]
      if (prof) {
        form.value.profession = prof
      }
    }

    // 填充精英特长
    const specs = data.specializations || []
    const eliteSpec = specs.find((s: any) => s.is_elite)
    if (eliteSpec?.name_cn || eliteSpec?.name) {
      form.value.eliteSpec = eliteSpec.name_cn || eliteSpec.name
    }

    // 填充特性线
    form.value.traitLines = specs
      .filter((s: any) => Array.isArray(s.selected_traits) && s.selected_traits.length === 3)
      .map((s: any) => ({
        name: s.name_cn || s.name || '',
        choices: s.selected_traits as [number, number, number]
      }))
      .filter((t: any) => t.name)

    toast.add({
      severity: 'success',
      summary: '解析成功',
      detail: `已自动填充职业、${form.value.traitLines.length} 条特性线`,
      life: 3000
    })
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '解析失败', detail: e?.message || '网络错误', life: 5000 })
  } finally {
    parsing.value = false
  }
}

async function onSubmit() {
  if (!isValid.value) return
  submitting.value = true
  try {
    let result: any
    if (isEdit.value && props.editingBuild) {
      result = await store.updateBuild(props.editingBuild.id, form.value as any)
    } else {
      result = await store.createBuild(form.value)
    }
    if (result.success) {
      toast.add({
        severity: 'success',
        summary: isEdit.value ? '修改成功' : '创建成功',
        detail: `配置「${form.value.title}」已${isEdit.value ? '更新' : '创建'}`,
        life: 3000
      })
      localVisible.value = false
      if (result.data) {
        emit('saved', result.data)
      }
    } else {
      toast.add({
        severity: 'error',
        summary: isEdit.value ? '修改失败' : '创建失败',
        detail: result.error || '未知错误',
        life: 5000
      })
    }
  } catch (e: any) {
    toast.add({
      severity: 'error',
      summary: '提交失败',
      detail: e?.message || '网络错误或服务器异常',
      life: 5000
    })
  } finally {
    submitting.value = false
  }
}
</script>
