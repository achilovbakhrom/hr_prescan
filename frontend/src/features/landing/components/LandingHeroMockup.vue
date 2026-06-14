<script setup lang="ts">
/**
 * LandingHeroMockup — Figma hero preview: a violet→magenta gradient card
 * holding a live AI-interview frame (rotating candidate photo), a question
 * row, and an "Advancing to interview · 9.2 / 10" score. Decorative.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Rotating candidate — a fresh face/name on each page load.
const CANDIDATES = [
  { img: '/landing/interview-1.jpg', name: 'James Cole', role: 'Senior Frontend Engineer' },
  { img: '/landing/interview-2.jpg', name: 'Aisha Patel', role: 'Product Designer' },
  { img: '/landing/interview-3.jpg', name: 'Maria Santos', role: 'Frontend Engineer' },
  { img: '/landing/interview-4.jpg', name: 'Elena Rossi', role: 'Backend Engineer' },
  { img: '/landing/interview-5.jpg', name: 'David Kim', role: 'Platform Engineer' },
  { img: '/landing/interview-6.jpg', name: 'Tom Becker', role: 'Backend Engineer' },
  { img: '/landing/interview-7.jpg', name: 'Alex Morgan', role: 'Senior Frontend Engineer' },
  { img: '/landing/interview-8.jpg', name: 'Marco Linden', role: 'Platform Engineer' },
]
const candidate = ref(CANDIDATES[0]!)
onMounted(() => {
  candidate.value = CANDIDATES[Math.floor(Math.random() * CANDIDATES.length)]!
})
</script>

<template>
  <div
    class="relative w-full overflow-hidden rounded-[26px] bg-[linear-gradient(150deg,#7c3aed,#a855f7_45%,#ec4899)] p-4 text-white shadow-[0_40px_90px_-24px_rgba(124,58,237,0.55)]"
  >
    <!-- Head -->
    <div class="flex items-center justify-between px-1 pb-3">
      <span class="flex items-center gap-2 text-xs font-medium">
        <span class="h-2 w-2 rounded-full bg-emerald-300"></span>
        {{ t('landing.heroPreview.live') }}
      </span>
      <span class="font-mono text-xs text-white/80">02:14</span>
    </div>

    <!-- Video frame -->
    <div class="relative h-[264px] overflow-hidden rounded-[18px]">
      <img
        :src="candidate.img"
        alt=""
        class="absolute inset-0 h-full w-full object-cover object-[center_22%]"
      />
      <!-- bottom legibility scrim -->
      <div
        class="absolute inset-x-0 bottom-0 h-2/5"
        style="background: linear-gradient(to top, rgba(0, 0, 0, 0.55), transparent)"
      ></div>
      <!-- REC badge -->
      <span
        class="absolute left-3 top-3 flex items-center gap-1.5 rounded-full bg-black/35 px-2.5 py-1 text-[10px] font-semibold backdrop-blur-sm"
      >
        <span class="h-1.5 w-1.5 rounded-full bg-red-500"></span>REC
      </span>
      <!-- name / role -->
      <div class="absolute bottom-3 left-3">
        <p class="text-sm font-semibold leading-tight">{{ candidate.name }}</p>
        <p class="text-xs text-white/80">{{ candidate.role }}</p>
      </div>
    </div>

    <!-- Question row (glass) -->
    <div class="mt-3 flex items-start gap-3 rounded-[16px] bg-white/15 p-3 backdrop-blur-md">
      <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white/25">
        <i class="pi pi-sparkles text-xs"></i>
      </span>
      <p class="text-sm leading-snug">{{ t('landing.heroPreview.question') }}</p>
    </div>

    <!-- Score row -->
    <div class="mt-3 flex items-end justify-between px-1">
      <div class="leading-tight">
        <p class="text-[11px] uppercase tracking-wide text-white/70">
          {{ t('landing.heroPreview.overallScore') }}
        </p>
        <p class="text-sm font-semibold">{{ t('landing.heroPreview.advancing') }}</p>
      </div>
      <span class="rounded-xl bg-black/25 px-3 py-1.5 font-mono text-sm font-bold backdrop-blur-sm">
        9.2 / 10
      </span>
    </div>
  </div>
</template>
