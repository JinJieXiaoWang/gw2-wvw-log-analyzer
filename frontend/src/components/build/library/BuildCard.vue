<template>
  <div
    class="build-card relative group cursor-pointer overflow-hidden rounded-2xl border transition-all duration-300"
    :class="{ 'hover:shadow-xl hover:-translate-y-1 hover:border-neutral-border-hover': true, 'ring-1 ring-primary/20': build.isMeta }"
    :style="{ borderLeftWidth: '4px', borderLeftColor: displayProfessionColor, backgroundColor: 'var(--color-card)' }"
    @click="$emit('select', build)"
  >
    <div
      v-if="build.isMeta"
      class="absolute top-0 right-0 z-10"
    >
      <div
        class="text-xs font-bold px-3 py-1 rounded-bl-xl"
        :style="{ backgroundColor: displayProfessionColor + '25', color: displayProfessionColor }"
      >
        META
      </div>
    </div>
    <div class="p-5">
      <div class="flex items-center gap-3.5 mb-3">
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-base flex-shrink-0 shadow-md"
          :style="{ backgroundColor: displayProfessionColor }"
        >
          {{ professionInitial }}
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="text-base font-bold text-neutral-text leading-snug truncate group-hover:text-primary transition-colors">
            {{ displayTitle }}
          </h3>
          <p class="text-sm text-neutral-text-secondary mt-1 truncate">
            {{ professionLabel }}
            <span v-if="build.eliteSpec"> · {{ getProfessionName(build.eliteSpec) }}</span>
          </p>
        </div>
      </div>

      <div class="flex flex-wrap gap-1.5 mb-3">
        <DictTag
          dict-type="role"
          :value="build.role"
          variant="badge"
          class="text-xs font-semibold"
        />
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

      <div
        v-if="build.weapons && build.weapons.length > 0"
        class="flex items-center gap-2 mb-3 text-sm text-neutral-text-secondary"
      >
        <i class="pi pi-swords text-xs text-neutral-text-disabled" /><span class="truncate">{{ weaponsDisplay }}</span>
      </div>
      <div
        v-if="build.rune"
        class="flex items-center gap-2 mb-3 text-sm text-neutral-text-secondary"
      >
        <i class="pi pi-star text-xs text-neutral-text-disabled" /><span class="truncate">{{ build.rune }}</span>
      </div>

      <div class="flex items-center justify-between pt-3 border-t border-neutral-border/50">
        <span class="text-xs text-neutral-text-disabled">{{ formatDate(build.updatedAt) }}</span>
        <div class="flex items-center gap-1">
          <button
            v-if="build.bdCode"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-text-secondary hover:text-primary hover:bg-primary/10 transition-all"
            title="复制Build代码"
            @click.stop="$emit('copy-code', build)"
          >
            <i class="pi pi-copy text-xs" />
          </button>
          <button
            v-permission="'write'"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-text-secondary hover:text-primary hover:bg-primary/10 transition-all"
            title="编辑配置"
            @click.stop="$emit('edit', build)"
          >
            <i class="pi pi-pencil text-xs" />
          </button>
          <button
            class="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-text-secondary hover:text-primary hover:bg-primary/10 transition-all"
            title="查看详情"
            @click.stop="$emit('select', build)"
          >
            <i class="pi pi-eye text-xs" />
          </button>
          <button
            v-if="showDelete"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-neutral-text-secondary hover:text-red-500 hover:bg-red-500/10 transition-all"
            title="删除配置"
            @click.stop="$emit('delete', build.id)"
          >
            <i class="pi pi-trash text-xs" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Build卡片组件
 * 功能：展示单个Build配置的概要信息，支持查看、编辑、复制、删除操作
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 * 更新日期：2026-05-10（合并两套BuildCard）
 */

import type { BuildEntry } from '@/types/buildLibrary'
import { getProfessionName, getProfessionColor } from '@/services/professionService'
import { computed } from 'vue'

interface Props {
  build: BuildEntry
  showDelete?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDelete: false
})

defineEmits<{
  'copy-code': [build: BuildEntry]
  'select': [build: BuildEntry]
  'edit': [build: BuildEntry]
  'delete': [buildId: string]
}>()

const professionInitialMap: Record<string, string> = {
  Warrior: '战',
  Guardian: '守',
  Revenant: '魂',
  Ranger: '游',
  Engineer: '工',
  Necromancer: '死',
  Mesmer: '幻',
  Elementalist: '元',
  Thief: '潜',
  Dragonhunter: '龙',
  Firebrand: '燃',
  Willbender: '破',
  Berserker: '狂',
  Spellbreaker: '破',
  Bladesworn: '誓',
  Scrapper: '机',
  Holosmith: '全',
  Mechanist: '机',
  Druid: '德',
  Soulbeast: '兽',
  Untamed: '野',
  Daredevil: '冒',
  Deadeye: '狙',
  Specter: '缚',
  Tempest: '风',
  Weaver: '编',
  Catalyst: '元',
  Chronomancer: '时',
  Mirage: '蜃',
  Virtuoso: '灵',
  Reaper: '夺',
  Scourge: '灾',
  Harbinger: '先',
  Herald: '预',
  Renegade: '叛',
  Vindicator: '裁'
}

const displayProfessionColor = computed(() => props.build.professionColor || getProfessionColor(props.build.profession))
const professionInitial = computed(() => professionInitialMap[props.build.profession] || props.build.profession.charAt(0))
const professionLabel = computed(() => getProfessionName(props.build.profession))

const displayTitle = computed(() => {
  const t = props.build.title
  const cleaned = t.replace(/^\d+[.\d]*、/, '').replace(/^\d+、/, '')
  if (props.build.eliteSpec && cleaned.includes(props.build.eliteSpec)) {
    return props.build.eliteSpec
  }
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
  if (type.includes('狂战士')) return '狂战士'
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
