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
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const TARGET = 12481
const candidatesScreened = ref(TARGET)
const metrics = computed(() => [
  {
    value: formatNumber(candidatesScreened.value),
    label: t('landing.stats.interviews'),
    tone: 'primary',
    live: true,
    featured: true,
  },
  { value: '3.2×', label: t('landing.stats.fasterScreening'), tone: 'ai' },
  { value: '94%', label: t('landing.stats.satisfaction'), tone: 'celebrate' },
  { value: '24/7', label: t('landing.stats.available'), tone: 'success' },
])

function formatNumber(n: number): string {
  return n.toLocaleString('en-US')
}

function numberClass(tone: string): string {
  switch (tone) {
    case 'ai':
      return 'text-[color:var(--color-accent-ai)]'
    case 'celebrate':
      return 'text-[color:var(--color-accent-celebrate)]'
    case 'success':
      return 'text-[color:var(--color-success)]'
    default:
      return 'text-[color:var(--color-text-primary)]'
  }
}

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
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
    <div class="mx-auto max-w-7xl">
      <div
        class="bg-glass-1 border-glass shadow-glass-float grid gap-4 rounded-[32px] p-4 sm:p-6 xl:grid-cols-[minmax(0,1.5fr)_repeat(3,minmax(0,1fr))]"
      >
        <div
          v-for="metric in metrics"
          :key="metric.label"
          class="relative rounded-[26px] border border-[color:var(--color-border-glass)] bg-white/58 px-5 py-6 text-left shadow-[0_14px_40px_rgba(15,23,42,0.06)] backdrop-blur-xl dark:bg-white/5"
          :class="metric.featured ? 'live-metric xl:row-span-1' : ''"
        >
          <div class="metric-number font-mono font-semibold" :class="numberClass(metric.tone)">
            {{ metric.value }}
          </div>
          <div
            class="mt-3 text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--color-text-muted)] sm:text-sm"
          >
            {{ metric.label }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.metric-number {
  font-size: clamp(2.5rem, 4.5vw, 3.75rem);
  line-height: 1;
  letter-spacing: -0.02em;
}

.live-metric {
  position: relative;
}
.live-metric::before {
  content: '';
  position: absolute;
  top: 24px;
  right: 24px;
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
    transform: scale(1);
    opacity: 0.95;
  }
  50% {
    transform: scale(1.25);
    opacity: 1;
  }
}
@media (prefers-reduced-motion: reduce) {
  .live-metric::before {
    animation: none;
  }
}
</style>
