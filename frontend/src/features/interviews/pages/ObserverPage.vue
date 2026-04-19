<script setup lang="ts">
/**
 * ObserverPage — HR live observation of an ongoing interview.
 * 2-column on desktop: live transcript (left) + score-criteria sidebar (right).
 * Spec: docs/design/spec.md §9 Interviews (HR Observer).
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import TranscriptView from '../components/TranscriptView.vue'
import InterviewScoresView from '../components/InterviewScoresView.vue'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import { useInterviewStore } from '../stores/interview.store'
import ConnectionStatus from '@/features/video/components/ConnectionStatus.vue'
import { useLiveKit } from '@/features/video/composables/useLiveKit'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

const livekitUrl = computed(() => import.meta.env.VITE_LIVEKIT_URL || 'wss://localhost:7880')

const { connectionState, error: livekitError, connectAsObserver, disconnect } = useLiveKit()
const isJoined = ref(false)

onMounted(async () => {
  await interviewStore.fetchInterviewDetail(interviewId.value)
  if (interview.value && interview.value.status === 'in_progress') {
    try {
      const token = await interviewStore.getObserverToken(interviewId.value)
      await connectAsObserver({
        url: livekitUrl.value,
        token,
        roomName: interview.value.livekitRoomName,
      })
      isJoined.value = true
    } catch {
      /* error set in store or livekit composable */
    }
  }
})

async function handleLeave(): Promise<void> {
  await disconnect()
  router.back()
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-[color:var(--color-text-muted)] transition-colors hover:text-[color:var(--color-text-primary)]"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
        {{ t('interviews.observerPage.title') }}
      </h1>
    </div>

    <p v-if="interviewStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ interviewStore.error }}
    </p>
    <p v-if="livekitError" class="text-sm text-[color:var(--color-danger)]">
      {{ livekitError }}
    </p>

    <div v-if="interviewStore.loading && !interview" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-if="interview">
      <!-- Not in progress banner -->
      <GlassCard v-if="interview.status !== 'in_progress' && !isJoined" accent="ai">
        <div class="flex flex-col items-center gap-3 py-6 text-center">
          <i class="pi pi-info-circle text-3xl text-[color:var(--color-warning)]"></i>
          <p class="text-[color:var(--color-text-primary)]">
            {{ t('interviews.observerPage.notInProgress') }}
          </p>
          <InterviewStatusBadge :status="interview.status" />
        </div>
      </GlassCard>

      <!-- Joined observer view -->
      <template v-if="isJoined">
        <!-- Status bar -->
        <GlassSurface class="flex items-center justify-between rounded-lg p-3" level="1">
          <div class="flex items-center gap-3">
            <ConnectionStatus :state="connectionState" />
            <span
              class="rounded bg-[color:var(--color-accent-ai-soft)] px-2 py-1 text-xs font-medium text-[color:var(--color-accent-ai)]"
            >
              {{ t('interviews.observerPage.observerMode') }}
            </span>
          </div>
          <div class="hidden text-sm text-[color:var(--color-text-secondary)] sm:block">
            <span class="font-medium">{{ interview.candidateName }}</span>
            <span class="mx-2 text-[color:var(--color-text-muted)]">|</span>
            <span>{{ interview.vacancyTitle }}</span>
          </div>
        </GlassSurface>

        <!-- 2-column: transcript | scores -->
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_20rem]">
          <GlassCard :title="t('interviews.detailPage.tabTranscript')">
            <TranscriptView :transcript="interview.transcript" />
          </GlassCard>

          <aside class="space-y-4">
            <GlassCard :title="t('interviews.detailPage.tabScores')">
              <InterviewScoresView :scores="interview.scores" />
            </GlassCard>

            <GlassCard class="text-center">
              <div
                class="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-[color:var(--color-surface-sunken)]"
              >
                <i class="pi pi-headphones text-2xl text-[color:var(--color-text-muted)]"></i>
              </div>
              <p class="text-sm text-[color:var(--color-text-secondary)]">
                {{ t('interviews.observerPage.listeningAudio') }}
              </p>
              <p class="mt-1 text-xs text-[color:var(--color-text-muted)]">
                {{ t('interviews.observerPage.audioOnlyNote') }}
              </p>
            </GlassCard>
          </aside>
        </div>

        <div class="flex justify-center">
          <Button
            :label="t('interviews.observerPage.leaveObservation')"
            icon="pi pi-sign-out"
            severity="secondary"
            @click="handleLeave"
          />
        </div>
      </template>
    </template>
  </div>
</template>
