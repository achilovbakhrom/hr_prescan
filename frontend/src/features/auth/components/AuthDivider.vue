<script setup lang="ts">
/** Thin divider with a centered label, themed via tokens. */
defineProps<{ label: string }>()
</script>

<template>
  <div class="my-4 flex items-center gap-3" aria-hidden="true">
    <div class="h-px flex-1 bg-[color:var(--color-border-soft)]"></div>
    <span class="text-[11px] uppercase tracking-wider text-[color:var(--color-text-muted)]">
      {{ label }}
    </span>
    <div class="h-px flex-1 bg-[color:var(--color-border-soft)]"></div>
  </div>
</template>
