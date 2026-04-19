<script setup lang="ts">
/**
 * BackgroundVellum — calm, paper-like two-layer background.
 * Layer 1: slow "breathing" radial gradient (12s cycle).
 * Layer 2: SVG fractal-noise texture at ~4% opacity — cached as inline SVG filter.
 * Reduced-motion: breathing locked at 0.75 opacity, noise static.
 */
</script>

<template>
  <div
    aria-hidden="true"
    class="vellum-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <!-- Layer 1: breathing radial gradient -->
    <div class="vellum-breath" />

    <!-- Layer 2: fractal-noise texture (SVG filter, rendered to a full-bleed rect) -->
    <svg class="vellum-noise" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
      <filter id="vellum-noise-filter">
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
        <feColorMatrix
          type="matrix"
          values="0 0 0 0 0
                  0 0 0 0 0
                  0 0 0 0 0
                  0 0 0 0.9 0"
        />
      </filter>
      <rect width="100%" height="100%" filter="url(#vellum-noise-filter)" />
    </svg>
  </div>
</template>

<style scoped>
.vellum-root {
  isolation: isolate;
  background-color: var(--color-surface-base);
}

.vellum-breath {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 40%, var(--color-surface-raised), transparent 70%);
  opacity: 0.75;
  will-change: opacity;
  animation: vellum-breathe 12s ease-in-out infinite;
}

@keyframes vellum-breathe {
  0%,
  100% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.9;
  }
}

.vellum-noise {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.04;
  mix-blend-mode: multiply;
  pointer-events: none;
}

:global(.dark) .vellum-noise {
  opacity: 0.06;
  mix-blend-mode: screen;
}

@media (prefers-reduced-motion: reduce) {
  .vellum-breath {
    animation: none !important;
    opacity: 0.75 !important;
  }
}
</style>
