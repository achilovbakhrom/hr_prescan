<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-white">
    <header class="border-b border-gray-200 px-6 py-4">
      <h1 class="text-2xl font-bold text-gray-900">HR PreScan</h1>
    </header>
    <main class="p-6">
      <RouterView />
    </main>
  </div>
</template>
