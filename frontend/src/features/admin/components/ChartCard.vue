<script setup lang="ts">
/**
 * ChartCard — glass frame around a chart.js canvas.
 * Used by admin analytics charts. Keeps per-chart components small.
 */
import GlassSurface from '@/shared/components/GlassSurface.vue'

defineProps<{ title: string }>()
</script>

<template>
  <GlassSurface level="1" class="px-4 py-3">
    <h2 class="mb-3 text-sm font-semibold text-[color:var(--color-text-primary)]">
      {{ title }}
    </h2>
    <div class="h-56">
      <slot />
    </div>
  </GlassSurface>
</template>
