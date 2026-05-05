<template>
  <div class="commander-cheatsheet">
    <div
      v-if="commands && commands.length > 0"
      class="overflow-hidden rounded-xl border border-neutral-border"
    >
      <table class="w-full">
        <thead>
          <tr class="bg-neutral-bg/80">
            <th class="text-left px-4 py-3 text-xs font-bold text-neutral-text-secondary uppercase tracking-wide w-28">
              口令
            </th>
            <th class="text-left px-4 py-3 text-xs font-bold text-neutral-text-secondary uppercase tracking-wide">
              操作
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(cmd, idx) in commands"
            :key="idx"
            class="border-t border-neutral-border/40 hover:bg-neutral-bg/20 transition-colors"
          >
            <td class="px-4 py-3 align-top">
              <span
                class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold"
                :class="calloutClass(cmd.callout)"
              >
                {{ cmd.callout }}
              </span>
            </td>
            <td class="px-4 py-3 text-neutral-text text-base">
              {{ cmd.action }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-else
      class="text-center py-8 text-neutral-text-secondary"
    >
      <i class="pi pi-microphone-slash text-3xl mb-2 opacity-40" />
      <p class="text-sm">
        暂无指挥口令
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BuildRotationCommand } from '@/types/buildLibrary'

interface Props {
  commands: BuildRotationCommand[]
}

defineProps<Props>()

const calloutClass = (callout: string): string => {
  const lower = callout.toLowerCase()
  if (lower.includes('炸火')) return 'bg-status-error/15 text-status-error'
  if (lower.includes('石板路')) return 'bg-status-warning/15 text-status-warning'
  if (lower.includes('削拉') || lower.includes('削控')) return 'bg-rarity-legendary/15 text-rarity-legendary'
  if (lower.includes('补稳') || lower.includes('稳固')) return 'bg-status-success/15 text-status-success'
  if (lower.includes('开刷') || lower.includes('刷')) return 'bg-primary/15 text-primary'
  if (lower.includes('格挡')) return 'bg-tech-cyan/15 text-tech-cyan'
  if (lower.includes('抗性')) return 'bg-info/15 text-info'
  if (lower.includes('急速') || lower.includes('豆子')) return 'bg-secondary/15 text-secondary'
  return 'bg-neutral-bg text-neutral-text-secondary border border-neutral-border'
}
</script>
