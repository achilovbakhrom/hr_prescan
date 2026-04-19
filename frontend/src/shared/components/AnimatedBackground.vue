<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/shared/stores/theme.store'

const themeStore = useThemeStore()

interface Animal {
  emoji: string
  size: number
  top: number
  left: number
  durationSec: number
  delaySec: number
  driftPx: number
}

const FOREST: Animal[] = [
  { emoji: '🦊', size: 56, top: 12, left: 8, durationSec: 22, delaySec: 0, driftPx: 80 },
  { emoji: '🦉', size: 48, top: 30, left: 78, durationSec: 26, delaySec: 4, driftPx: -60 },
  { emoji: '🦔', size: 44, top: 68, left: 18, durationSec: 30, delaySec: 2, driftPx: 50 },
  { emoji: '🐿️', size: 42, top: 52, left: 62, durationSec: 24, delaySec: 6, driftPx: -70 },
  { emoji: '🍃', size: 32, top: 20, left: 40, durationSec: 18, delaySec: 1, driftPx: 120 },
  { emoji: '🌿', size: 36, top: 80, left: 88, durationSec: 20, delaySec: 3, driftPx: -40 },
  { emoji: '🦌', size: 58, top: 74, left: 48, durationSec: 28, delaySec: 5, driftPx: 90 },
]

const OCEAN: Animal[] = [
  { emoji: '🐋', size: 72, top: 22, left: 12, durationSec: 32, delaySec: 0, driftPx: 140 },
  { emoji: '🪼', size: 48, top: 48, left: 70, durationSec: 20, delaySec: 2, driftPx: -60 },
  { emoji: '🐠', size: 40, top: 18, left: 58, durationSec: 16, delaySec: 1, driftPx: 100 },
  { emoji: '🐙', size: 52, top: 76, left: 24, durationSec: 26, delaySec: 4, driftPx: -80 },
  { emoji: '🐚', size: 36, top: 66, left: 84, durationSec: 22, delaySec: 3, driftPx: 40 },
  { emoji: '🐢', size: 54, top: 38, left: 38, durationSec: 30, delaySec: 5, driftPx: 70 },
  { emoji: '🫧', size: 30, top: 8, left: 82, durationSec: 18, delaySec: 2, driftPx: -50 },
]

const animals = computed<Animal[]>(() => {
  if (themeStore.backgroundMode === 'forest') return FOREST
  if (themeStore.backgroundMode === 'ocean') return OCEAN
  return []
})
</script>

<template>
  <div
    v-if="animals.length"
    aria-hidden="true"
    class="pointer-events-none fixed inset-0 z-0 overflow-hidden"
  >
    <span
      v-for="(a, i) in animals"
      :key="`${themeStore.backgroundMode}-${i}`"
      class="bg-animal absolute select-none opacity-20 dark:opacity-25"
      :style="{
        top: a.top + '%',
        left: a.left + '%',
        fontSize: a.size + 'px',
        animationDuration: a.durationSec + 's',
        animationDelay: a.delaySec + 's',
        '--drift': a.driftPx + 'px',
      }"
    >
      {{ a.emoji }}
    </span>
  </div>
</template>

<style scoped>
.bg-animal {
  animation-name: float-drift;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
  animation-direction: alternate;
  will-change: transform;
  filter: blur(0.3px);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

@keyframes float-drift {
  0% {
    transform: translate(0, 0) rotate(-4deg);
  }
  50% {
    transform: translate(calc(var(--drift) * 0.5), -18px) rotate(3deg);
  }
  100% {
    transform: translate(var(--drift), 10px) rotate(-2deg);
  }
}
</style>
