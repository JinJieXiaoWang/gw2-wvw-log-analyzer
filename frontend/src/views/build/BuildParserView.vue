<template>
  <div class="build-parser-view">
    <!-- 页面头部 -->
    <PageHeader
      title="Build解析"
      subtitle="解析并管理你的GW2 Build配置"
      icon="pi pi-code"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <!-- 主要内容 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <!-- 左侧：Build代码输入区 -->
      <div class="lg:col-span-1">
        <BuildCodeInput
          v-model:build-code="buildCode"
          :is-parsing="isParsing"
          :parse-error="parseError"
          @parse-build-code="handleParseBuildCode"
          @show-import-dialog="showImportDialog = true"
          @clear-code="handleClearCode"
        />

        <!-- 保存对话框 -->
        <SaveDialog
          v-model:visible="showSaveDialog"
          :parsed-data="parsedData"
          :build-code="buildCode"
          @save="handleSaveBuild"
        />

        <!-- 导入对话框 -->
        <ImportDialog
          v-model:visible="showImportDialog"
          @import-build-code="handleImportBuildCode"
        />
      </div>

      <!-- 右侧：解析结果展示区 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 解析结果头部 -->
        <div v-if="parsedData" class="card">
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

        <!-- 特性配置 -->
        <div v-if="parsedData" class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">特性配置</h3>
          <div class="space-y-4">
            <div
              v-for="spec in parsedData.specializations"
              :key="spec.id"
              class="p-4 bg-neutral-800 rounded-lg"
            >
              <div class="flex items-center gap-3 mb-3">
                <img
                  v-if="spec.icon"
                  :src="cleanIconUrl(spec.icon)"
                  :alt="spec.name_cn"
                  class="w-8 h-8 rounded"
                />
                <div>
                  <span class="text-neutral-text font-medium">{{ spec.name_cn }}</span>
                  <span
                    v-if="spec.is_elite"
                    class="ml-2 text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-500 rounded"
                  >
                    精英特长
                  </span>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-2">
                <div
                  v-for="trait in spec.traits"
                  :key="trait.id"
                  class="p-3 rounded-lg"
                  :class="trait.is_selected ? 'bg-primary/20 border border-primary/50' : 'bg-neutral-700/50'"
                >
                  <div class="flex items-center gap-2 mb-1">
                    <img
                      v-if="trait.icon"
                      :src="cleanIconUrl(trait.icon)"
                      :alt="trait.name"
                      class="w-4 h-4 rounded"
                    />
                    <span
                      class="text-sm font-medium"
                      :class="trait.is_selected ? 'text-primary' : 'text-neutral-text-secondary'"
                    >
                      {{ trait.name }}
                    </span>
                  </div>
                  <p class="text-xs text-neutral-text-secondary line-clamp-2">{{ trait.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 技能配置 -->
        <div v-if="parsedData" class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">技能配置</h3>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- 治疗技能 -->
            <div class="text-center">
              <div class="text-sm text-neutral-text-secondary mb-2">治疗</div>
              <div class="w-20 h-20 mx-auto bg-neutral-800 rounded-lg flex flex-col items-center justify-center p-2">
                <img
                  v-if="parsedData.skills.heal?.icon"
                  :src="cleanIconUrl(parsedData.skills.heal.icon)"
                  :alt="parsedData.skills.heal.name_cn"
                  class="w-10 h-10 rounded mb-1"
                />
                <span class="text-xs text-neutral-text">{{ parsedData.skills.heal?.name_cn || '未配置' }}</span>
              </div>
              <p class="text-xs text-neutral-text-secondary mt-2">{{ parsedData.skills.heal?.recharge }}s CD</p>
            </div>

            <!-- 通用技能 -->
            <div class="col-span-2">
              <div class="text-sm text-neutral-text-secondary mb-2">通用</div>
              <div class="flex gap-2 justify-center">
                <div
                  v-for="(skill, index) in parsedData.skills.utility"
                  :key="index"
                  class="w-20 h-20 bg-neutral-800 rounded-lg flex flex-col items-center justify-center p-2"
                >
                  <img
                    v-if="skill.icon"
                    :src="cleanIconUrl(skill.icon)"
                    :alt="skill.name_cn"
                    class="w-10 h-10 rounded mb-1"
                  />
                  <span class="text-xs text-neutral-text">{{ skill.name_cn }}</span>
                </div>
              </div>
              <div class="flex gap-2 justify-center mt-1">
                <span
                  v-for="(skill, index) in parsedData.skills.utility"
                  :key="index"
                  class="w-20 text-center"
                >
                  <span class="text-xs text-neutral-text-secondary">{{ skill.recharge }}s</span>
                </span>
              </div>
            </div>

            <!-- 精英技能 -->
            <div class="text-center">
              <div class="text-sm text-neutral-text-secondary mb-2">精英</div>
              <div class="w-20 h-20 mx-auto bg-neutral-800 rounded-lg flex flex-col items-center justify-center p-2 border border-yellow-500/30">
                <img
                  v-if="parsedData.skills.elite?.icon"
                  :src="cleanIconUrl(parsedData.skills.elite.icon)"
                  :alt="parsedData.skills.elite.name_cn"
                  class="w-10 h-10 rounded mb-1"
                />
                <span class="text-xs text-neutral-text">{{ parsedData.skills.elite?.name_cn || '未配置' }}</span>
              </div>
              <p class="text-xs text-neutral-text-secondary mt-2">{{ parsedData.skills.elite?.recharge }}s CD</p>
            </div>
          </div>
        </div>

        <!-- BD码显示 -->
        <div v-if="parsedData" class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">BD码</h3>
          <div class="p-4 bg-neutral-800 rounded-lg font-mono text-sm">
            <code>{{ parsedData.bd_code }}</code>
          </div>
        </div>

        <!-- 无解析结果时的提示 -->
        <div v-else class="card text-center py-12">
          <i class="pi pi-code text-5xl text-neutral-text-secondary mb-4 opacity-50"></i>
          <h3 class="text-lg font-semibold text-neutral-text mb-2">输入Build代码开始解析</h3>
          <p class="text-neutral-text-secondary">
            粘贴你的GW2 Build代码（如 [&DQgBAAA=]），点击解析按钮即可
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Build解析页面
 * 功能：解析GW2 Build代码并展示详细信息
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import PageHeader from '@/components/common/layout/PageHeader.vue';
import BuildCodeInput from '@/components/build/parser/BuildCodeInput.vue';
import ImportDialog from '@/components/build/parser/ImportDialog.vue';
import SaveDialog from '@/components/build/parser/SaveDialog.vue';
import buildApi from '@/api/build/build';


// Toast 服务
const toast = useToast();

// 状态
const buildCode = ref('');
const isParsing = ref(false);
const parseError = ref('');
const parsedData = ref<any>(null);
const showSaveDialog = ref(false);
const showImportDialog = ref(false);

// 计算属性：获取精英特长名称
const eliteSpecName = computed(() => {
  if (!parsedData.value?.specializations) return '';
  const eliteSpec = parsedData.value.specializations.find(spec => spec.is_elite);
  return eliteSpec?.name_cn || '';
});

// 职业颜色映射
const getProfessionColor = (profession: string) => {
  const colors: Record<string, string> = {
    Warrior: '#E85D04',
    Guardian: '#FAA307',
    Revenant: '#9D4EDD',
    Ranger: '#06D6A0',
    Engineer: '#7B8FA1',
    Necromancer: '#8D0801',
    Mesmer: '#4361EE',
    Elementalist: '#FF6B6B'
  };
  return colors[profession] || '#6C757D';
};

// 获取职业首字母
const getProfessionInitial = (profession: string) => {
  return profession.charAt(0).toUpperCase();
};

// 清理图标URL（移除可能的引号和空格）
const cleanIconUrl = (iconUrl: string): string => {
  if (!iconUrl) return '';
  return iconUrl.trim().replace(/^[`'"]+|[`'"]+$/g, '');
};

// 解析Build代码
const handleParseBuildCode = async () => {
  if (!buildCode.value.trim()) {
    parseError.value = '请输入Build代码';
    return;
  }

  // 验证代码格式
  const codePattern = /^\[&[A-Za-z0-9+/=]+\]$/;
  if (!codePattern.test(buildCode.value.trim())) {
    parseError.value = 'Build代码格式不正确，应为 [&...] 格式';
    return;
  }

  isParsing.value = true;
  parseError.value = '';

  try {
    const result = await buildApi.parseBuildCode(buildCode.value.trim());

    if (result) {
      parsedData.value = result;
      toast.add({
        severity: 'success',
        summary: '解析成功',
        detail: 'Build代码解析完成',
        life: 3000
      });
    } else {
      parseError.value = '解析失败，请稍后重试';
    }
  } catch (error) {
    console.error('解析Build代码失败:', error);
    parseError.value = error instanceof Error ? error.message : '解析失败';
    toast.add({
      severity: 'error',
      summary: '解析失败',
      detail: parseError.value,
      life: 5000
    });
  } finally {
    isParsing.value = false;
  }
};

// 清空代码
const handleClearCode = () => {
  buildCode.value = '';
  parsedData.value = null;
  parseError.value = '';
};

// 导入Build代码
const handleImportBuildCode = (code: string) => {
  buildCode.value = code;
  showImportDialog.value = false;
};

// 保存Build
const handleSaveBuild = async (buildData: any) => {
  try {
    await buildApi.saveBuild(buildData);
    showSaveDialog.value = false;
    toast.add({
      severity: 'success',
      summary: '保存成功',
      detail: 'Build配置已保存',
      life: 3000
    });
  } catch (error) {
    console.error('保存Build失败:', error);
    toast.add({
      severity: 'error',
      summary: '保存失败',
      detail: error instanceof Error ? error.message : '保存失败',
      life: 5000
    });
  }
};

// 复制Build代码
const handleCopyBuildCode = async () => {
  if (!buildCode.value) return;

  try {
    await navigator.clipboard.writeText(buildCode.value);
    toast.add({
      severity: 'success',
      summary: '复制成功',
      detail: 'Build代码已复制到剪贴板',
      life: 2000
    });
  } catch (error) {
    console.error('复制失败:', error);
    toast.add({
      severity: 'error',
      summary: '复制失败',
      detail: '无法复制到剪贴板',
      life: 3000
    });
  }
};
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