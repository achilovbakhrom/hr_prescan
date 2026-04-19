<script setup lang="ts">
/**
 * InterviewDetailPage — single-interview HR view.
 * Header GlassCard + AI summary (accent="ai") + tabs for
 * Scores / Transcript / Integrity / Recording.
 * Spec: docs/design/spec.md §9 Interviews (HR detail).
 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import GlassCard from '@/shared/components/GlassCard.vue'
import { useInterviewStore } from '../stores/interview.store'
import InterviewDetailHeader from '../components/InterviewDetailHeader.vue'
import InterviewScoresView from '../components/InterviewScoresView.vue'
import TranscriptView from '../components/TranscriptView.vue'
import IntegrityFlagsView from '../components/IntegrityFlagsView.vue'
import TranslatableText from '@/shared/components/TranslatableText.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const interviewStore = useInterviewStore()

const TAB_NAMES = ['scores', 'transcript', 'integrity', 'recording'] as const
const activeTab = computed({
  get: () => {
    const tab = route.query.tab as string
    const idx = TAB_NAMES.indexOf(tab as (typeof TAB_NAMES)[number])
    return idx >= 0 ? idx : 0
  },
  set: (val: number) => {
    router.replace({ query: { ...route.query, tab: TAB_NAMES[val] } })
  },
})

const interviewId = computed(() => route.params.id as string)
const interview = computed(() => interviewStore.currentInterview)

onMounted(() => interviewStore.fetchInterviewDetail(interviewId.value))

async function handleCancel(): Promise<void> {
  await interviewStore.cancelInterview(interviewId.value).catch(() => {})
}

async function handleWatchLive(): Promise<void> {
  try {
    const token = await interviewStore.getObserverToken(interviewId.value)
    window.alert(`Observer token: ${token}\n\nLiveKit integration coming in Phase 7.`)
  } catch {
    /* error set in store */
  }
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
        {{ t('interviews.detailPage.title') }}
      </h1>
    </div>

    <p v-if="interviewStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ interviewStore.error }}
    </p>

    <div v-if="!interview && interviewStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="interview">
      <InterviewDetailHeader
        :interview="interview"
        :loading="interviewStore.loading"
        @cancel="handleCancel"
        @watch-live="handleWatchLive"
      />

      <!-- AI summary (AI-accent glass card) -->
      <GlassCard v-if="interview.aiSummary" accent="ai">
        <div class="flex items-start gap-3">
          <span
            class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]"
          >
            <i class="pi pi-sparkles text-sm"></i>
          </span>
          <div class="min-w-0 flex-1">
            <p
              class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-accent-ai)]"
            >
              {{ t('candidates.aiSummary', 'AI summary') }}
            </p>
            <TranslatableText
              :text="interview.aiSummary"
              :translations="interview.aiSummaryTranslations || {}"
              model="interview"
              :object-id="interview.id"
              field="ai_summary"
              @translated="
                (tr) => {
                  if (interview) interview.aiSummaryTranslations = tr
                }
              "
            >
              <template #default="{ text }">
                <p class="mt-1 text-sm text-[color:var(--color-text-primary)]">{{ text }}</p>
              </template>
            </TranslatableText>
          </div>
        </div>
      </GlassCard>

      <TabView v-model:activeIndex="activeTab">
        <TabPanel value="0" :header="t('interviews.detailPage.tabScores')">
          <div class="py-3">
            <GlassCard>
              <InterviewScoresView :scores="interview.scores" />
            </GlassCard>
          </div>
        </TabPanel>
        <TabPanel value="1" :header="t('interviews.detailPage.tabTranscript')">
          <div class="py-3">
            <GlassCard>
              <TranscriptView :transcript="interview.transcript" />
            </GlassCard>
          </div>
        </TabPanel>
        <TabPanel value="2" :header="t('interviews.detailPage.tabIntegrity')">
          <div class="py-3">
            <GlassCard>
              <IntegrityFlagsView :flags="interview.integrityFlags" />
            </GlassCard>
          </div>
        </TabPanel>
        <TabPanel value="3" :header="t('interviews.detailPage.tabRecording')">
          <div class="py-3">
            <GlassCard>
              <div v-if="interview.recordingPath">
                <p class="mb-2 text-sm font-medium text-[color:var(--color-text-primary)]">
                  {{ t('interviews.detailPage.recordingPath') }}
                </p>
                <code class="break-all font-mono text-sm text-[color:var(--color-text-secondary)]">
                  {{ interview.recordingPath }}
                </code>
                <p class="mt-4 text-xs text-[color:var(--color-text-muted)]">
                  {{ t('interviews.detailPage.playbackNote') }}
                </p>
              </div>
              <p v-else class="text-sm text-[color:var(--color-text-muted)]">
                {{ t('interviews.detailPage.noRecording') }}
              </p>
            </GlassCard>
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
