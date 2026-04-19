<script setup lang="ts">
/**
 * CandidateScoreCard — displays the big overall score number in a glass
 * card, with an accent ring that pulses when the score is AI-derived.
 * Per-criteria breakdown renders below as rows: label / 1-10 / weighted.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'

const props = defineProps<{
  overallScore: number | null | undefined
  prescanningScore?: number | null
  interviewScore?: number | null
  /** 0-100 CV match score */
  cvMatchScore?: number | null
}>()

const { t } = useI18n()

const displayScore = computed(() =>
  props.overallScore == null ? '—' : String(Math.round(props.overallScore)),
)

const scoreColor = computed(() => {
  const s = props.overallScore
  if (s == null) return 'var(--color-text-muted)'
  if (s >= 75) return 'var(--color-success)'
  if (s >= 55) return 'var(--color-warning)'
  return 'var(--color-danger)'
})

const hasAnyScore = computed(
  () =>
    props.overallScore != null ||
    props.prescanningScore != null ||
    props.interviewScore != null ||
    props.cvMatchScore != null,
)
</script>

<template>
  <GlassCard>
    <div class="flex flex-col items-center gap-4">
      <!-- Big ring w/ score -->
      <div class="score-ring relative flex h-32 w-32 items-center justify-center">
        <span class="score-number font-mono text-5xl font-semibold" :style="{ color: scoreColor }">
          {{ displayScore }}
        </span>
      </div>
      <p class="text-xs uppercase tracking-wider text-[color:var(--color-text-muted)]">
        {{ t('candidates.overallScore', 'Overall score') }}
      </p>

      <!-- Criteria breakdown (rows) -->
      <div v-if="hasAnyScore" class="w-full space-y-2">
        <div
          v-if="cvMatchScore != null"
          class="flex items-center justify-between rounded-md bg-[color:var(--color-surface-sunken)] px-3 py-2"
        >
          <span class="text-sm text-[color:var(--color-text-secondary)]">{{
            t('candidates.cv', 'CV match')
          }}</span>
          <span class="font-mono text-sm font-semibold text-[color:var(--color-text-primary)]"
            >{{ cvMatchScore }}%</span
          >
        </div>
        <div
          v-if="prescanningScore != null"
          class="flex items-center justify-between rounded-md bg-[color:var(--color-surface-sunken)] px-3 py-2"
        >
          <span class="text-sm text-[color:var(--color-text-secondary)]">{{
            t('candidates.prescanning')
          }}</span>
          <span class="font-mono text-sm font-semibold text-[color:var(--color-text-primary)]"
            >{{ prescanningScore.toFixed(1) }}/10</span
          >
        </div>
        <div
          v-if="interviewScore != null"
          class="flex items-center justify-between rounded-md bg-[color:var(--color-surface-sunken)] px-3 py-2"
        >
          <span class="text-sm text-[color:var(--color-text-secondary)]">{{
            t('candidates.interview')
          }}</span>
          <span class="font-mono text-sm font-semibold text-[color:var(--color-text-primary)]"
            >{{ interviewScore.toFixed(1) }}/10</span
          >
        </div>
      </div>
    </div>
  </GlassCard>
</template>

<style scoped>
.score-ring::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid v-bind(scoreColor);
  opacity: 0.9;
  animation: accent-pulse 1600ms ease-in-out infinite;
}
@keyframes accent-pulse {
  0%,
  100% {
    opacity: 0.75;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.03);
  }
}
@media (prefers-reduced-motion: reduce) {
  .score-ring::before {
    animation: none;
    opacity: 1;
  }
}
</style>
