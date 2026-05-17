<template>
  <div
    v-if="isExternalResult"
    :style="styleExternalIcon"
    class="svg-external-icon svg-icon"
    v-bind="$attrs"
  />
  <svg
    v-else
    :class="svgClass"
    aria-hidden="true"
    v-bind="$attrs"
  >
    <use :xlink:href="iconName" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  iconClass?: string
  className?: string
  icon?: string
  size?: number | 'xs' | 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  className: '',
  icon: '',
  size: 'md'
})

const iconClass = computed(() => props.iconClass || props.icon || '')

const isExternalResult = computed(() => {
  const value = iconClass.value
  return /^(https?:|data:)/.test(value)
})

const iconName = computed(() => `#icon-${iconClass.value}`)

const svgClass = computed(() => {
  const classes: string[] = ['svg-icon']
  
  if (props.className) {
    classes.push(props.className)
  }
  
  if (typeof props.size === 'string') {
    classes.push(`svg-icon--${props.size}`)
  }
  
  return classes.join(' ')
})

const styleExternalIcon = computed(() => ({
  mask: `url(${iconClass.value}) no-repeat 50% 50%`,
  '-webkit-mask': `url(${iconClass.value}) no-repeat 50% 50%`
}))
</script>

<style scoped>
.svg-icon {
  width: 1em;
  height: 1em;
  vertical-align: -0.15em;
  fill: currentColor;
  overflow: hidden;
}

.svg-external-icon {
  background-color: currentColor;
  mask-size: cover!important;
  display: inline-block;
}

.svg-icon--xs {
  width: 12px;
  height: 12px;
}

.svg-icon--sm {
  width: 16px;
  height: 16px;
}

.svg-icon--md {
  width: 20px;
  height: 20px;
}

.svg-icon--lg {
  width: 24px;
  height: 24px;
}

.svg-icon--xl {
  width: 32px;
  height: 32px;
}
</style>