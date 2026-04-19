<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/shared/stores/theme.store'
import { ANIMAL_MAP, type AnimalArt } from '@/shared/components/animals/animals'
import './animated-background.css'

const themeStore = useThemeStore()

type Motion = 'walk-right' | 'walk-left' | 'swim-right' | 'swim-left' | 'fly' | 'float-up' | 'float-up-slow'

interface Placement {
  art: AnimalArt
  size: number
  /** Top position as % of viewport (0–100) */
  top: number
  durationSec: number
  delaySec: number
  /** Tailwind text-* classes for currentColor */
  tone: string
  motion: Motion
  /** Flip horizontally (for left-walking animals that face right by default) */
  flip?: boolean
}

const FOREST: Placement[] = [
  // Ground-dwellers walking across
  { art: ANIMAL_MAP.fox, size: 120, top: 72, durationSec: 55, delaySec: 0, tone: 'text-amber-700/55 dark:text-amber-300/80', motion: 'walk-right' },
  { art: ANIMAL_MAP.deer, size: 150, top: 68, durationSec: 80, delaySec: 20, tone: 'text-stone-600/50 dark:text-stone-300/70', motion: 'walk-right' },
  { art: ANIMAL_MAP.fox, size: 100, top: 78, durationSec: 65, delaySec: 40, tone: 'text-amber-800/45 dark:text-amber-400/70', motion: 'walk-left', flip: true },
  // Flying owls diagonal
  { art: ANIMAL_MAP.owl, size: 80, top: 18, durationSec: 48, delaySec: 5, tone: 'text-slate-500/50 dark:text-slate-300/75', motion: 'fly' },
  { art: ANIMAL_MAP.owl, size: 64, top: 32, durationSec: 40, delaySec: 25, tone: 'text-slate-600/45 dark:text-slate-400/70', motion: 'fly' },
  // Floating leaves
  { art: ANIMAL_MAP.leaf, size: 50, top: 85, durationSec: 28, delaySec: 0, tone: 'text-emerald-700/55 dark:text-emerald-400/80', motion: 'float-up' },
  { art: ANIMAL_MAP.leaf, size: 38, top: 90, durationSec: 34, delaySec: 8, tone: 'text-green-700/50 dark:text-green-400/70', motion: 'float-up-slow' },
  { art: ANIMAL_MAP.leaf, size: 44, top: 95, durationSec: 30, delaySec: 16, tone: 'text-emerald-800/50 dark:text-emerald-500/70', motion: 'float-up' },
]

const OCEAN: Placement[] = [
  // Whales + fish swim full-width
  { art: ANIMAL_MAP.whale, size: 180, top: 30, durationSec: 90, delaySec: 0, tone: 'text-sky-700/50 dark:text-sky-300/75', motion: 'swim-right' },
  { art: ANIMAL_MAP.whale, size: 130, top: 60, durationSec: 70, delaySec: 35, tone: 'text-indigo-600/45 dark:text-indigo-300/70', motion: 'swim-left', flip: true },
  { art: ANIMAL_MAP.turtle, size: 110, top: 72, durationSec: 60, delaySec: 15, tone: 'text-teal-700/50 dark:text-teal-300/70', motion: 'swim-right' },
  { art: ANIMAL_MAP.jellyfish, size: 85, top: 45, durationSec: 32, delaySec: 0, tone: 'text-cyan-600/55 dark:text-cyan-300/80', motion: 'float-up-slow' },
  { art: ANIMAL_MAP.jellyfish, size: 60, top: 55, durationSec: 28, delaySec: 10, tone: 'text-indigo-500/50 dark:text-indigo-300/75', motion: 'float-up' },
  // Bubbles drift up
  { art: ANIMAL_MAP.bubble, size: 32, top: 95, durationSec: 18, delaySec: 0, tone: 'text-sky-500/55 dark:text-sky-200/80', motion: 'float-up' },
  { art: ANIMAL_MAP.bubble, size: 24, top: 98, durationSec: 22, delaySec: 5, tone: 'text-sky-500/50 dark:text-sky-200/70', motion: 'float-up-slow' },
  { art: ANIMAL_MAP.bubble, size: 40, top: 92, durationSec: 20, delaySec: 12, tone: 'text-cyan-500/55 dark:text-cyan-200/80', motion: 'float-up' },
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
      :class="['bg-animal absolute', p.tone, `motion-${p.motion}`, { 'flip-x': p.flip }]"
      :viewBox="p.art.viewBox"
      :style="{
        top: p.top + '%',
        width: p.size + 'px',
        height: p.size + 'px',
        animationDuration: p.durationSec + 's',
        animationDelay: p.delaySec + 's',
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
