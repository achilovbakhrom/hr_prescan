<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { CONSTELLATION_LINES as LINES, CONSTELLATION_NODES as NODES } from './constellationLayout'

/**
 * BackgroundConstellation — seeded jittered grid (32 nodes), each wired to its
 * 2 nearest neighbors. Layout computed once at module load (see
 * ./constellationLayout.ts) so reloads don't flash new positions.
 *
 * Pulse uses CSS transform: scale() (not SVG `r`) — transform-origin is set via
 * inline style per-circle to the node center because transform-box: fill-box
 * has spotty pre-2023 Safari support.
 *
 * Mouse parallax: desktop-only (pointer:fine) and motion-allowed only.
 * rAF-throttled, listener removed in onBeforeUnmount.
 */

const rootEl = ref<HTMLElement | null>(null)
let rafId: number | null = null
let pendingX = 0
let pendingY = 0
let parallaxActive = false

function onMouseMove(e: MouseEvent): void {
  pendingX = (e.clientX / window.innerWidth) * 2 - 1
  pendingY = (e.clientY / window.innerHeight) * 2 - 1
  if (rafId != null) return
  rafId = requestAnimationFrame(() => {
    rafId = null
    if (rootEl.value) {
      rootEl.value.style.setProperty('--parallax-x', String(pendingX))
      rootEl.value.style.setProperty('--parallax-y', String(pendingY))
    }
  })
}

onMounted(() => {
  const fine = window.matchMedia('(pointer: fine)').matches
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (fine && !reduced) {
    parallaxActive = true
    window.addEventListener('mousemove', onMouseMove, { passive: true })
  }
})

onBeforeUnmount(() => {
  if (parallaxActive) window.removeEventListener('mousemove', onMouseMove)
  if (rafId != null) cancelAnimationFrame(rafId)
})
</script>

<template>
  <div
    ref="rootEl"
    aria-hidden="true"
    class="constellation-root pointer-events-none fixed inset-0 -z-10 overflow-hidden"
  >
    <svg class="constellation-svg" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
      <g class="constellation-lines">
        <line
          v-for="(l, i) in LINES"
          :key="`l-${i}`"
          :x1="l.x1"
          :y1="l.y1"
          :x2="l.x2"
          :y2="l.y2"
          stroke="var(--color-accent-ai)"
          stroke-width="0.5"
          stroke-opacity="0.15"
        />
      </g>
      <g class="constellation-nodes">
        <circle
          v-for="(n, i) in NODES"
          :key="`n-${i}`"
          :cx="n.x"
          :cy="n.y"
          r="2.5"
          fill="var(--color-accent-ai)"
          opacity="0.6"
          class="constellation-node"
          :style="{
            animationDelay: `${i * 0.13}s`,
            transformOrigin: `${n.x}px ${n.y}px`,
          }"
        />
      </g>
    </svg>
  </div>
</template>

<style scoped>
.constellation-root {
  --parallax-x: 0;
  --parallax-y: 0;
  isolation: isolate;
}

.constellation-svg {
  width: 100%;
  height: 100%;
  display: block;
  transform: translate(calc(var(--parallax-x) * 10px), calc(var(--parallax-y) * 10px));
  transition: transform 240ms var(--ease-out-soft);
  will-change: transform;
}

.constellation-node {
  animation: constellation-pulse 5s ease-in-out infinite;
}

@keyframes constellation-pulse {
  0%,
  100% {
    opacity: 0.6;
    transform: scale(0.85);
  }
  50% {
    opacity: 1;
    transform: scale(1.25);
  }
}

@media (prefers-reduced-motion: reduce) {
  .constellation-node {
    animation: none !important;
  }
  .constellation-svg {
    transform: none !important;
    transition: none !important;
  }
}
</style>
