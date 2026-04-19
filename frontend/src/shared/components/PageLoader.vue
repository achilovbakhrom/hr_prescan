<script setup lang="ts">
interface Props {
  message?: string
  overlay?: boolean
}

withDefaults(defineProps<Props>(), {
  message: 'Loading...',
  overlay: false,
})
</script>

<template>
  <div
    :class="[
      'flex flex-col items-center justify-center gap-4',
      overlay ? 'fixed inset-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm' : 'min-h-64 w-full',
    ]"
    role="status"
    :aria-label="message"
    aria-busy="true"
    aria-live="polite"
  >
    <!-- Spinner -->
    <div class="relative">
      <div
        class="h-12 w-12 animate-spin rounded-full border-4 border-blue-100 dark:border-blue-900 border-t-blue-600"
      ></div>
      <div
        class="absolute inset-0 h-12 w-12 animate-ping rounded-full border-2 border-blue-200 dark:border-blue-800 opacity-20"
      ></div>
    </div>

    <!-- Message -->
    <p class="text-sm font-medium text-gray-600">{{ message }}</p>
  </div>
</template>
