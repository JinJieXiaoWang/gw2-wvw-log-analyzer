<template>
  <div class="build-parser-view">
    <PageHeader
      :title="PAGE_TITLE"
      :subtitle="PAGE_SUBTITLE"
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
              <!-- 动态值，无法使用 Tailwind 静态类 -->
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
                  {{ eliteSpecName || DEFAULT_ELITE_SPEC_NAME }}
                </p>
              </div>
            </div>
            <div class="flex gap-2">
              <BaseButton
                :label="SAVE_BUILD_LABEL"
                icon="pi pi-save"
                class="btn-game"
                @click="showSaveDialog = true"
              />
              <BaseButton
                :label="COPY_CODE_LABEL"
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
            {{ BD_CODE_TITLE }}
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
            {{ EMPTY_STATE_TITLE }}
          </h3>
          <p class="text-neutral-text-secondary">
            {{ EMPTY_STATE_DESCRIPTION }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import PageHeader from '@/layout/components/PageHeader.vue'
import BuildCodeInput from '@/components/build/parser/BuildCodeInput.vue'
import ImportDialog from '@/components/build/parser/ImportDialog.vue'
import SaveDialog from '@/components/build/parser/SaveDialog.vue'
import BuildTraitsPanel from '@/components/build/parser/BuildTraitsPanel.vue'
import BuildSkillsPanel from '@/components/build/parser/BuildSkillsPanel.vue'
import { buildsService } from '@/services/build/buildsService'
import { getProfessionColor, getProfessionInitial } from '@/utils/build/buildParserUtils'

// ========== 常量定义 ==========

// 页面文案
const PAGE_TITLE = 'Build解析'
const PAGE_SUBTITLE = '解析并管理你的GW2 Build配置'
const DEFAULT_ELITE_SPEC_NAME = '核心职业'
const BD_CODE_TITLE = 'BD码'
const EMPTY_STATE_TITLE = '输入Build代码开始解析'
const EMPTY_STATE_DESCRIPTION = '粘贴你的GW2 Build代码（如 [&DQgBAAA=]），点击解析按钮即可'
const SAVE_BUILD_LABEL = '保存Build'
const COPY_CODE_LABEL = '复制代码'

// Build代码验证
const BUILD_CODE_REQUIRED = '请输入Build代码'
const BUILD_CODE_FORMAT_ERROR = 'Build代码格式不正确，应为 [&...] 格式'
const BUILD_CODE_PATTERN = /^\[&[A-Za-z0-9+/=]+\]$/

// Toast 生命周期
const TOAST_LIFE_SHORT = 2000
const TOAST_LIFE_NORMAL = 3000
const TOAST_LIFE_LONG = 5000

// Toast 消息
const PARSE_SUCCESS_SUMMARY = '解析成功'
const PARSE_SUCCESS_DETAIL = 'Build代码解析完成'
const PARSE_RETRY_ERROR = '解析失败，请稍后重试'
const PARSE_FAILED_SUMMARY = '解析失败'
const SAVE_SUCCESS_SUMMARY = '保存成功'
const SAVE_SUCCESS_DETAIL = 'Build配置已保存'
const SAVE_FAILED_SUMMARY = '保存失败'
const GENERIC_SAVE_FAILED = '保存失败'
const COPY_SUCCESS_SUMMARY = '复制成功'
const COPY_SUCCESS_DETAIL = 'Build代码已复制到剪贴板'
const COPY_FAILED_SUMMARY = '复制失败'
const COPY_FAILED_DETAIL = '无法复制到剪贴板'

// 控制台错误前缀
const LOG_PARSE_ERROR_PREFIX = '解析Build代码失败:'
const LOG_SAVE_ERROR_PREFIX = '保存Build失败:'
const LOG_COPY_ERROR_PREFIX = '复制失败:'

// ========== 逻辑 ==========

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
    parseError.value = BUILD_CODE_REQUIRED
    return
  }
  if (!BUILD_CODE_PATTERN.test(buildCode.value.trim())) {
    parseError.value = BUILD_CODE_FORMAT_ERROR
    return
  }
  isParsing.value = true
  parseError.value = ''
  try {
    const response = await buildsService.parseBuild(buildCode.value.trim())
    if (response.success && response.data) {
      parsedData.value = response.data
      toast.add({ severity: 'success', summary: PARSE_SUCCESS_SUMMARY, detail: PARSE_SUCCESS_DETAIL, life: TOAST_LIFE_NORMAL })
    } else {
      parseError.value = PARSE_RETRY_ERROR
    }
  } catch (error) {
    console.error(LOG_PARSE_ERROR_PREFIX, error)
    parseError.value = error instanceof Error ? error.message : PARSE_FAILED_SUMMARY
    toast.add({ severity: 'error', summary: PARSE_FAILED_SUMMARY, detail: parseError.value, life: TOAST_LIFE_LONG })
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
    const saveResponse = await buildsService.createBuild(buildData)
    if (!saveResponse.success) {
      throw new Error(GENERIC_SAVE_FAILED)
    }
    showSaveDialog.value = false
    toast.add({ severity: 'success', summary: SAVE_SUCCESS_SUMMARY, detail: SAVE_SUCCESS_DETAIL, life: TOAST_LIFE_NORMAL })
  } catch (error) {
    console.error(LOG_SAVE_ERROR_PREFIX, error)
    toast.add({ severity: 'error', summary: SAVE_FAILED_SUMMARY, detail: error instanceof Error ? error.message : GENERIC_SAVE_FAILED, life: TOAST_LIFE_LONG })
  }
}

const handleCopyBuildCode = async () => {
  if (!buildCode.value) return
  try {
    await navigator.clipboard.writeText(buildCode.value)
    toast.add({ severity: 'success', summary: COPY_SUCCESS_SUMMARY, detail: COPY_SUCCESS_DETAIL, life: TOAST_LIFE_SHORT })
  } catch (error) {
    console.error(LOG_COPY_ERROR_PREFIX, error)
    toast.add({ severity: 'error', summary: COPY_FAILED_SUMMARY, detail: COPY_FAILED_DETAIL, life: TOAST_LIFE_NORMAL })
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
