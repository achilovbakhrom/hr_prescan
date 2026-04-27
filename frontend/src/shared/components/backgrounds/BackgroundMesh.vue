<script setup lang="ts">
/**
 * BackgroundMesh — continuous layered color field.
 * Replaces separate blobs with broad gradient sheets so the default background
 * feels richer and less spotty. Motion is slow background-position drift only.
 */
</script>

<template>
  <div aria-hidden="true" class="mesh-root pointer-events-none fixed inset-0 -z-10 overflow-hidden">
    <div class="mesh-field" />
    <div class="mesh-sheen" />
    <div class="mesh-grain" />
  </div>
</template>

<style scoped>
.mesh-root {
  isolation: isolate;
  background:
    linear-gradient(135deg, rgba(248, 250, 252, 0.86), rgba(241, 245, 249, 0.62)),
    var(--color-surface-base);
}

.mesh-field,
.mesh-sheen,
.mesh-grain {
  position: absolute;
  inset: -16%;
}

.mesh-field {
  background:
    radial-gradient(ellipse 78% 54% at 12% 18%, rgba(37, 99, 235, 0.26), transparent 68%),
    radial-gradient(ellipse 72% 58% at 86% 24%, rgba(20, 184, 166, 0.2), transparent 68%),
    radial-gradient(ellipse 70% 60% at 48% 88%, rgba(244, 114, 182, 0.16), transparent 70%),
    linear-gradient(120deg, rgba(124, 92, 255, 0.12), rgba(253, 186, 116, 0.12), transparent 72%);
  background-size:
    120% 120%,
    118% 118%,
    130% 130%,
    160% 160%;
  filter: blur(34px) saturate(1.12);
  opacity: 0.92;
  mix-blend-mode: multiply;
  animation: mesh-field-drift 34s ease-in-out infinite alternate;
}

.mesh-sheen {
  background:
    linear-gradient(105deg, transparent 18%, rgba(255, 255, 255, 0.38) 43%, transparent 67%),
    linear-gradient(18deg, rgba(37, 99, 235, 0.06), transparent 48%);
  filter: blur(20px);
  opacity: 0.52;
  transform: rotate(-4deg);
  animation: mesh-sheen-drift 26s ease-in-out infinite alternate;
}

.mesh-grain {
  inset: 0;
  background-image:
    linear-gradient(rgba(15, 23, 42, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 23, 42, 0.026) 1px, transparent 1px);
  background-size: 76px 76px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.72), transparent 72%);
  opacity: 0.28;
}

:global(.dark .mesh-root) {
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.9)), var(--color-surface-base);
}

:global(.dark .mesh-field) {
  opacity: 0.5;
  mix-blend-mode: screen;
  filter: blur(42px) saturate(1.18);
}

:global(.dark .mesh-sheen) {
  opacity: 0.2;
}

:global(.dark .mesh-grain) {
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  opacity: 0.22;
}

@keyframes mesh-field-drift {
  0% {
    background-position:
      0% 0%,
      100% 0%,
      50% 100%,
      0% 50%;
    transform: scale(1) rotate(0deg);
  }
  100% {
    background-position:
      12% 8%,
      88% 12%,
      42% 86%,
      100% 44%;
    transform: scale(1.04) rotate(1.5deg);
  }
}

@keyframes mesh-sheen-drift {
  0% {
    transform: translateX(-3%) rotate(-4deg);
  }
  100% {
    transform: translateX(3%) rotate(-2deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .mesh-field,
  .mesh-sheen {
    animation: none !important;
  }
}
</style>
