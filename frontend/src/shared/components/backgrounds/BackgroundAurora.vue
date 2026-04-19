<script setup lang="ts">
/**
 * BackgroundAurora — 3 curved ribbons drifting across the top of the viewport.
 * Each ribbon is a radial/linear gradient blob with large blur + slow vertical
 * sway. Dark mode: higher opacity via screen blending.
 */
</script>

<template>
  <div
    aria-hidden="true"
    class="aurora-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <div class="aurora-ribbon aurora-ribbon--a" />
    <div class="aurora-ribbon aurora-ribbon--b" />
    <div class="aurora-ribbon aurora-ribbon--c" />
  </div>
</template>

<style scoped>
.aurora-root {
  isolation: isolate;
  background-color: transparent;
}

.aurora-ribbon {
  position: absolute;
  left: -20%;
  right: -20%;
  height: 45vmin;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.35;
  mix-blend-mode: multiply;
  will-change: transform;
}

:global(.dark .aurora-ribbon) {
  opacity: 0.22;
  mix-blend-mode: screen;
}

.aurora-ribbon--a {
  top: -10%;
  background: radial-gradient(ellipse at 30% 50%, #60a5fa 0%, transparent 60%);
  animation: aurora-sway-a 18s ease-in-out infinite alternate;
}
.aurora-ribbon--b {
  top: 8%;
  background: radial-gradient(ellipse at 70% 50%, #c4b5fd 0%, transparent 60%);
  animation: aurora-sway-b 22s ease-in-out infinite alternate;
}
.aurora-ribbon--c {
  top: 22%;
  background: radial-gradient(ellipse at 50% 50%, #fdba74 0%, transparent 60%);
  animation: aurora-sway-c 26s ease-in-out infinite alternate;
}

@keyframes aurora-sway-a {
  0% {
    transform: translate(-3%, -2%) scaleX(1.1);
  }
  100% {
    transform: translate(4%, 3%) scaleX(0.95);
  }
}
@keyframes aurora-sway-b {
  0% {
    transform: translate(4%, 2%) scaleX(0.95);
  }
  100% {
    transform: translate(-4%, -2%) scaleX(1.1);
  }
}
@keyframes aurora-sway-c {
  0% {
    transform: translate(-2%, 3%) scaleX(1.05);
  }
  100% {
    transform: translate(3%, -3%) scaleX(0.9);
  }
}

@media (prefers-reduced-motion: reduce) {
  .aurora-ribbon {
    animation: none !important;
  }
}
</style>
