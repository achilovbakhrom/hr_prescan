<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'

const { t } = useI18n()
const activeFrame = ref(0)
const isPlaying = ref(false)
let playbackTimer: number | undefined

const frames = computed(() => [
  {
    icon: 'pi pi-filter',
    title: t('landing.video.frame1Title'),
    text: t('landing.video.frame1Text'),
  },
  {
    icon: 'pi pi-sparkles',
    title: t('landing.video.frame2Title'),
    text: t('landing.video.frame2Text'),
  },
  {
    icon: 'pi pi-link',
    title: t('landing.video.frame3Title'),
    text: t('landing.video.frame3Text'),
  },
  {
    icon: 'pi pi-chart-line',
    title: t('landing.video.frame4Title'),
    text: t('landing.video.frame4Text'),
  },
])

const currentTime = computed(() => `00:${String((activeFrame.value + 1) * 14).padStart(2, '0')}`)

const stopPlayback = () => {
  isPlaying.value = false
  if (playbackTimer) {
    window.clearInterval(playbackTimer)
    playbackTimer = undefined
  }
}

const startPlayback = () => {
  stopPlayback()
  isPlaying.value = true
  playbackTimer = window.setInterval(() => {
    activeFrame.value = (activeFrame.value + 1) % frames.value.length
  }, 1700)
}

const togglePlayback = () => {
  if (isPlaying.value) {
    stopPlayback()
    return
  }
  startPlayback()
}

const playFrame = (index: number) => {
  activeFrame.value = index
  startPlayback()
}

onBeforeUnmount(stopPlayback)
</script>

<template>
  <section id="intro-video" class="px-4 py-20 sm:px-6 md:py-28">
    <div class="mx-auto grid max-w-7xl items-center gap-8 lg:grid-cols-[0.9fr_1.1fr]">
      <div class="scroll-animate">
        <p
          class="mb-3 text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--color-accent-ai)]"
        >
          {{ t('landing.video.eyebrow') }}
        </p>
        <h2
          class="max-w-xl text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl md:text-5xl"
        >
          {{ t('landing.video.title') }}
        </h2>
        <p class="mt-5 max-w-xl text-base leading-relaxed text-[color:var(--color-text-secondary)]">
          {{ t('landing.video.subtitle') }}
        </p>
      </div>

      <GlassCard class="scroll-animate overflow-hidden p-0">
        <div class="relative min-h-[360px] bg-[color:var(--color-surface-raised)] p-5 sm:p-6">
          <div
            class="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,var(--color-accent-ai),var(--color-accent-celebrate),var(--color-accent))]"
          ></div>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-semibold text-[color:var(--color-text-primary)]">
                {{ t('landing.video.playerTitle') }}
              </p>
              <p class="mt-1 text-xs text-[color:var(--color-text-muted)]">
                {{ currentTime }} / 00:58
              </p>
            </div>
            <button
              type="button"
              class="group flex h-12 w-12 items-center justify-center rounded-full bg-[color:var(--color-accent)] text-white shadow-[0_16px_42px_rgba(59,130,246,0.28)] transition-transform hover:scale-105"
              :aria-label="t('landing.video.play')"
              :aria-pressed="isPlaying"
              @click="togglePlayback"
            >
              <i :class="[isPlaying ? 'pi pi-pause' : 'pi pi-play ml-0.5', 'text-sm']"></i>
            </button>
          </div>

          <div class="mt-8 grid gap-3 sm:grid-cols-2">
            <button
              v-for="(frame, index) in frames"
              :key="frame.title"
              type="button"
              class="video-frame rounded-2xl border bg-white/70 p-4 text-left shadow-[0_12px_36px_rgba(15,23,42,0.06)] backdrop-blur-xl transition-all hover:-translate-y-1 dark:bg-white/5"
              :class="
                activeFrame === index
                  ? 'border-[color:var(--color-accent-ai)] ring-2 ring-[color:var(--color-accent-ai-soft)]'
                  : 'border-[color:var(--color-border-glass)]'
              "
              :style="{ animationDelay: `${index * 160}ms` }"
              @click="playFrame(index)"
            >
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]"
              >
                <i :class="frame.icon"></i>
              </div>
              <h3 class="mt-4 text-sm font-semibold text-[color:var(--color-text-primary)]">
                {{ frame.title }}
              </h3>
              <p class="mt-2 text-xs leading-relaxed text-[color:var(--color-text-secondary)]">
                {{ frame.text }}
              </p>
            </button>
          </div>

          <div
            class="mt-6 h-2 overflow-hidden rounded-full bg-[color:var(--color-surface-sunken)]"
            aria-hidden="true"
          >
            <div
              class="video-progress h-full rounded-full"
              :class="{ 'is-playing': isPlaying }"
              :style="{ width: `${((activeFrame + 1) / frames.length) * 100}%` }"
            ></div>
          </div>
        </div>
      </GlassCard>
    </div>
  </section>
</template>

<style scoped>
.video-frame {
  animation: frame-float 4.8s ease-in-out infinite;
}
.video-progress {
  background: linear-gradient(
    90deg,
    var(--color-accent-ai),
    var(--color-accent-celebrate),
    var(--color-accent)
  );
  transition: width 420ms ease;
}
.video-progress.is-playing {
  animation: progress-pulse 1.7s ease-in-out infinite;
}
@keyframes frame-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}
@keyframes progress-pulse {
  0% {
    filter: saturate(1);
  }
  50% {
    filter: saturate(1.35);
  }
  100% {
    filter: saturate(1);
  }
}
@media (prefers-reduced-motion: reduce) {
  .video-frame,
  .video-progress {
    animation: none;
  }
}
</style>
