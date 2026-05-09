<script setup lang="ts">
/**
 * BackgroundCatGarden — soft cartoon cat + nature ambience.
 * Decorative only: paw paths, leaves, and small cat silhouettes sit behind
 * page content and respect reduced-motion preferences.
 */
import './BackgroundCatGarden.css'

const pawPrints = [
  { className: 'catgarden-paw catgarden-paw--one', rotation: -14 },
  { className: 'catgarden-paw catgarden-paw--two', rotation: 10 },
  { className: 'catgarden-paw catgarden-paw--three', rotation: -8 },
  { className: 'catgarden-paw catgarden-paw--four', rotation: 12 },
] as const

const leaves = [
  'catgarden-leaf catgarden-leaf--one',
  'catgarden-leaf catgarden-leaf--two',
  'catgarden-leaf catgarden-leaf--three',
] as const
</script>

<template>
  <div
    aria-hidden="true"
    class="catgarden-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <div class="catgarden-sky" />
    <div class="catgarden-meadow" />

    <svg class="catgarden-vines" viewBox="0 0 1440 900" preserveAspectRatio="none">
      <path
        class="catgarden-vine catgarden-vine--a"
        d="M-120 210 C150 120 310 265 570 160 C840 50 1020 245 1560 120"
      />
      <path
        class="catgarden-vine catgarden-vine--b"
        d="M-150 680 C180 560 390 760 720 610 C990 485 1210 700 1600 555"
      />
    </svg>

    <span v-for="leaf in leaves" :key="leaf" :class="leaf" />

    <span
      v-for="paw in pawPrints"
      :key="paw.className"
      :class="paw.className"
      :style="{ '--paw-rotate': `${paw.rotation}deg` }"
    >
      <i />
      <i />
      <i />
      <i />
      <b />
    </span>
  </div>
</template>
