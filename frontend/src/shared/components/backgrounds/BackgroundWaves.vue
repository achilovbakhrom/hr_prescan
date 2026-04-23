<script setup lang="ts">
/**
 * BackgroundWaves — three overlapping SVG sine waves at the bottom of the
 * viewport, each animating horizontally at a different speed. Gives the page
 * a calm "tide" feel.
 */
</script>

<template>
  <div
    aria-hidden="true"
    class="waves-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <svg class="waves-svg waves-svg--a" viewBox="0 0 1440 320" preserveAspectRatio="none">
      <path fill="#60a5fa" d="M0,160 C320,260 720,60 1440,180 L1440,320 L0,320 Z" />
    </svg>
    <svg class="waves-svg waves-svg--b" viewBox="0 0 1440 320" preserveAspectRatio="none">
      <path fill="#c4b5fd" d="M0,200 C360,100 820,260 1440,140 L1440,320 L0,320 Z" />
    </svg>
    <svg class="waves-svg waves-svg--c" viewBox="0 0 1440 320" preserveAspectRatio="none">
      <path fill="#fdba74" d="M0,240 C400,140 900,280 1440,200 L1440,320 L0,320 Z" />
    </svg>
  </div>
</template>

<style scoped>
.waves-root {
  isolation: isolate;
  background-color: transparent;
}

.waves-svg {
  position: absolute;
  left: -10%;
  right: -10%;
  bottom: 0;
  width: 120%;
  height: 60vmin;
  opacity: 0.18;
  mix-blend-mode: multiply;
  will-change: transform;
}

:global(.dark .waves-svg) {
  opacity: 0.12;
  mix-blend-mode: screen;
}

.waves-svg--a {
  animation: waves-drift-a 22s ease-in-out infinite alternate;
}
.waves-svg--b {
  animation: waves-drift-b 28s ease-in-out infinite alternate;
  bottom: -3vmin;
}
.waves-svg--c {
  animation: waves-drift-c 34s ease-in-out infinite alternate;
  bottom: -6vmin;
}

@keyframes waves-drift-a {
  0% {
    transform: translateX(-3%);
  }
  100% {
    transform: translateX(3%);
  }
}
@keyframes waves-drift-b {
  0% {
    transform: translateX(4%);
  }
  100% {
    transform: translateX(-4%);
  }
}
@keyframes waves-drift-c {
  0% {
    transform: translateX(-2%);
  }
  100% {
    transform: translateX(5%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .waves-svg {
    animation: none !important;
  }
}
</style>
