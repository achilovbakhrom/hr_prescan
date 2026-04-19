<script setup lang="ts">
/**
 * CandidateInterviewPage — the `/my-interview/:id` pre-interview briefing.
 *
 * Distinction from InterviewGatewayPage:
 * - Gateway (`/interview/:token`) is the token-based entry from the email
 *   link; it's a redirect hub that sends the candidate to chat or room.
 * - CandidateInterviewPage is the authenticated candidate's interview
 *   landing inside the app (PublicLayout via candidateInterviewRoutes);
 *   it shows a scheduled interview and a "Join" CTA.
 *
 * T13 redesign: glass card on ambient background; prescan-style pre-check
 * and device-test hints.
 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const isCompleted = computed(() => interview.value?.status === 'completed')
const isScheduled = computed(() => interview.value?.status === 'pending')
const isInProgress = computed(() => interview.value?.status === 'in_progress')

onMounted(() => interviewStore.fetchCandidateInterview(interviewId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function handleJoinInterview(): void {
  router.push({ name: ROUTE_NAMES.INTERVIEW_ROOM, params: { id: interviewId.value } })
}
</script>

<template>
  <div class="mx-auto max-w-lg py-10">
    <div v-if="!interview && interviewStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <p v-if="interviewStore.error" class="mb-4 text-sm text-[color:var(--color-danger)]">
      {{ interviewStore.error }}
    </p>

    <template v-if="interview">
      <!-- Completed -->
      <GlassCard v-if="isCompleted" accent="celebrate" class="text-center">
        <div
          class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
        >
          <i class="pi pi-check-circle text-3xl text-[color:var(--color-accent-celebrate)]"></i>
        </div>
        <h1 class="mb-2 text-2xl font-semibold text-[color:var(--color-text-primary)]">
          {{ t('interviews.candidatePage.thankYou') }}
        </h1>
        <p class="text-sm text-[color:var(--color-text-secondary)]">
          {{ t('interviews.candidatePage.completedMessage') }}
        </p>
      </GlassCard>

      <!-- Pre-interview briefing -->
      <GlassCard v-else>
        <div class="mb-6 flex items-center gap-3">
          <AppLogo variant="glyph" size="md" :linked="false" />
          <h1 class="text-2xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.candidatePage.yourInterview') }}
          </h1>
        </div>

        <div class="space-y-4">
          <div class="bg-glass-2 rounded-md border border-[color:var(--color-border-soft)] p-4">
            <dl class="space-y-2 text-sm">
              <div class="flex justify-between">
                <dt class="text-[color:var(--color-text-muted)]">
                  {{ t('interviews.preCheck.position') }}
                </dt>
                <dd class="font-medium text-[color:var(--color-text-primary)]">
                  {{ interview.vacancyTitle }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-[color:var(--color-text-muted)]">
                  {{ t('interviews.preCheck.scheduled') }}
                </dt>
                <dd class="font-mono text-xs text-[color:var(--color-text-primary)]">
                  {{ formatDate(interview.createdAt) }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-[color:var(--color-text-muted)]">
                  {{ t('interviews.preCheck.duration') }}
                </dt>
                <dd class="font-mono text-xs text-[color:var(--color-text-primary)]">
                  {{
                    t('interviews.preCheck.durationMinutes', {
                      minutes: interview.durationMinutes,
                    })
                  }}
                </dd>
              </div>
              <div class="flex items-center justify-between">
                <dt class="text-[color:var(--color-text-muted)]">
                  {{ t('common.status') }}
                </dt>
                <dd>
                  <InterviewStatusBadge :status="interview.status" />
                </dd>
              </div>
            </dl>
          </div>

          <div
            class="rounded-md border border-[color:var(--color-accent-ai)]/30 bg-[color:var(--color-accent-ai-soft)] p-4"
          >
            <h3 class="mb-2 text-sm font-semibold text-[color:var(--color-accent-ai)]">
              {{ t('interviews.candidatePage.instructions') }}
            </h3>
            <ul
              class="list-inside list-disc space-y-1 text-sm text-[color:var(--color-text-secondary)]"
            >
              <li>{{ t('interviews.preCheck.stableConnection') }}</li>
              <li>{{ t('interviews.preCheck.quietRoom') }}</li>
              <li>{{ t('interviews.preCheck.allowCameraMicAccess') }}</li>
              <li>{{ t('interviews.preCheck.faceVisible') }}</li>
            </ul>
          </div>

          <div class="rounded-md border border-[color:var(--color-border-soft)] p-4">
            <h3 class="mb-2 text-sm font-semibold text-[color:var(--color-text-secondary)]">
              {{ t('interviews.candidatePage.cameraMicTest') }}
            </h3>
            <p class="text-xs text-[color:var(--color-text-muted)]">
              {{ t('interviews.candidatePage.deviceTestNote') }}
            </p>
          </div>

          <Button
            v-if="isScheduled || isInProgress"
            :label="t('interviews.candidatePage.joinInterview')"
            icon="pi pi-video"
            class="w-full"
            size="large"
            @click="handleJoinInterview"
          />
        </div>
      </GlassCard>
    </template>
  </div>
</template>
