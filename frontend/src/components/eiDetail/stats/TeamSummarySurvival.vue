<template>
  <div class="stat-card survival">
    <div class="stat-icon">
      <i class="pi pi-shield" />
    </div>
    <div class="stat-content">
      <div class="stat-label">
        生存数据
      </div>
      <div class="stat-values">
        <span class="down">
          <i class="pi pi-exclamation-triangle" />
          {{ totalDowns }}
        </span>
        <span class="death">
          <i class="pi pi-times" />
          {{ totalDeaths }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  totalDowns: number
  totalDeaths: number
}

defineProps<Props>()
</script>

<style scoped lang="css">
.stat-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--color-card-hover);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--color-accent-alpha-30);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--color-shadow);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  flex-shrink: 0;
}

.stat-card.survival .stat-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.25rem;
}

.stat-values {
  display: flex;
  gap: 1rem;
}

.stat-values span {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}
</style>
