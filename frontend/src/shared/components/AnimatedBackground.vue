<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/shared/stores/theme.store'
import { ANIMAL_MAP, type AnimalArt } from '@/shared/components/animals/animals'

const themeStore = useThemeStore()

interface Placement {
  art: AnimalArt
  size: number
  top: number
  left: number
  durationSec: number
  delaySec: number
  driftX: number
  driftY: number
  rotate: number
  tone: string
  anim: 'drift-a' | 'drift-b' | 'drift-c'
}

const FOREST: Placement[] = [
  { art: ANIMAL_MAP.fox, size: 110, top: 14, left: 6, durationSec: 28, delaySec: 0, driftX: 80, driftY: -20, rotate: 4, tone: 'text-amber-700/30 dark:text-amber-300/25', anim: 'drift-a' },
  { art: ANIMAL_MAP.owl, size: 96, top: 28, left: 78, durationSec: 34, delaySec: 3, driftX: -70, driftY: 30, rotate: -3, tone: 'text-slate-500/25 dark:text-slate-300/25', anim: 'drift-b' },
  { art: ANIMAL_MAP.deer, size: 140, top: 62, left: 44, durationSec: 38, delaySec: 2, driftX: 60, driftY: -40, rotate: 2, tone: 'text-stone-600/25 dark:text-stone-300/20', anim: 'drift-c' },
  { art: ANIMAL_MAP.leaf, size: 70, top: 18, left: 42, durationSec: 22, delaySec: 1, driftX: 140, driftY: 40, rotate: 12, tone: 'text-emerald-700/25 dark:text-emerald-400/25', anim: 'drift-b' },
  { art: ANIMAL_MAP.leaf, size: 58, top: 74, left: 86, durationSec: 26, delaySec: 4, driftX: -110, driftY: -30, rotate: -15, tone: 'text-green-700/25 dark:text-green-400/20', anim: 'drift-a' },
  { art: ANIMAL_MAP.owl, size: 72, top: 70, left: 14, durationSec: 30, delaySec: 5, driftX: 50, driftY: 20, rotate: 6, tone: 'text-slate-600/20 dark:text-slate-300/20', anim: 'drift-c' },
]

const OCEAN: Placement[] = [
  { art: ANIMAL_MAP.whale, size: 170, top: 20, left: 8, durationSec: 40, delaySec: 0, driftX: 160, driftY: 20, rotate: 3, tone: 'text-sky-700/25 dark:text-sky-300/25', anim: 'drift-a' },
  { art: ANIMAL_MAP.jellyfish, size: 90, top: 46, left: 72, durationSec: 24, delaySec: 2, driftX: -40, driftY: -80, rotate: -4, tone: 'text-cyan-600/30 dark:text-cyan-300/25', anim: 'drift-b' },
  { art: ANIMAL_MAP.turtle, size: 120, top: 72, left: 36, durationSec: 34, delaySec: 3, driftX: 90, driftY: -20, rotate: 2, tone: 'text-teal-700/25 dark:text-teal-300/20', anim: 'drift-c' },
  { art: ANIMAL_MAP.bubble, size: 40, top: 30, left: 54, durationSec: 20, delaySec: 1, driftX: 20, driftY: -120, rotate: 0, tone: 'text-sky-500/30 dark:text-sky-200/25', anim: 'drift-b' },
  { art: ANIMAL_MAP.bubble, size: 28, top: 62, left: 18, durationSec: 26, delaySec: 4, driftX: -15, driftY: -140, rotate: 0, tone: 'text-sky-500/25 dark:text-sky-200/20', anim: 'drift-b' },
  { art: ANIMAL_MAP.jellyfish, size: 70, top: 10, left: 86, durationSec: 28, delaySec: 5, driftX: -60, driftY: 50, rotate: 5, tone: 'text-indigo-500/25 dark:text-indigo-300/20', anim: 'drift-a' },
]

const placements = computed<Placement[]>(() => {
  if (themeStore.backgroundMode === 'forest') return FOREST
  if (themeStore.backgroundMode === 'ocean') return OCEAN
  return []
})
</script>

<template>
  <div
    v-if="placements.length"
    aria-hidden="true"
    class="pointer-events-none fixed inset-0 z-0 overflow-hidden"
  >
    <svg
      v-for="(p, i) in placements"
      :key="`${themeStore.backgroundMode}-${i}`"
      :class="['bg-animal absolute', p.tone, `anim-${p.anim}`]"
      :viewBox="p.art.viewBox"
      :style="{
        top: p.top + '%',
        left: p.left + '%',
        width: p.size + 'px',
        height: p.size + 'px',
        animationDuration: p.durationSec + 's',
        animationDelay: p.delaySec + 's',
        '--dx': p.driftX + 'px',
        '--dy': p.driftY + 'px',
        '--rot': p.rotate + 'deg',
      }"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path v-for="(d, idx) in p.art.paths" :key="idx" :d="d" />
    </svg>
  </div>
</template>

<style scoped>
.bg-animal {
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
  animation-direction: alternate;
  will-change: transform;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.08));
}

.anim-drift-a {
  animation-name: drift-a;
}
.anim-drift-b {
  animation-name: drift-b;
}
.anim-drift-c {
  animation-name: drift-c;
}

@keyframes drift-a {
  0% {
    transform: translate(0, 0) rotate(calc(var(--rot) * -1));
  }
  40% {
    transform: translate(calc(var(--dx) * 0.4), calc(var(--dy) * 0.7)) rotate(calc(var(--rot) * 0.5));
  }
  100% {
    transform: translate(var(--dx), var(--dy)) rotate(var(--rot));
  }
}

@keyframes drift-b {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  30% {
    transform: translate(calc(var(--dx) * 0.3), calc(var(--dy) * 0.5)) rotate(calc(var(--rot) * 1.2));
  }
  70% {
    transform: translate(calc(var(--dx) * 0.8), calc(var(--dy) * 0.9)) rotate(calc(var(--rot) * -0.8));
  }
  100% {
    transform: translate(var(--dx), var(--dy)) rotate(var(--rot));
  }
}

@keyframes drift-c {
  0% {
    transform: translate(0, 0) rotate(calc(var(--rot) * 0.3));
  }
  50% {
    transform: translate(calc(var(--dx) * 0.6), calc(var(--dy) * 0.4)) rotate(calc(var(--rot) * -1));
  }
  100% {
    transform: translate(var(--dx), var(--dy)) rotate(var(--rot));
  }
}

@media (prefers-reduced-motion: reduce) {
  .bg-animal {
    animation: none !important;
    transform: none !important;
  }
}
</style>
