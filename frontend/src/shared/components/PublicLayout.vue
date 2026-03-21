<script setup lang="ts">
import PublicHeader from './PublicHeader.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-gray-50">
    <PublicHeader />
    <RouterView />
  </div>
</template>
