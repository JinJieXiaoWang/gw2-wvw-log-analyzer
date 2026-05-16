<template>
  <div class="overview-cards">
    <div
      v-for="card in cards"
      :key="card.label"
      class="overview-card"
    >
      <div
        class="card-icon"
        :class="card.type"
      >
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
import { computed } from 'vue';

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
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.overview-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  min-height: 80px;
}
.overview-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}
.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}
.card-icon.primary {
  background: var(--color-primary-alpha-10);
  color: var(--color-primary);
}
.card-icon.success {
  background: var(--color-success-alpha-10);
  color: var(--color-success);
}
.card-icon.warning {
  background: var(--color-warning-alpha-10);
  color: var(--color-warning);
}
.card-icon.info {
  background: var(--color-info-alpha-10);
  color: var(--color-info);
}
.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}
.card-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
}
.card-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

@media (max-width: 1024px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }
}
</style>
