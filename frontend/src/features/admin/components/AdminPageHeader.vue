<script setup lang="ts">
/**
 * AdminPageHeader — dense page header used across all admin pages.
 * Minimal glass treatment per spec §9: just a thin glass surface + eyebrow
 * crumb + title + optional subtitle. Compact vertical rhythm (tighter than
 * HR dashboard).
 */
import GlassSurface from '@/shared/components/GlassSurface.vue'

defineProps<{
  eyebrow: string
  title: string
  subtitle?: string
}>()
</script>

<template>
  <GlassSurface
    level="1"
    class="admin-header sticky top-4 z-10 mb-4 flex items-center justify-between gap-3 px-4 py-2.5"
  >
    <div class="min-w-0">
      <p
        class="font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
      >
        {{ eyebrow }}
      </p>
      <h1 class="truncate text-lg font-semibold text-[color:var(--color-text-primary)]">
        {{ title }}
      </h1>
      <p v-if="subtitle" class="truncate text-xs text-[color:var(--color-text-muted)]">
        {{ subtitle }}
      </p>
    </div>
    <div class="shrink-0">
      <slot name="actions" />
    </div>
  </GlassSurface>
</template>
