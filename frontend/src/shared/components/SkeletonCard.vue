<script setup lang="ts">
interface Props {
  lines?: number
  showAvatar?: boolean
}

withDefaults(defineProps<Props>(), {
  lines: 3,
  showAvatar: false,
})
</script>

<template>
  <div
    class="rounded-xl border border-gray-100 bg-white p-6 shadow-sm"
    role="status"
    aria-label="Loading content"
    aria-busy="true"
  >
    <!-- Avatar / icon placeholder -->
    <div v-if="showAvatar" class="mb-4 flex items-center gap-3">
      <div
        class="h-10 w-10 animate-pulse rounded-full bg-gray-200"
      ></div>
      <div class="flex-1 space-y-2">
        <div class="h-4 w-1/3 animate-pulse rounded-full bg-gray-200"></div>
        <div class="h-3 w-1/4 animate-pulse rounded-full bg-gray-200"></div>
      </div>
    </div>

    <!-- Title placeholder -->
    <div class="mb-4 h-5 w-2/3 animate-pulse rounded-full bg-gray-200"></div>

    <!-- Content lines -->
    <div class="space-y-3">
      <div
        v-for="i in lines"
        :key="i"
        class="animate-pulse rounded-full bg-gray-200"
        :class="i === lines ? 'h-3 w-1/2' : 'h-3 w-full'"
      ></div>
    </div>

    <!-- Footer placeholder -->
    <div class="mt-6 flex items-center justify-between">
      <div class="h-8 w-24 animate-pulse rounded-lg bg-gray-200"></div>
      <div class="h-8 w-16 animate-pulse rounded-lg bg-gray-200"></div>
    </div>
  </div>
</template>
