<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore, type BackgroundMode } from '@/shared/stores/theme.store'
import BackgroundMesh from './backgrounds/BackgroundMesh.vue'
import BackgroundConstellation from './backgrounds/BackgroundConstellation.vue'
import BackgroundVellum from './backgrounds/BackgroundVellum.vue'
import BackgroundAurora from './backgrounds/BackgroundAurora.vue'
import BackgroundWaves from './backgrounds/BackgroundWaves.vue'
import BackgroundRays from './backgrounds/BackgroundRays.vue'

/**
 * AnimatedBackground — orchestrator.
 * Renders one of 4 background variants based on themeStore.backgroundMode,
 * with a 600ms opacity crossfade between modes (spec §8: bgCrossfade).
 * First-time users get the first picker option from theme.store; returning
 * users keep their saved choice.
 */

const themeStore = useThemeStore()

const variantMap = {
  mesh: BackgroundMesh,
  constellation: BackgroundConstellation,
  vellum: BackgroundVellum,
  aurora: BackgroundAurora,
  waves: BackgroundWaves,
  rays: BackgroundRays,
} as const

const current = computed(() => {
  const mode = themeStore.backgroundMode
  if (mode === 'off') return null
  return variantMap[mode] ?? null
})

</script>

<template>
  <Transition name="bg-crossfade" mode="out-in">
    <component :is="current" v-if="current" :key="themeStore.backgroundMode" />
  </Transition>
</template>

<style scoped>
.bg-crossfade-enter-active,
.bg-crossfade-leave-active {
  transition: opacity 600ms var(--ease-out-soft);
}

.bg-crossfade-enter-from,
.bg-crossfade-leave-to {
  opacity: 0;
}

.bg-crossfade-enter-to,
.bg-crossfade-leave-from {
  opacity: 1;
}
</style>
