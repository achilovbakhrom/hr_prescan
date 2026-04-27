<script setup lang="ts">
/**
 * BackgroundVellum — soft editorial surface for auth and focused flows.
 * Uses layered sheets, a restrained grid, and static paper texture.
 */
</script>

<template>
  <div
    aria-hidden="true"
    class="vellum-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <div class="vellum-wash" />
    <div class="vellum-folds" />
    <div class="vellum-grid" />
    <svg class="vellum-noise" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
      <filter id="vellum-noise-filter">
        <feTurbulence
          type="fractalNoise"
          baseFrequency="0.72"
          numOctaves="2"
          stitchTiles="stitch"
        />
        <feColorMatrix
          type="matrix"
          values="0 0 0 0 0
                  0 0 0 0 0
                  0 0 0 0 0
                  0 0 0 0.75 0"
        />
      </filter>
      <rect width="100%" height="100%" filter="url(#vellum-noise-filter)" />
    </svg>
  </div>
</template>

<style scoped>
.vellum-root {
  isolation: isolate;
  background:
    linear-gradient(145deg, rgba(248, 250, 252, 0.94), rgba(226, 232, 240, 0.58)),
    var(--color-surface-base);
}

.vellum-wash,
.vellum-folds,
.vellum-grid,
.vellum-noise {
  position: absolute;
  inset: 0;
}

.vellum-wash {
  background:
    radial-gradient(ellipse 90% 50% at 18% 8%, rgba(59, 130, 246, 0.1), transparent 68%),
    radial-gradient(ellipse 70% 46% at 92% 86%, rgba(20, 184, 166, 0.1), transparent 70%),
    linear-gradient(120deg, transparent 12%, rgba(255, 255, 255, 0.54) 38%, transparent 64%);
  opacity: 0.95;
  animation: vellum-wash 22s ease-in-out infinite alternate;
}

.vellum-folds {
  background:
    linear-gradient(
      112deg,
      transparent 0 28%,
      rgba(255, 255, 255, 0.32) 29% 31%,
      transparent 32% 100%
    ),
    linear-gradient(
      112deg,
      transparent 0 63%,
      rgba(15, 23, 42, 0.045) 64% 65%,
      transparent 66% 100%
    );
  opacity: 0.6;
}

.vellum-grid {
  background-image:
    linear-gradient(rgba(15, 23, 42, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 23, 42, 0.032) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(150deg, rgba(0, 0, 0, 0.45), transparent 72%);
  opacity: 0.36;
}

.vellum-noise {
  width: 100%;
  height: 100%;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

:global(.dark .vellum-root) {
  background:
    linear-gradient(145deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.78)),
    var(--color-surface-base);
}

:global(.dark .vellum-wash) {
  opacity: 0.42;
  mix-blend-mode: screen;
}

:global(.dark .vellum-folds),
:global(.dark .vellum-grid) {
  opacity: 0.24;
}

:global(.dark .vellum-noise) {
  opacity: 0.05;
  mix-blend-mode: screen;
}

@keyframes vellum-wash {
  0% {
    transform: translateX(-1.5%);
    opacity: 0.82;
  }
  100% {
    transform: translateX(1.5%);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .vellum-wash {
    animation: none !important;
  }
}
</style>
