<script setup lang="ts">
withDefaults(defineProps<{
  size?: 'sm' | 'md' | 'lg'
}>(), {
  size: 'sm',
})

const sizeMap = {
  sm: { wrapper: 'h-9 w-9', svg: 24 },
  md: { wrapper: 'h-11 w-11', svg: 30 },
  lg: { wrapper: 'h-14 w-14', svg: 38 },
}
</script>

<template>
  <div
    class="flex items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-sm"
    :class="sizeMap[size].wrapper"
  >
    <svg
      :width="sizeMap[size].svg"
      :height="sizeMap[size].svg"
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <!-- Shield outline -->
      <path
        d="M24 4L8 12v12c0 10.4 6.8 20.1 16 23 9.2-2.9 16-12.6 16-23V12L24 4z"
        fill="rgba(255,255,255,0.15)"
        stroke="white"
        stroke-width="1.5"
        stroke-linejoin="round"
      />
      <!-- Person head -->
      <circle cx="24" cy="18" r="4.5" fill="white" />
      <!-- Person body -->
      <path
        d="M16 31c0-4.4 3.6-8 8-8s8 3.6 8 8"
        stroke="white"
        stroke-width="2.5"
        stroke-linecap="round"
        fill="none"
      />
      <!-- AI sparkle left -->
      <path
        d="M12 15l1.2 2.4L15.6 18.6l-2.4 1.2L12 22.2l-1.2-2.4L8.4 18.6l2.4-1.2z"
        fill="rgba(255,255,255,0.7)"
      />
      <!-- AI sparkle right -->
      <path
        d="M36 15l1 2L39 18l-2 1L36 21l-1-2L33 18l2-1z"
        fill="rgba(255,255,255,0.7)"
      />
    </svg>
  </div>
</template>
