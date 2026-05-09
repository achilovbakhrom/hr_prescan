<script setup lang="ts">
import PublicHeader from '@/shared/components/PublicHeader.vue'
import PageShell from '@/shared/components/PageShell.vue'
</script>

<template>
  <PageShell variant="public">
    <template #nav>
      <PublicHeader />
    </template>
    <slot />
  </PageShell>
</template>
