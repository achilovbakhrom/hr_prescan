<script setup lang="ts">
import { computed, onMounted } from 'vue'
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
 * On first load (no stored preference) picks a random variant and persists it,
 * so users don't see the same one every time but returning users keep theirs.
 */

const BG_KEY = 'hr_prescan_bg_mode'
const RANDOM_POOL: BackgroundMode[] = ['mesh', 'constellation', 'vellum', 'aurora', 'waves', 'rays']

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

onMounted(() => {
  // Random-on-first-load: only override when the key was never written.
  // theme.store's readBackground() returns 'vellum' for null and writes on
  // legacy values — so checking null identifies truly first-time users.
  if (localStorage.getItem(BG_KEY) === null) {
    const pick = RANDOM_POOL[Math.floor(Math.random() * RANDOM_POOL.length)]
    themeStore.setBackgroundMode(pick)
  }
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
