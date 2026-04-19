<script setup lang="ts">
/**
 * LandingStats — live-metric strip (replaces the old 3-up stat grid).
 * A single horizontal glass chip below the hero, showing 3 inline metrics
 * separated by faint dividers. The leading number gets a subtle
 * `accentPulse` ring to sell the "live" feel.
 *
 * NOTE: metrics here are plausible placeholders — wire to real telemetry
 * if/when the backend exposes a `/api/public/metrics` endpoint.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const TARGET = 12481
// Default to the final value so the number is always readable (incl. static
// screenshot / reduced-motion / slow-load paths). Counter-up is delight, not
// the content.
const candidatesScreened = ref(TARGET)

function formatNumber(n: number): string {
  return n.toLocaleString('en-US')
}

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  // Animate from 0 → TARGET on mount as a delight pass.
  candidatesScreened.value = 0
  const duration = 1400
  const fps = 60
  const frames = (duration / 1000) * fps
  let frame = 0
  const interval = setInterval(() => {
    frame++
    const progress = frame / frames
    const eased = 1 - Math.pow(1 - progress, 3)
    candidatesScreened.value = Math.round(eased * TARGET)
    if (frame >= frames) {
      candidatesScreened.value = TARGET
      clearInterval(interval)
    }
  }, 1000 / fps)
})
</script>

<template>
  <section class="scroll-animate px-4 pb-12 pt-4 sm:px-6 sm:pb-20 sm:pt-6">
    <div class="mx-auto max-w-5xl">
      <div
        class="bg-glass-1 border-glass shadow-glass-float flex flex-col items-stretch justify-between gap-6 rounded-[--radius-lg] px-6 py-8 text-center sm:flex-row sm:items-center sm:gap-0 sm:divide-x sm:divide-[color:var(--color-border-soft)] sm:px-10 sm:py-10"
      >
        <!-- Metric 1: live candidates screened -->
        <div class="metric-item live-metric flex-1 px-4">
          <div class="metric-number font-mono font-semibold text-[color:var(--color-text-primary)]">
            {{ formatNumber(candidatesScreened) }}
          </div>
          <div
            class="mt-3 text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--color-text-muted)] sm:text-sm"
          >
            candidates screened this week
          </div>
        </div>

        <!-- Metric 2: speed -->
        <div class="flex-1 px-4">
          <div class="metric-number font-mono font-semibold text-[color:var(--color-accent-ai)]">
            3.2×
          </div>
          <div
            class="mt-3 text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--color-text-muted)] sm:text-sm"
          >
            {{ t('landing.stats.fasterScreening') }}
          </div>
        </div>

        <!-- Metric 3: satisfaction -->
        <div class="flex-1 px-4">
          <div
            class="metric-number font-mono font-semibold text-[color:var(--color-accent-celebrate)]"
          >
            94%
          </div>
          <div
            class="mt-3 text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--color-text-muted)] sm:text-sm"
          >
            HR satisfaction
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Metric number — use display type scale so the strip reads as confident,
   not decorative. Mobile stays large (clamp lower bound ~44px). */
.metric-number {
  font-size: clamp(2.5rem, 4.5vw, 3.75rem);
  line-height: 1;
  letter-spacing: -0.02em;
}

/* accentPulse ring on the leading "live" number — a bigger, more
   prominent double-ring so the "live" feel actually lands. */
.live-metric {
  position: relative;
}
.live-metric::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 12px;
  border-radius: 9999px;
  background: var(--color-success);
  box-shadow:
    0 0 0 6px color-mix(in srgb, var(--color-success) 24%, transparent),
    0 0 0 12px color-mix(in srgb, var(--color-success) 10%, transparent);
  animation: metric-pulse 1800ms ease-in-out infinite;
  pointer-events: none;
}
@keyframes metric-pulse {
  0%,
  100% {
    transform: translateX(-50%) scale(1);
    opacity: 0.95;
  }
  50% {
    transform: translateX(-50%) scale(1.25);
    opacity: 1;
  }
}
@media (min-width: 640px) {
  .live-metric::before {
    top: 10px;
    left: 18px;
    transform: none;
  }
  @keyframes metric-pulse {
    0%,
    100% {
      transform: scale(1);
      opacity: 0.95;
    }
    50% {
      transform: scale(1.25);
      opacity: 1;
    }
  }
}
@media (prefers-reduced-motion: reduce) {
  .live-metric::before {
    animation: none;
  }
}
</style>
