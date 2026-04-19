<script setup lang="ts">
/**
 * ApplicationStepsBar — glass breadcrumb that shows the 3 application
 * steps (form → ready → done) with the active step highlighted.
 */
import GlassSurface from '@/shared/components/GlassSurface.vue'

interface Step {
  id: string
  label: string
}

defineProps<{
  steps: Step[]
  current: string
}>()
</script>

<template>
  <GlassSurface level="float" class="flex items-center gap-2 p-2 sm:gap-3">
    <template v-for="(s, idx) in steps" :key="s.id">
      <div
        class="flex items-center gap-2 rounded-md px-2 py-1 text-xs font-medium sm:px-3 sm:text-sm"
        :class="
          current === s.id
            ? 'bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]'
            : 'text-[color:var(--color-text-muted)]'
        "
      >
        <span
          class="flex h-5 w-5 items-center justify-center rounded-full font-mono text-[10px]"
          :class="
            current === s.id
              ? 'bg-[color:var(--color-accent-ai)] text-[color:var(--color-text-on-accent)]'
              : 'bg-[color:var(--color-surface-sunken)]'
          "
        >
          {{ idx + 1 }}
        </span>
        <span class="hidden sm:inline">{{ s.label }}</span>
      </div>
      <i
        v-if="idx < steps.length - 1"
        class="pi pi-chevron-right text-[10px] text-[color:var(--color-text-muted)]"
      ></i>
    </template>
  </GlassSurface>
</template>
