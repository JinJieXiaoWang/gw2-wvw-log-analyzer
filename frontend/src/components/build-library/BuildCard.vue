<template>
  <div
    class="build-card relative group cursor-pointer overflow-hidden rounded-2xl border transition-all duration-300"
    :class="{
      'hover:shadow-xl hover:-translate-y-1 hover:border-neutral-border-hover': true,
      'ring-1 ring-primary/20': build.isMeta
    }"
    :style="{
      borderLeftWidth: '4px',
      borderLeftColor: build.professionColor,
      backgroundColor: 'var(--color-card)'
    }"
    @click="$emit('select', build)"
  >
    <!-- META 角标 -->
    <div v-if="build.isMeta" class="absolute top-0 right-0 z-10">
      <div
        class="text-xs font-bold px-3 py-1 rounded-bl-xl"
        :style="{ backgroundColor: build.professionColor + '25', color: build.professionColor }"
      >
        META
      </div>
    </div>

    <div class="p-5">
      <!-- 头部：图标 + 标题 -->
      <div class="flex items-center gap-3.5 mb-3">
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-base flex-shrink-0 shadow-md"
          :style="{ backgroundColor: build.professionColor }"
        >
          {{ professionInitial }}
        </div>
        <div class="flex-1 min-w-0">
          <h3
            class="text-base font-bold text-neutral-text leading-snug truncate group-hover:text-primary transition-colors"
          >
            {{ displayTitle }}
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-1 truncate">
            {{ professionLabel }}
            <span v-if="build.eliteSpec"> · {{ build.eliteSpec }}</span>
          </p>
        </div>
      </div>

      <!-- 职责标签 -->
      <div class="flex flex-wrap gap-1.5 mb-3">
        <span
          class="inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold"
          :class="
            build.role === 'dps'
              ? 'bg-status-error/12 text-status-error'
              : 'bg-status-success/12 text-status-success'
          "
        >
          {{ build.role === 'dps' ? '输出' : '辅助' }}
        </span>
        <span
          v-for="sub in build.subRoles"
          :key="sub"
          class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-primary/10 text-primary"
        >
          {{ subRoleLabel(sub) }}
        </span>
        <span
          v-if="build.armorType"
          class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-neutral-bg text-neutral-text-secondary"
        >
          {{ armorTypeShort }}
        </span>
      </div>

      <!-- 武器行 -->
      <div
        v-if="build.weapons && build.weapons.length > 0"
        class="flex items-center gap-2 mb-3 text-sm text-neutral-text-secondary"
      >
        <i class="pi pi-swords text-xs text-neutral-text-disabled" />
        <span class="truncate">{{ weaponsDisplay }}</span>
      </div>

      <!-- 底部信息行 -->
      <div class="flex items-center justify-between pt-3 border-t border-neutral-border/50">
        <span class="text-xs text-neutral-text-disabled">{{ formatDate(build.updatedAt) }}</span>
        <div class="flex items-center gap-1">
          <button
            class="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-text-secondary hover:text-primary hover:bg-primary/10 transition-all"
            title="复制Build代码"
            @click.stop="$emit('copy-code', build)"
          >
            <i class="pi pi-copy text-xs" />
          </button>
          <button
            class="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-text-secondary hover:text-primary hover:bg-primary/10 transition-all"
            title="查看详情"
          >
            <i class="pi pi-eye text-xs" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BuildEntry } from '@/types/buildLibrary'

interface Props {
  build: BuildEntry
}

const props = defineProps<Props>()
defineEmits<{
  'copy-code': [build: BuildEntry]
  'select': [build: BuildEntry]
}>()

const professionInitial = computed(() => {
  const map: Record<string, string> = {
    Elementalist: '元',
    Engineer: '工',
    Guardian: '守',
    Mesmer: '幻',
    Necromancer: '死',
    Ranger: '游',
    Revenant: '魂',
    Warrior: '战'
  }
  return map[props.build.profession] || props.build.profession.charAt(0)
})

const professionLabel = computed(() => {
  const map: Record<string, string> = {
    Elementalist: '元素使',
    Engineer: '工程师',
    Guardian: '守护者',
    Mesmer: '幻术师',
    Necromancer: '唤灵师',
    Ranger: '游侠',
    Revenant: '魂武者',
    Warrior: '战士'
  }
  return map[props.build.profession] || props.build.profession
})

const displayTitle = computed(() => {
  const t = props.build.title
  // 去掉前缀编号如 "1.1、" "8、"
  const cleaned = t.replace(/^\d+[.\d]*、/, '').replace(/^\d+、/, '')
  // 如果 eliteSpec 存在且标题中包含它，优先显示 eliteSpec
  if (props.build.eliteSpec && cleaned.includes(props.build.eliteSpec)) {
    return props.build.eliteSpec
  }
  // 截取括号前的部分
  const bracketIdx = cleaned.indexOf('（')
  if (bracketIdx > 0) return cleaned.slice(0, bracketIdx)
  return cleaned
})

const subRoleLabel = (sub: string): string => {
  const map: Record<string, string> = { boon: '增益', heal: '治疗', tank: '承伤', cc: '削控' }
  return map[sub] || sub
}

const armorTypeShort = computed(() => {
  const type = props.build.armorType
  if (type.includes('狂战')) return '狂战士'
  if (type.includes('吟游')) return '吟游诗人'
  if (type.includes('游荡')) return '游荡者'
  if (type.includes('天界')) return '天界'
  return type.length > 6 ? type.slice(0, 6) + '..' : type
})

const weaponsDisplay = computed(() => {
  return props.build.weapons
    .map((w) => w.name)
    .filter(Boolean)
    .join(' / ')
})

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>

<style scoped>
.build-card {
  border-color: var(--color-border);
}
.build-card:hover {
  border-color: var(--color-border-hover);
}
</style>
