<template>
  <div class="section-header">
    <h2 class="section-title">
      <i class="pi pi-heart" />
      {{ HEALING_SECTION_TITLE }}
    </h2>
    <div class="section-subtitle">
      {{ HEALING_SECTION_SUBTITLE }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { HEALING_SECTION_TITLE, HEALING_SECTION_SUBTITLE } from '@/constants/eiLabels'
</script>

<style scoped lang="css">
.section-header {
  margin-bottom: 1rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
}

.section-title i {
  color: var(--color-accent);
}

.section-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}
</style>
