<template>
  <div class="overview-cards">
    <div v-for="card in cards" :key="card.label" class="overview-card">
      <div class="card-icon" :class="card.type">
        <i :class="card.icon" />
      </div>
      <div class="card-content">
        <span class="card-value">{{ card.value }}</span>
        <span class="card-label">{{ card.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  dictDataLength: number
  enabledCount: number
  disabledCount: number
  dictTypesLength: number
}>()

const cards = computed(() => [
  { label: '当前页数据', value: props.dictDataLength, icon: 'pi pi-list', type: 'primary' },
  { label: '启用数量', value: props.enabledCount, icon: 'pi pi-check-circle', type: 'success' },
  { label: '禁用数量', value: props.disabledCount, icon: 'pi pi-ban', type: 'warning' },
  { label: '分类总数', value: props.dictTypesLength, icon: 'pi pi-sitemap', type: 'info' }
])
</script>

<style scoped>
.overview-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.overview-card {
  background: #2a2a2a; border-radius: 12px; padding: 16px;
  display: flex; align-items: center; gap: 16px;
}
.card-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
}
.card-icon.primary { background: rgba(22, 93, 255, 0.2); color: #165dff; }
.card-icon.success { background: rgba(38, 191, 99, 0.2); color: #26bf63; }
.card-icon.warning { background: rgba(255, 125, 0, 0.2); color: #ff7d00; }
.card-icon.info { background: rgba(0, 200, 150, 0.2); color: #00c896; }
.card-content { display: flex; flex-direction: column; gap: 4px; }
.card-value { font-size: 24px; font-weight: 700; color: #e5e5e5; }
.card-label { font-size: 12px; color: #909399; }
</style>
