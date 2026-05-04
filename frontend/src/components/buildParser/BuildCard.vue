<template>
  <div class="build-card">
    <!-- 头部：职业图标和Meta标记 -->
    <div class="build-card-header">
      <div
        class="profession-badge"
        :style="{ backgroundColor: professionColor }"
      >
        <span class="profession-initial">{{ professionInitial }}</span>
      </div>
      <div class="flex items-center gap-2">
        <Tag
          v-if="build.isMeta"
          severity="success"
        >
          Meta
        </Tag>
        <Tag :severity="roleSeverity">
          {{ roleLabel }}
        </Tag>
      </div>
    </div>

    <!-- 标题和描述 -->
    <div class="build-card-content">
      <h3 class="build-title">{{ build.title }}</h3>
      <p class="build-subtitle">
        {{ professionLabel }}
        <span v-if="build.eliteSpec"> · {{ build.eliteSpec }}</span>
      </p>

      <!-- 快速信息 -->
      <div class="build-info">
        <div v-if="build.armorType" class="info-item">
          <i class="pi pi-shield"></i>
          <span>{{ armorTypeLabel }}</span>
        </div>
        <div v-if="build.rune" class="info-item">
          <i class="pi pi-star"></i>
          <span>{{ build.rune }}</span>
        </div>
        <div v-if="build.weapons && build.weapons.length > 0" class="info-item">
          <i class="pi pi-swords"></i>
          <span>{{ build.weapons.length }}套武器</span>
        </div>
      </div>
    </div>

    <!-- 底部：操作按钮 -->
    <div class="build-card-footer">
      <div class="build-date">
        <i class="pi pi-calendar"></i>
        <span>{{ formatDate(build.updatedAt) }}</span>
      </div>
      <div class="flex gap-2">
        <Button
          v-if="build.bdCode"
          icon="pi pi-copy"
          class="btn-ghost btn-sm"
          @click.stop="handleCopyCode"
        />
        <Button
          icon="pi pi-eye"
          class="btn-ghost btn-sm"
          @click.stop="handleView"
        />
        <Button
          icon="pi pi-pencil"
          class="btn-ghost btn-sm"
          @click.stop="handleEdit"
        />
        <Button
          icon="pi pi-trash"
          class="btn-ghost btn-sm btn-danger"
          @click.stop="handleDelete"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Build卡片组件
 * 功能：展示单个Build配置的概要信息
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

import { computed } from 'vue';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import type { BuildEntry } from '@/types/buildLibrary';

// Props
const props = defineProps<{
  build: BuildEntry;
}>();

// Emits
const emit = defineEmits<{
  'view': [build: BuildEntry];
  'edit': [build: BuildEntry];
  'delete': [buildId: string];
  'copy': [build: BuildEntry];
}>();

// 职业颜色映射
const professionColors: Record<string, string> = {
  Warrior: '#E85D04',
  Guardian: '#FAA307',
  Revenant: '#9D4EDD',
  Ranger: '#06D6A0',
  Engineer: '#7B8FA1',
  Necromancer: '#8D0801',
  Mesmer: '#4361EE',
  Elementalist: '#FF6B6B'
};

// 职业名称映射
const professionLabels: Record<string, string> = {
  Warrior: '战士',
  Guardian: '守护者',
  Revenant: '魂武者',
  Ranger: '游侠',
  Engineer: '工程师',
  Necromancer: '唤灵师',
  Mesmer: '幻术师',
  Elementalist: '元素使'
};

// 护甲类型映射
const armorTypeLabels: Record<string, string> = {
  Heavy: '重甲',
  Medium: '中甲',
  Light: '轻甲'
};

// 计算属性
const professionColor = computed(() => {
  return professionColors[props.build.profession] || '#6C757D';
});

const professionInitial = computed(() => {
  return props.build.profession.charAt(0).toUpperCase();
});

const professionLabel = computed(() => {
  return professionLabels[props.build.profession] || props.build.profession;
});

const roleLabel = computed(() => {
  return props.build.role === 'dps' ? 'DPS' : '辅助';
});

const roleSeverity = computed(() => {
  return props.build.role === 'dps' ? 'danger' : 'success';
});

const armorTypeLabel = computed(() => {
  return armorTypeLabels[props.build.armorType] || props.build.armorType;
});

// 方法
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const handleView = () => {
  emit('view', props.build);
};

const handleEdit = () => {
  emit('edit', props.build);
};

const handleDelete = () => {
  emit('delete', props.build.id);
};

const handleCopyCode = () => {
  emit('copy', props.build);
};
</script>

<style scoped lang="postcss">
.build-card {
  @apply bg-neutral-900 rounded-xl border border-neutral-800 overflow-hidden hover:border-neutral-700 transition-colors;
}

.build-card-header {
  @apply flex items-center justify-between p-4 border-b border-neutral-800;
}

.profession-badge {
  @apply w-10 h-10 rounded-full flex items-center justify-center;
}

.profession-initial {
  @apply text-white font-bold text-lg;
}

.build-card-content {
  @apply p-4;
}

.build-title {
  @apply text-lg font-semibold text-neutral-text mb-1;
}

.build-subtitle {
  @apply text-sm text-neutral-text-secondary mb-3;
}

.build-info {
  @apply flex flex-wrap gap-3;
}

.info-item {
  @apply flex items-center gap-1 text-sm text-neutral-text-secondary;
}

.build-card-footer {
  @apply flex items-center justify-between p-4 bg-neutral-bg-secondary border-t border-neutral-800;
}

.build-date {
  @apply flex items-center gap-1 text-xs text-neutral-text-secondary;
}

.btn-sm {
  @apply w-8 h-8 p-0 flex items-center justify-center;
}

.btn-danger {
  @apply text-red-500 hover:bg-red-500/10;
}
</style>