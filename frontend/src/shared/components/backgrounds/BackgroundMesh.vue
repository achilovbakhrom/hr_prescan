<script setup lang="ts">
/**
 * BackgroundMesh — 5 large blurred blobs drifting on coprime timers.
 * Uses mix-blend-mode: screen in dark / multiply in light for color interplay.
 * Reduced-motion: blobs freeze at their start positions.
 */
</script>

<template>
  <div aria-hidden="true" class="mesh-root pointer-events-none fixed inset-0 -z-10 overflow-hidden">
    <div class="mesh-blob mesh-blob--a" />
    <div class="mesh-blob mesh-blob--b" />
    <div class="mesh-blob mesh-blob--c" />
    <div class="mesh-blob mesh-blob--d" />
    <div class="mesh-blob mesh-blob--e" />
  </div>
</template>

<style scoped>
.mesh-root {
  isolation: isolate;
  background-color: transparent;
}

.mesh-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(var(--blur-xl));
  will-change: transform;
  opacity: 0.45;
  mix-blend-mode: multiply;
}

:global(.dark .mesh-blob) {
  opacity: 0.1;
  mix-blend-mode: screen;
}

/* -------- Blob A (blue) — 15%, 20% -------- */
.mesh-blob--a {
  top: 20%;
  left: 15%;
  width: 65vmin;
  height: 65vmin;
  transform: translate(-50%, -50%);
  background: #2563eb;
  animation: mesh-drift-a 14s ease-in-out infinite alternate;
}

/* -------- Blob B (ai-violet) — 75%, 30% -------- */
.mesh-blob--b {
  top: 30%;
  left: 75%;
  width: 70vmin;
  height: 70vmin;
  transform: translate(-50%, -50%);
  background: #7c5cff;
  animation: mesh-drift-b 17s ease-in-out infinite alternate;
}

/* -------- Blob C (celebrate-peach) — 50%, 55% -------- */
.mesh-blob--c {
  top: 55%;
  left: 50%;
  width: 80vmin;
  height: 80vmin;
  transform: translate(-50%, -50%);
  background: #ff9b73;
  animation: mesh-drift-c 19s ease-in-out infinite alternate;
}

/* -------- Blob D (soft-teal) — 20%, 80% -------- */
.mesh-blob--d {
  top: 80%;
  left: 20%;
  width: 55vmin;
  height: 55vmin;
  transform: translate(-50%, -50%);
  background: #06b6d4;
  animation: mesh-drift-d 21s ease-in-out infinite alternate;
}

/* -------- Blob E (soft-pink) — 85%, 75% -------- */
.mesh-blob--e {
  top: 75%;
  left: 85%;
  width: 50vmin;
  height: 50vmin;
  transform: translate(-50%, -50%);
  background: #f472b6;
  animation: mesh-drift-e 23s ease-in-out infinite alternate;
}

/* Each blob drifts −6% → +6% of viewport on both axes, no rotation. */
@keyframes mesh-drift-a {
  0% {
    transform: translate(calc(-50% - 6vw), calc(-50% - 6vh));
  }
  100% {
    transform: translate(calc(-50% + 6vw), calc(-50% + 6vh));
  }
}
@keyframes mesh-drift-b {
  0% {
    transform: translate(calc(-50% + 6vw), calc(-50% - 6vh));
  }
  100% {
    transform: translate(calc(-50% - 6vw), calc(-50% + 6vh));
  }
}
@keyframes mesh-drift-c {
  0% {
    transform: translate(calc(-50% - 5vw), calc(-50% + 6vh));
  }
  100% {
    transform: translate(calc(-50% + 5vw), calc(-50% - 6vh));
  }
}
@keyframes mesh-drift-d {
  0% {
    transform: translate(calc(-50% + 6vw), calc(-50% + 4vh));
  }
  100% {
    transform: translate(calc(-50% - 6vw), calc(-50% - 4vh));
  }
}
@keyframes mesh-drift-e {
  0% {
    transform: translate(calc(-50% - 4vw), calc(-50% - 6vh));
  }
  100% {
    transform: translate(calc(-50% + 4vw), calc(-50% + 6vh));
  }
}

@media (prefers-reduced-motion: reduce) {
  .mesh-blob {
    animation: none !important;
  }
}
</style>
