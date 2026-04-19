<script setup lang="ts">
/**
 * AdminStatTile — compact metric tile for admin dashboards.
 * Denser than DashboardStatsCard: smaller padding, smaller numbers, thinner glass.
 *
 * Spec: docs/design/spec.md §9 (admin = denser).
 */
import { computed } from 'vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'

type Accent = 'default' | 'ai' | 'celebrate' | 'success' | 'warning' | 'danger' | 'info'

interface Props {
  label: string
  value: string | number
  icon?: string
  accent?: Accent
}

const props = withDefaults(defineProps<Props>(), {
  icon: '',
  accent: 'default',
})

const iconClass = computed(() => {
  switch (props.accent) {
    case 'ai':
      return 'text-[color:var(--color-accent-ai)]'
    case 'celebrate':
      return 'text-[color:var(--color-accent-celebrate)]'
    case 'success':
      return 'text-[color:var(--color-success)]'
    case 'warning':
      return 'text-[color:var(--color-warning)]'
    case 'danger':
      return 'text-[color:var(--color-danger)]'
    case 'info':
      return 'text-[color:var(--color-info)]'
    default:
      return 'text-[color:var(--color-accent)]'
  }
})
</script>

<template>
  <GlassSurface level="1" class="admin-stat px-4 py-3">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0 flex-1">
        <p
          class="truncate font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--color-text-muted)]"
        >
          {{ label }}
        </p>
        <p
          class="mt-1 font-mono text-2xl font-semibold leading-none tracking-tight text-[color:var(--color-text-primary)]"
        >
          {{ value }}
        </p>
      </div>
      <i v-if="icon" :class="[icon, iconClass]" class="text-lg shrink-0"></i>
    </div>
  </GlassSurface>
</template>
