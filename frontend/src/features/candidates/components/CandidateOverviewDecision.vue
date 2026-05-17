<script setup lang="ts">
import TranslatableText from '@/shared/components/TranslatableText.vue'
import CandidateAnalysisHighlights from './CandidateAnalysisHighlights.vue'
import type { CandidateAnalysisSession } from '../composables/useInterviewData'

interface RecommendationView {
  label: string
  icon: string
  cls: string
}

defineProps<{
  recommendation: RecommendationView | null
  aiSummary?: string | null
  aiSummaryTranslations?: Record<string, string>
  aiSummaryInterviewId?: string
  analysisSessions: CandidateAnalysisSession[]
}>()

const emit = defineEmits<{
  'update:aiSummaryTranslations': [tr: Record<string, string>]
}>()
</script>

<template>
  <div v-if="recommendation || analysisSessions.length" class="space-y-4">
    <div v-if="recommendation" class="rounded-lg border p-4" :class="recommendation.cls">
      <div class="flex items-start gap-3">
        <i class="pi mt-0.5 text-lg" :class="recommendation.icon"></i>
        <div>
          <p class="font-semibold">{{ recommendation.label }}</p>
          <TranslatableText
            v-if="aiSummary && aiSummaryInterviewId"
            :text="aiSummary"
            :translations="aiSummaryTranslations || {}"
            model="interview"
            :object-id="aiSummaryInterviewId"
            field="ai_summary"
            @translated="(tr) => emit('update:aiSummaryTranslations', tr)"
          >
            <template #default="{ text }">
              <p class="mt-1 text-sm opacity-80">{{ text }}</p>
            </template>
          </TranslatableText>
          <p v-else-if="aiSummary" class="mt-1 text-sm opacity-80">{{ aiSummary }}</p>
        </div>
      </div>
    </div>
    <CandidateAnalysisHighlights :sessions="analysisSessions" />
  </div>
</template>
