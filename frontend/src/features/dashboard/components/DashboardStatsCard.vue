<script setup lang="ts">
/**
 * DashboardStatsCard — metric tile in Arc/Raycast style.
 * GlassCard wrapper with big Geist-Mono number, label, and optional delta.
 *
 * Spec: docs/design/spec.md §5, §9 (dashboard).
 */
import { computed } from 'vue'
import GlassCard from '@/shared/components/GlassCard.vue'

type Accent = 'default' | 'ai' | 'celebrate'
type DeltaDir = 'up' | 'down' | 'flat'

interface Props {
  label: string
  value: string | number
  icon?: string
  iconAccent?: Accent | 'info' | 'success' | 'warning' | 'danger'
  deltaLabel?: string
  deltaDir?: DeltaDir
  sublabel?: string
  cardAccent?: Accent
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  icon: '',
  iconAccent: 'default',
  deltaLabel: '',
  deltaDir: 'flat',
  sublabel: '',
  cardAccent: 'default',
  clickable: false,
})

defineEmits<{ (e: 'click'): void }>()

const iconBgClass = computed(() => {
  switch (props.iconAccent) {
    case 'ai':
      return 'bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]'
    case 'celebrate':
      return 'bg-[color:var(--color-accent-celebrate-soft)] text-[color:var(--color-accent-celebrate)]'
    case 'success':
      return 'bg-[color:color-mix(in_srgb,var(--color-success)_15%,transparent)] text-[color:var(--color-success)]'
    case 'warning':
      return 'bg-[color:color-mix(in_srgb,var(--color-warning)_18%,transparent)] text-[color:var(--color-warning)]'
    case 'danger':
      return 'bg-[color:color-mix(in_srgb,var(--color-danger)_15%,transparent)] text-[color:var(--color-danger)]'
    case 'info':
      return 'bg-[color:color-mix(in_srgb,var(--color-info)_15%,transparent)] text-[color:var(--color-info)]'
    default:
      return 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
  }
})

const deltaClass = computed(() => {
  if (props.deltaDir === 'up') return 'text-[color:var(--color-success)]'
  if (props.deltaDir === 'down') return 'text-[color:var(--color-danger)]'
  return 'text-[color:var(--color-text-muted)]'
})

const deltaIcon = computed(() => {
  if (props.deltaDir === 'up') return 'pi pi-arrow-up'
  if (props.deltaDir === 'down') return 'pi pi-arrow-down'
  return 'pi pi-minus'
})
</script>

<template>
  <GlassCard
    :accent="cardAccent"
    :class="[
      'stats-card h-full',
      clickable
        ? 'cursor-pointer transition-transform duration-[240ms] ease-ios motion-safe:hover:-translate-y-px'
        : '',
    ]"
    @click="clickable ? $emit('click') : null"
  >
    <div class="flex items-start justify-between gap-3">
      <div
        v-if="icon"
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[--radius-sm]"
        :class="iconBgClass"
      >
        <i :class="icon" class="text-lg"></i>
      </div>
      <div v-if="deltaLabel" class="flex items-center gap-1 text-xs font-mono" :class="deltaClass">
        <i :class="deltaIcon" class="text-[10px]"></i>
        <span>{{ deltaLabel }}</span>
      </div>
    </div>
    <div class="mt-4">
      <div
        class="font-mono text-4xl font-semibold leading-none tracking-tight text-[color:var(--color-text-primary)]"
      >
        {{ value }}
      </div>
      <p class="mt-2 text-sm font-medium text-[color:var(--color-text-secondary)]">
        {{ label }}
      </p>
      <p v-if="sublabel" class="mt-1 text-xs text-[color:var(--color-text-muted)]">
        {{ sublabel }}
      </p>
    </div>
  </GlassCard>
</template>
