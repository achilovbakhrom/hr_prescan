<script setup lang="ts">
/**
 * BackgroundOcean — slow water field with line-art sea life.
 * Uses existing SVG animal paths and keeps motion calm enough to sit behind UI.
 */
import { JELLYFISH, TURTLE, WHALE, type AnimalArt } from '../animals/animals'
import './BackgroundOcean.css'

interface Creature {
  art: AnimalArt
  className: string
}

const creatures: readonly Creature[] = [
  { art: WHALE, className: 'ocean-creature ocean-creature--whale' },
  { art: TURTLE, className: 'ocean-creature ocean-creature--turtle' },
  { art: JELLYFISH, className: 'ocean-creature ocean-creature--jellyfish' },
]
</script>

<template>
  <div
    aria-hidden="true"
    class="ocean-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <div class="ocean-surface" />
    <div class="ocean-caustics" />

    <svg class="ocean-waves" viewBox="0 0 1440 900" preserveAspectRatio="none">
      <path
        class="ocean-wave ocean-wave--a"
        d="M-120 175 C140 90 330 260 610 160 C880 60 1070 225 1560 118"
      />
      <path
        class="ocean-wave ocean-wave--b"
        d="M-150 360 C180 250 390 470 690 330 C980 190 1190 450 1590 285"
      />
      <path
        class="ocean-wave ocean-wave--c"
        d="M-160 585 C170 455 410 690 730 560 C1040 430 1250 660 1600 500"
      />
      <path
        class="ocean-wave ocean-wave--d"
        d="M-120 760 C230 660 480 830 790 710 C1100 590 1280 790 1560 660"
      />
    </svg>

    <svg
      v-for="creature in creatures"
      :key="creature.art.id"
      :class="creature.className"
      :viewBox="creature.art.viewBox"
      fill="none"
    >
      <path
        v-for="path in creature.art.paths"
        :key="path"
        :d="path"
        vector-effect="non-scaling-stroke"
      />
    </svg>
  </div>
</template>
