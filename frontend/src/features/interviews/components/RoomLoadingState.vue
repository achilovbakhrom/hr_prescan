<script setup lang="ts">
import AppLogo from '@/shared/components/AppLogo.vue'

withDefaults(
  defineProps<{
    label: string
    icon?: string
    logo?: boolean
  }>(),
  {
    icon: 'pi pi-video',
    logo: false,
  },
)
</script>

<template>
  <div class="w-full max-w-sm px-6 text-center">
    <div
      class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-white shadow-2xl shadow-black/30 ring-1 ring-white/15"
    >
      <AppLogo v-if="logo" variant="glyph" size="md" :linked="false" />
      <i v-else :class="icon" class="text-2xl"></i>
    </div>
    <div class="mx-auto mb-4 h-1.5 w-44 overflow-hidden rounded-full bg-white/10">
      <div class="room-loading-bar h-full rounded-full"></div>
    </div>
    <p class="text-sm font-medium text-white/90">
      {{ label }}
    </p>
  </div>
</template>

<style scoped>
.room-loading-bar {
  width: 45%;
  background: linear-gradient(90deg, #7dd3fc, #a7f3d0, #fef3c7);
  animation: room-loading-slide 1.15s ease-in-out infinite;
}

@keyframes room-loading-slide {
  0% {
    transform: translateX(-110%);
  }

  50% {
    transform: translateX(80%);
  }

  100% {
    transform: translateX(260%);
  }
}
</style>
