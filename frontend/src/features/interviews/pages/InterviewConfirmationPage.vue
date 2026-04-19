<script setup lang="ts">
/**
 * InterviewConfirmationPage — post-scheduling "you're booked" page.
 *
 * T13 redesign: celebrate-accented GlassCard with the Prism glyph. Uses
 * the peach celebrate tint. Route lives under PublicLayout.
 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import { useInterviewStore } from '../stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

onMounted(() => interviewStore.fetchCandidateInterview(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleDownloadCalendar(): void {
  window.alert('Calendar invite download will be available in a future release.')
}

function handleGoToInterview(): void {
  router.push({
    name: ROUTE_NAMES.CANDIDATE_INTERVIEW,
    params: { id: interviewId.value },
  })
}
</script>

<template>
  <div class="mx-auto max-w-lg py-10">
    <div v-if="!interview && interviewStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <GlassCard v-else-if="interview" accent="celebrate" class="text-center">
      <!-- Prism + celebrate glow -->
      <div class="relative mx-auto mb-4 flex items-center justify-center">
        <div
          class="absolute inset-0 mx-auto h-20 w-20 animate-[celebrate-pulse_2s_ease-in-out_infinite] rounded-full bg-[color:var(--color-accent-celebrate-soft)] blur-xl"
        ></div>
        <div class="relative">
          <AppLogo variant="glyph" size="lg" :linked="false" />
        </div>
      </div>

      <h1 class="mb-2 text-2xl font-semibold text-[color:var(--color-text-primary)]">
        {{ t('interviews.status.scheduled') }}!
      </h1>
      <p class="mb-6 text-sm text-[color:var(--color-text-secondary)]">
        {{ t('interviews.confirmationPage.confirmed') }}
      </p>

      <div
        class="bg-glass-2 mb-6 rounded-md border border-[color:var(--color-border-soft)] p-4 text-left"
      >
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between">
            <dt class="text-[color:var(--color-text-muted)]">
              {{ t('interviews.confirmationPage.date') }}
            </dt>
            <dd class="font-medium text-[color:var(--color-text-primary)]">
              {{ formatDate(interview.createdAt) }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-[color:var(--color-text-muted)]">
              {{ t('interviews.confirmationPage.time') }}
            </dt>
            <dd class="font-mono text-xs text-[color:var(--color-text-primary)]">
              {{ formatTime(interview.createdAt) }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-[color:var(--color-text-muted)]">
              {{ t('interviews.preCheck.duration') }}
            </dt>
            <dd class="font-mono text-xs text-[color:var(--color-text-primary)]">
              {{ t('interviews.preCheck.durationMinutes', { minutes: interview.durationMinutes }) }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-[color:var(--color-text-muted)]">
              {{ t('interviews.preCheck.position') }}
            </dt>
            <dd class="font-medium text-[color:var(--color-text-primary)]">
              {{ interview.vacancyTitle }}
            </dd>
          </div>
        </dl>
      </div>

      <div class="flex flex-col gap-3">
        <Button
          :label="t('interviews.confirmationPage.downloadCalendar')"
          icon="pi pi-download"
          severity="secondary"
          outlined
          @click="handleDownloadCalendar"
        />
        <Button
          :label="t('interviews.confirmationPage.goToRoom')"
          icon="pi pi-video"
          @click="handleGoToInterview"
        />
      </div>
    </GlassCard>
  </div>
</template>

<style scoped>
@keyframes celebrate-pulse {
  0%,
  100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.08);
  }
}

@media (prefers-reduced-motion: reduce) {
  [class*='celebrate-pulse'] {
    animation: none !important;
    opacity: 0.8;
  }
}
</style>
