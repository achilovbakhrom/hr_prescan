<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const statsRef = ref<HTMLElement | null>(null)
const animated = ref(false)
const counters = ref({ fast: 0, saved: 0 })
let observer: IntersectionObserver | null = null

function animateCounters(): void {
  if (animated.value) return
  animated.value = true
  const duration = 1500
  const fps = 60
  const frames = (duration / 1000) * fps
  let frame = 0

  const interval = setInterval(() => {
    frame++
    const progress = frame / frames
    const eased = 1 - Math.pow(1 - progress, 3)
    counters.value.fast = Math.round(eased * 10)
    counters.value.saved = Math.round(eased * 90)
    if (frame >= frames) {
      counters.value.fast = 10
      counters.value.saved = 90
      clearInterval(interval)
    }
  }, 1000 / fps)
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        animateCounters()
        observer?.disconnect()
      }
    },
    { threshold: 0.3 },
  )
  if (statsRef.value) {
    observer.observe(statsRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <section ref="statsRef" class="border-y border-gray-100 dark:border-gray-800 bg-gray-50/50">
    <div
      class="mx-auto grid max-w-5xl grid-cols-1 divide-y divide-gray-200 dark:divide-gray-800 py-10 sm:grid-cols-3 sm:divide-x sm:divide-y-0"
    >
      <div class="py-6 text-center sm:py-0">
        <div class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">{{ counters.fast }}x</div>
        <div class="mt-1 text-sm text-gray-500">{{ t('landing.stats.fasterScreening') }}</div>
      </div>
      <div class="py-6 text-center sm:py-0">
        <div class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">{{ counters.saved }}%</div>
        <div class="mt-1 text-sm text-gray-500">{{ t('landing.stats.timeSaved') }}</div>
      </div>
      <div class="py-6 text-center sm:py-0">
        <div class="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">24/7</div>
        <div class="mt-1 text-sm text-gray-500">{{ t('landing.stats.available') }}</div>
      </div>
    </div>
  </section>
</template>
