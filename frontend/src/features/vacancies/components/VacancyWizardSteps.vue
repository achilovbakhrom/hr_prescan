<script setup lang="ts">
/**
 * VacancyWizardSteps — horizontal glass-chip progress bar for the
 * vacancy creation wizard. Chips are clickable so users can jump to
 * earlier steps; forward jumps are gated by `maxReached`.
 */
import GlassSurface from '@/shared/components/GlassSurface.vue'

interface Step {
  key: string
  label: string
}

defineProps<{
  steps: Step[]
  /** Index of the step currently shown. */
  activeIndex: number
  /** Highest step index the user has reached. */
  maxReached: number
}>()

defineEmits<{
  select: [index: number]
}>()
</script>

<template>
  <GlassSurface class="flex w-full items-stretch gap-1 overflow-x-auto rounded-lg p-1" level="1">
    <button
      v-for="(step, i) in steps"
      :key="step.key"
      type="button"
      class="wizard-chip flex min-w-0 flex-1 items-center gap-2 whitespace-nowrap rounded-md px-3 py-2 text-left text-sm transition-colors"
      :class="[
        i === activeIndex
          ? 'wizard-chip--active bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
          : i <= maxReached
            ? 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-sunken)]'
            : 'cursor-not-allowed text-[color:var(--color-text-muted)] opacity-60',
      ]"
      :disabled="i > maxReached"
      :aria-current="i === activeIndex ? 'step' : undefined"
      @click="i <= maxReached && $emit('select', i)"
    >
      <span
        class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
        :class="
          i === activeIndex
            ? 'bg-[color:var(--color-accent)] text-[color:var(--color-text-on-accent)]'
            : i < maxReached
              ? 'bg-[color:var(--color-success)] text-[color:var(--color-text-on-accent)]'
              : 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
        "
      >
        <i v-if="i < activeIndex && i < maxReached" class="pi pi-check text-[10px]"></i>
        <template v-else>{{ i + 1 }}</template>
      </span>
      <span class="truncate font-medium">{{ step.label }}</span>
    </button>
  </GlassSurface>
</template>
