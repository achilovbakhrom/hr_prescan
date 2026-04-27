<script setup lang="ts">
/**
 * BackgroundWaves — quiet contour ribbons.
 * The old heavy bottom waves are replaced by thin full-viewport paths that
 * drift slowly and stay behind glass UI without pulling focus.
 */
</script>

<template>
  <div
    aria-hidden="true"
    class="waves-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <svg class="waves-svg" viewBox="0 0 1440 900" preserveAspectRatio="none">
      <path class="wave wave--a" d="M-120 210 C190 70 390 360 710 210 C1010 70 1170 220 1560 90" />
      <path
        class="wave wave--b"
        d="M-160 430 C180 300 420 570 730 410 C990 270 1230 510 1600 330"
      />
      <path
        class="wave wave--c"
        d="M-140 665 C210 545 440 760 760 635 C1060 520 1230 760 1580 600"
      />
      <path
        class="wave wave--d"
        d="M-100 815 C230 720 500 865 790 760 C1080 655 1280 815 1540 715"
      />
    </svg>
  </div>
</template>

<style scoped>
.waves-root {
  isolation: isolate;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.62), transparent), transparent;
}

.waves-svg {
  position: absolute;
  inset: -8% -6%;
  width: 112%;
  height: 116%;
  fill: none;
  transform: translate3d(0, 0, 0);
}

.wave {
  stroke-linecap: round;
  stroke-width: 2.4;
  opacity: 0.34;
  filter: drop-shadow(0 18px 24px rgba(37, 99, 235, 0.08));
  animation: wave-drift 30s ease-in-out infinite alternate;
}

.wave--a {
  stroke: rgba(37, 99, 235, 0.32);
  animation-duration: 28s;
}

.wave--b {
  stroke: rgba(20, 184, 166, 0.28);
  animation-duration: 34s;
  animation-delay: -7s;
}

.wave--c {
  stroke: rgba(124, 92, 255, 0.24);
  animation-duration: 38s;
  animation-delay: -13s;
}

.wave--d {
  stroke: rgba(253, 186, 116, 0.28);
  animation-duration: 42s;
  animation-delay: -18s;
}

:global(.dark .waves-root) {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.82), transparent), transparent;
}

:global(.dark .wave) {
  opacity: 0.22;
  filter: drop-shadow(0 20px 28px rgba(96, 165, 250, 0.08));
}

@keyframes wave-drift {
  0% {
    transform: translateX(-18px) translateY(8px);
  }
  100% {
    transform: translateX(22px) translateY(-10px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .wave {
    animation: none !important;
  }
}
</style>
