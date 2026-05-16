<template>
  <div class="card-header">
    <div class="header-title">
      <i class="pi pi-users" />
      <span>团队统计</span>
    </div>
    <div class="header-badge">
      {{ playerCount }} 名玩家
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  playerCount: number
}

defineProps<Props>()
</script>

<style scoped lang="css">
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.header-title i {
  color: var(--color-accent);
}

.header-badge {
  padding: 0.25rem 0.75rem;
  background-color: var(--color-accent-alpha-10);
  color: var(--color-accent);
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
