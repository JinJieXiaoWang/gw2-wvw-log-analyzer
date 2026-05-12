<template>
  <div class="build-parser-view">
    <PageHeader
      title="Build解析"
      subtitle="解析并管理你的GW2 Build配置"
      icon="pi pi-code"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <div class="lg:col-span-1">
        <BuildCodeInput
          v-model:build-code="buildCode"
          :is-parsing="isParsing"
          :parse-error="parseError"
          @parse-build-code="handleParseBuildCode"
          @show-import-dialog="showImportDialog = true"
          @clear-code="handleClearCode"
        />
        <SaveDialog
          v-model:visible="showSaveDialog"
          :parsed-data="parsedData"
          :build-code="buildCode"
          @save="handleSaveBuild"
        />
        <ImportDialog
          v-model:visible="showImportDialog"
          @import-build-code="handleImportBuildCode"
        />
      </div>

      <div class="lg:col-span-2 space-y-6">
        <div
          v-if="parsedData"
          class="card"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-xl"
                :style="{ background: getProfessionColor(parsedData.profession) }"
              >
                {{ getProfessionInitial(parsedData.profession) }}
              </div>
              <div>
                <h3 class="text-lg font-semibold text-neutral-text">
                  {{ parsedData.profession_cn }}
                </h3>
                <p class="text-sm text-neutral-text-secondary">
                  {{ eliteSpecName || '核心职业' }}
                </p>
              </div>
            </div>
            <div class="flex gap-2">
              <Button
                label="保存Build"
                icon="pi pi-save"
                class="btn-game"
                @click="showSaveDialog = true"
              />
              <Button
                label="复制代码"
                icon="pi pi-copy"
                class="btn-ghost"
                @click="handleCopyBuildCode"
              />
            </div>
          </div>
        </div>

        <BuildTraitsPanel :parsed-data="parsedData" />
        <BuildSkillsPanel :parsed-data="parsedData" />

        <div
          v-if="parsedData"
          class="card"
        >
          <h3 class="text-lg font-semibold text-neutral-text mb-4">
            BD码
          </h3>
          <div class="p-4 bg-neutral-800 rounded-lg font-mono text-sm">
            <code>{{ parsedData.bd_code }}</code>
          </div>
        </div>

        <div
          v-else
          class="card text-center py-12"
        >
          <i class="pi pi-code text-5xl text-neutral-text-secondary mb-4 opacity-50" />
          <h3 class="text-lg font-semibold text-neutral-text mb-2">
            输入Build代码开始解析
          </h3>
          <p class="text-neutral-text-secondary">
            粘贴你的GW2 Build代码（如 [&DQgBAAA=]），点击解析按钮即可
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import PageHeader from '@/layout/components/PageHeader.vue'
import BuildCodeInput from '@/components/build/parser/BuildCodeInput.vue'
import ImportDialog from '@/components/build/parser/ImportDialog.vue'
import SaveDialog from '@/components/build/parser/SaveDialog.vue'
import BuildTraitsPanel from '@/components/build/parser/BuildTraitsPanel.vue'
import BuildSkillsPanel from '@/components/build/parser/BuildSkillsPanel.vue'
import buildApi from '@/api/build/build'
import { getProfessionColor, getProfessionInitial } from '@/utils/build/buildParserUtils'

const toast = useToast()

const buildCode = ref('')
const isParsing = ref(false)
const parseError = ref('')
const parsedData = ref<any>(null)
const showSaveDialog = ref(false)
const showImportDialog = ref(false)

const eliteSpecName = computed(() => {
  if (!parsedData.value?.specializations) return ''
  const eliteSpec = parsedData.value.specializations.find((spec: any) => spec.is_elite)
  return eliteSpec?.name_cn || ''
})

const handleParseBuildCode = async () => {
  if (!buildCode.value.trim()) {
    parseError.value = '请输入Build代码'
    return
  }
  const codePattern = /^\[&[A-Za-z0-9+/=]+\]$/
  if (!codePattern.test(buildCode.value.trim())) {
    parseError.value = 'Build代码格式不正确，应为 [&...] 格式'
    return
  }
  isParsing.value = true
  parseError.value = ''
  try {
    const result = await buildApi.parseBuildCode(buildCode.value.trim())
    if (result) {
      parsedData.value = result
      toast.add({ severity: 'success', summary: '解析成功', detail: 'Build代码解析完成', life: 3000 })
    } else {
      parseError.value = '解析失败，请稍后重试'
    }
  } catch (error) {
    console.error('解析Build代码失败:', error)
    parseError.value = error instanceof Error ? error.message : '解析失败'
    toast.add({ severity: 'error', summary: '解析失败', detail: parseError.value, life: 5000 })
  } finally {
    isParsing.value = false
  }
}

const handleClearCode = () => {
  buildCode.value = ''
  parsedData.value = null
  parseError.value = ''
}

const handleImportBuildCode = (code: string) => {
  buildCode.value = code
  showImportDialog.value = false
}

const handleSaveBuild = async (buildData: any) => {
  try {
    await buildApi.saveBuild(buildData)
    showSaveDialog.value = false
    toast.add({ severity: 'success', summary: '保存成功', detail: 'Build配置已保存', life: 3000 })
  } catch (error) {
    console.error('保存Build失败:', error)
    toast.add({ severity: 'error', summary: '保存失败', detail: error instanceof Error ? error.message : '保存失败', life: 5000 })
  }
}

const handleCopyBuildCode = async () => {
  if (!buildCode.value) return
  try {
    await navigator.clipboard.writeText(buildCode.value)
    toast.add({ severity: 'success', summary: '复制成功', detail: 'Build代码已复制到剪贴板', life: 2000 })
  } catch (error) {
    console.error('复制失败:', error)
    toast.add({ severity: 'error', summary: '复制失败', detail: '无法复制到剪贴板', life: 3000 })
  }
}
</script>

<style scoped lang="postcss">
.build-parser-view {
  min-height: 100vh;
  padding-bottom: 2rem;
}

.card {
  @apply bg-neutral-900 rounded-xl p-6 border border-neutral-800;
}
</style>
