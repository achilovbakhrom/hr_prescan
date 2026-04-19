<script setup lang="ts">
import { computed } from 'vue'

type Size = 'xs' | 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    logo?: string | null
    name?: string | null
    size?: Size
    rounded?: 'md' | 'lg' | 'xl'
  }>(),
  { size: 'md', rounded: 'lg', name: '' },
)

// Treat null/undefined/empty-string uniformly as "no logo".
const resolvedLogo = computed(() => (props.logo && props.logo.length > 0 ? props.logo : null))
const resolvedName = computed(() => props.name ?? '')

const boxClass = computed(() => {
  const sizeClass = {
    xs: 'h-6 w-6',
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  }[props.size]
  const roundedClass = `rounded-${props.rounded}`
  return `${sizeClass} ${roundedClass}`
})

const iconClass = computed(
  () =>
    ({
      xs: 'text-[10px]',
      sm: 'text-sm',
      md: 'text-lg',
      lg: 'text-xl',
    })[props.size],
)
</script>

<template>
  <div
    v-if="resolvedLogo"
    :class="[
      boxClass,
      'flex shrink-0 items-center justify-center overflow-hidden bg-gray-100',
    ]"
  >
    <img :src="resolvedLogo" :alt="resolvedName" class="h-full w-full object-contain" />
  </div>
  <div
    v-else
    :class="[
      boxClass,
      'flex shrink-0 items-center justify-center bg-blue-50 text-blue-600',
    ]"
    role="img"
    :aria-label="resolvedName || 'Company'"
  >
    <i class="pi pi-building" :class="iconClass" aria-hidden="true"></i>
  </div>
</template>
