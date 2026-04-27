<script setup lang="ts">
/**
 * BackgroundRays — narrow glass-light planes.
 * Keeps the directional energy of rays, but replaces the rotating conic sweep
 * with slow, architectural diagonal sheets.
 */
</script>

<template>
  <div aria-hidden="true" class="rays-root pointer-events-none fixed inset-0 -z-10 overflow-hidden">
    <div class="rays-field" />
    <div class="rays-lines" />
    <div class="rays-vignette" />
  </div>
</template>

<style scoped>
.rays-root {
  isolation: isolate;
  background:
    linear-gradient(140deg, rgba(248, 250, 252, 0.86), rgba(226, 232, 240, 0.4)), transparent;
}

.rays-field,
.rays-lines,
.rays-vignette {
  position: absolute;
  inset: 0;
}

.rays-field {
  inset: -18%;
  background:
    linear-gradient(118deg, transparent 13%, rgba(37, 99, 235, 0.13) 22%, transparent 35%),
    linear-gradient(118deg, transparent 38%, rgba(20, 184, 166, 0.1) 49%, transparent 62%),
    linear-gradient(118deg, transparent 64%, rgba(124, 92, 255, 0.1) 74%, transparent 86%);
  filter: blur(26px);
  opacity: 0.9;
  transform: rotate(-5deg);
  animation: rays-slide 32s ease-in-out infinite alternate;
}

.rays-lines {
  background-image: repeating-linear-gradient(
    118deg,
    transparent 0 72px,
    rgba(15, 23, 42, 0.035) 73px 74px,
    transparent 75px 146px
  );
  mask-image: linear-gradient(135deg, rgba(0, 0, 0, 0.7), transparent 68%);
  opacity: 0.42;
}

.rays-vignette {
  background:
    radial-gradient(ellipse 90% 64% at 18% 14%, rgba(255, 255, 255, 0.48), transparent 64%),
    radial-gradient(ellipse 90% 70% at 100% 100%, rgba(15, 23, 42, 0.05), transparent 70%);
}

:global(.dark .rays-root) {
  background: linear-gradient(140deg, rgba(15, 23, 42, 0.94), rgba(2, 6, 23, 0.88)), transparent;
}

:global(.dark .rays-field) {
  opacity: 0.36;
  mix-blend-mode: screen;
}

:global(.dark .rays-lines) {
  background-image: repeating-linear-gradient(
    118deg,
    transparent 0 72px,
    rgba(255, 255, 255, 0.04) 73px 74px,
    transparent 75px 146px
  );
  opacity: 0.24;
}

:global(.dark .rays-vignette) {
  opacity: 0.35;
  mix-blend-mode: screen;
}

@keyframes rays-slide {
  0% {
    transform: translateX(-2%) rotate(-5deg);
  }
  100% {
    transform: translateX(2%) rotate(-3deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .rays-field {
    animation: none !important;
  }
}
</style>
