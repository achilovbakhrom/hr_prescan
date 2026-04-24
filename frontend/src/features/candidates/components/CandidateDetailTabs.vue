<script setup lang="ts">
/**
 * CandidateDetailTabs — TabView for the HR candidate-detail page.
 * Extracted from the page shell so the page stays under the 200-line cap.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import GlassCard from '@/shared/components/GlassCard.vue'
import CandidateOverview from './CandidateOverview.vue'
import CvDataView from './CvDataView.vue'
import MatchScoreView from './MatchScoreView.vue'
import HRNotesPanel from './HRNotesPanel.vue'
import InterviewReviewPanel from './InterviewReviewPanel.vue'
import type { ApplicationDetail } from '../types/candidate.types'

const props = defineProps<{
  candidate: ApplicationDetail
  loading: boolean
  activeTab: number
  prescanningScore: number | null
  interviewScore: number | null
  aiSummary: string | null
  aiSummaryTranslations: Record<string, string>
  aiSummaryInterviewId: string | null
}>()

const emit = defineEmits<{
  'update:activeTab': [value: number]
  'update:aiSummaryTranslations': [tr: Record<string, string>]
  saveNotes: [note: string]
  downloadCv: []
}>()

const { t } = useI18n()
const hasInterview = computed(() => props.candidate.interviewEnabled ?? false)
</script>

<template>
  <TabView
    :active-index="activeTab"
    scrollable
    @update:active-index="emit('update:activeTab', $event)"
  >
    <TabPanel value="0" :header="t('candidates.overview')">
      <div class="py-3">
        <GlassCard>
          <CandidateOverview
            :candidate="candidate"
            :loading="loading"
            :prescanning-score="prescanningScore"
            :interview-score="interviewScore"
            :ai-summary="aiSummary"
            :ai-summary-translations="aiSummaryTranslations"
            :ai-summary-interview-id="aiSummaryInterviewId ?? undefined"
            @update:ai-summary-translations="emit('update:aiSummaryTranslations', $event)"
          />
        </GlassCard>
      </div>
    </TabPanel>
    <TabPanel value="1" :header="t('candidates.cv')">
      <div class="py-3">
        <GlassCard>
          <CvDataView
            :data="candidate.cvParsedData as unknown as Record<string, unknown>"
            :cv-file="candidate.cvFile"
            :cv-filename="candidate.cvOriginalFilename"
            :match-score="candidate.matchScore"
            :match-details="candidate.matchDetails"
            :match-notes-translations="candidate.matchNotesTranslations"
            :cv-summary-translations="candidate.cvSummaryTranslations"
            :application-id="candidate.id"
            @download-cv="emit('downloadCv')"
          />
        </GlassCard>
      </div>
    </TabPanel>
    <TabPanel value="2" :header="t('candidates.prescanning')">
      <div class="py-3">
        <GlassCard>
          <InterviewReviewPanel :candidate-id="candidate.id" session-type="prescanning" />
        </GlassCard>
      </div>
    </TabPanel>
    <TabPanel v-if="hasInterview" value="3" :header="t('candidates.interview')">
      <div class="py-3">
        <GlassCard>
          <InterviewReviewPanel :candidate-id="candidate.id" session-type="interview" />
        </GlassCard>
      </div>
    </TabPanel>
    <TabPanel :value="String(hasInterview ? 4 : 3)" :header="t('candidates.analysis')">
      <div class="py-3">
        <GlassCard>
          <MatchScoreView
            :cv-match-score="candidate.matchScore"
            :match-details="candidate.matchDetails"
            :match-notes-translations="candidate.matchNotesTranslations"
            :application-id="candidate.id"
            :prescanning-score="prescanningScore"
            :interview-score="interviewScore"
          />
        </GlassCard>
      </div>
    </TabPanel>
    <TabPanel :value="String(hasInterview ? 5 : 4)" :header="t('candidates.notes')">
      <div class="py-3">
        <GlassCard>
          <HRNotesPanel
            :notes="candidate.hrNotes"
            :loading="loading"
            @save="emit('saveNotes', $event)"
          />
        </GlassCard>
      </div>
    </TabPanel>
  </TabView>
</template>
