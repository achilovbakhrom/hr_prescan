<script setup lang="ts">
/**
 * AdminFiltersBar — thin glass toolbar above admin DataTables.
 * Holds search + filter selects + action buttons. Denser than main app toolbars.
 *
 * Spec: docs/design/spec.md §9 (admin = minimal glass on chrome only).
 */
import GlassSurface from '@/shared/components/GlassSurface.vue'
</script>

<template>
  <GlassSurface
    level="1"
    class="admin-filters-bar mb-3 flex flex-wrap items-center gap-2 px-3 py-2"
  >
    <slot />
  </GlassSurface>
</template>
