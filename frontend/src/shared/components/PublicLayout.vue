<script setup lang="ts">
import PublicHeader from './PublicHeader.vue'
import PageShell from './PageShell.vue'
</script>

<template>
  <PageShell variant="public">
    <template #nav>
      <PublicHeader />
    </template>
    <RouterView />
  </PageShell>
</template>
