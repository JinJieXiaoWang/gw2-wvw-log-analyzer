<template>
  <Drawer
    :visible="visible"
    position="right"
    :modal="true"
    :dismissable="true"
    :pt="{ root: { style: { width: '920px' } } }"
    @update:visible="$emit('update:visible', $event)"
  >
    <template v-if="build">
      <div class="flex items-start gap-5 mb-6">
        <div
          class="w-16 h-16 rounded-2xl flex items-center justify-center text-white font-bold text-xl flex-shrink-0 shadow-lg"
          :style="{ backgroundColor: build.professionColor }"
        >
          {{ professionInitial(build.profession) }}
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="text-xl font-bold leading-snug">
            {{ build.title }}
          </h2>
          <p class="text-sm text-surface-400 mt-1">
            {{ build.role === 'dps' ? '输出' : '辅助' }} ·
            {{ build.eliteSpec ? getProfessionName(build.eliteSpec) : '核心职业' }}
          </p>
          <div class="flex flex-wrap gap-2 mt-3">
            <Tag
              :value="build.role === 'dps' ? '输出' : '辅助'"
              :severity="build.role === 'dps' ? 'danger' : 'success'"
              class="text-sm font-semibold"
            />
            <Tag
              v-for="sub in build.subRoles"
              :key="sub"
              :value="subRoleLabel(sub)"
              severity="info"
              class="text-sm"
            />
            <Tag
              v-if="build.isMeta"
              value="META"
              severity="success"
              class="text-sm font-bold"
            />
          </div>
        </div>
      </div>

      <Divider />

      <Panel
        header="配装"
        class="mb-4"
        toggleable
      >
        <template #icons>
          <i class="pi pi-shield text-primary" />
        </template>
        <GearOverviewCard :build="build" />
      </Panel>

      <Panel
        header="Build 代码"
        class="mb-4"
        toggleable
      >
        <template #icons>
          <i class="pi pi-code text-primary" />
        </template>
        <div
          class="p-4 rounded-lg bg-surface-900 font-mono text-sm break-all mb-4 leading-relaxed border border-surface-700"
        >
          {{ build.bdCode }}
        </div>
        <div class="flex gap-3">
          <Button
            icon="pi pi-copy"
            label="复制代码"
            size="small"
            @click="$emit('copyCode', build)"
          />
          <router-link
            :to="{ path: '/build-parser', query: { code: build.bdCode } }"
            class="no-underline"
          >
            <Button
              icon="pi pi-external-link"
              label="在解析器中打开"
              size="small"
              outlined
            />
          </router-link>
        </div>
      </Panel>

      <Panel
        v-if="build.traitLines?.length"
        header="特性"
        class="mb-4"
        toggleable
      >
        <template #icons>
          <i class="pi pi-sitemap text-rarity-legendary" />
        </template>
        <div class="space-y-3">
          <div
            v-for="(line, idx) in build.traitLines"
            :key="idx"
            class="flex items-center gap-4 p-3 rounded-lg bg-surface-900 border border-surface-700"
          >
            <span class="text-base font-semibold min-w-[100px]">{{ line.name }}</span>
            <div class="flex gap-2">
              <Tag
                v-for="(choice, cIdx) in line.choices"
                :key="cIdx"
                :value="String(choice)"
                :severity="['danger', 'warning', 'success'][cIdx]"
                class="text-sm font-bold w-9 h-9 flex items-center justify-center"
              />
            </div>
          </div>
        </div>
      </Panel>

      <Panel
        header="指挥口令速查"
        class="mb-4"
        toggleable
      >
        <template #icons>
          <i class="pi pi-microphone text-secondary" />
        </template>
        <CommanderCheatsheet :commands="build.rotationCommands" />
      </Panel>

      <Panel
        v-if="build.mechanics?.length"
        header="关键机制"
        class="mb-4"
        toggleable
      >
        <template #icons>
          <i class="pi pi-cog text-tech-cyan" />
        </template>
        <div class="space-y-3">
          <div
            v-for="mech in build.mechanics"
            :key="mech.name"
            class="p-4 rounded-lg bg-surface-900 border border-surface-700"
          >
            <div class="text-base font-semibold mb-2">
              {{ mech.name }}
            </div>
            <ul class="list-disc list-inside text-sm text-surface-400 space-y-1">
              <li
                v-for="source in mech.sources"
                :key="source"
              >
                {{ source }}
              </li>
            </ul>
          </div>
        </div>
      </Panel>

      <Panel
        v-if="build.videos?.length"
        header="参考视频"
        class="mb-4"
        toggleable
      >
        <template #icons>
          <i class="pi pi-video text-red-400" />
        </template>
        <div class="space-y-3">
          <a
            v-for="video in build.videos"
            :key="video.title"
            :href="video.url || '#'"
            class="flex items-center gap-4 p-4 rounded-lg bg-surface-900 border border-surface-700 hover:border-primary transition-colors group no-underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 bg-red-500/10">
              <i class="pi pi-play text-red-400" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-base font-medium truncate group-hover:text-primary transition-colors">{{ video.title }}</p>
              <p
                v-if="video.author"
                class="text-sm text-surface-400 mt-0.5"
              >{{ video.author }}</p>
            </div>
            <i class="pi pi-external-link text-surface-500" />
          </a>
        </div>
      </Panel>

      <Divider />

      <div class="text-sm text-surface-400 space-y-1">
        <p>作者：{{ build.author || '未知' }}</p>
        <p>更新：{{ formatFullDate(build.updatedAt) }}</p>
        <p>字数：{{ build.wordCount }}</p>
      </div>

      <div
        v-permission="'write'"
        class="flex gap-3 mt-6 pt-4 border-t border-surface-700"
      >
        <BaseButton
          icon="pi pi-pencil"
          label="编辑配置"
          severity="primary"
          outlined
          @click="$emit('edit')"
        />
        <BaseButton
          icon="pi pi-trash"
          label="删除配置"
          severity="danger"
          outlined
          @click="$emit('delete')"
        />
      </div>
    </template>
  </Drawer>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import type { BuildEntry } from '@/types/buildLibrary'
import { formatFullDate, professionInitial, subRoleLabel } from '@/utils/build/buildUtils'
import { getProfessionName } from '@/utils/profession/professionUtils'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import Drawer from 'primevue/drawer'
import Panel from 'primevue/panel'
import Tag from 'primevue/tag'
import CommanderCheatsheet from './CommanderCheatsheet.vue'
import GearOverviewCard from './GearOverviewCard.vue'

defineProps<{
  visible: boolean
  build: BuildEntry | null
}>()

defineEmits<{
  'update:visible': [boolean]
  copyCode: [BuildEntry]
  edit: []
  delete: []
}>()
</script>
