<script setup lang="ts">
/**
 * BackgroundRays — diagonal light beams emanating from the upper-left corner,
 * slowly rotating. Evokes sun rays through a window. Subtle in both themes.
 */
</script>

<template>
  <div aria-hidden="true" class="rays-root pointer-events-none fixed inset-0 -z-10 overflow-hidden">
    <div class="rays-sweep" />
  </div>
</template>

<style scoped>
.rays-root {
  isolation: isolate;
  background-color: transparent;
}

.rays-sweep {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(
    from 210deg at 20% 20%,
    transparent 0deg,
    rgba(96, 165, 250, 0.18) 20deg,
    transparent 40deg,
    rgba(196, 181, 253, 0.18) 70deg,
    transparent 95deg,
    rgba(253, 186, 116, 0.14) 130deg,
    transparent 160deg,
    rgba(96, 165, 250, 0.1) 200deg,
    transparent 240deg,
    transparent 360deg
  );
  filter: blur(60px);
  opacity: 0.6;
  mix-blend-mode: multiply;
  will-change: transform;
  animation: rays-rotate 60s linear infinite;
}

:global(.dark .rays-sweep) {
  opacity: 0.4;
  mix-blend-mode: screen;
}

@keyframes rays-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .rays-sweep {
    animation: none !important;
  }
}
</style>
