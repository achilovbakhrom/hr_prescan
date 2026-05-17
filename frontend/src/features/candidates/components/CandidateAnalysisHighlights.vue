<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CandidateAnalysisSession } from '../composables/useInterviewData'
import type { DecisionSupport } from '@/shared/types/interview.types'

const props = defineProps<{
  sessions: CandidateAnalysisSession[]
}>()

const { t } = useI18n()

const cards = computed(() =>
  props.sessions
    .map((session) => {
      const support: DecisionSupport = session.decisionSupport || {}
      const positives =
        support.positiveMoments || support.positive_moments || support.strengths || []
      const negatives = support.negativeMoments || support.negative_moments || support.risks || []
      const conclusion =
        support.conclusion || support.nextStep || support.next_step || support.recommendation || ''
      return { ...session, positives, negatives, conclusion }
    })
    .filter(
      (session) =>
        session.aiSummary ||
        session.positives.length ||
        session.negatives.length ||
        session.conclusion,
    ),
)
</script>

<template>
  <div v-if="cards.length" class="space-y-3">
    <div class="flex items-center justify-between gap-3">
      <h3 class="text-sm font-semibold text-[color:var(--color-text-primary)]">
        {{ t('candidates.analysisDetails.title', 'Detailed AI analysis') }}
      </h3>
    </div>
    <div class="grid gap-3 lg:grid-cols-2">
      <section
        v-for="session in cards"
        :key="session.id || session.sessionType"
        class="rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-3"
      >
        <div class="mb-3 flex items-center justify-between gap-2">
          <p class="text-sm font-semibold text-[color:var(--color-text-primary)]">
            {{
              session.sessionType === 'prescanning'
                ? t('candidates.prescanning')
                : t('candidates.interview')
            }}
          </p>
          <span
            v-if="session.overallScore !== null"
            class="rounded-md bg-[color:var(--color-surface-sunken)] px-2 py-1 font-mono text-xs"
          >
            {{ session.overallScore }}/10
          </span>
        </div>
        <p v-if="session.aiSummary" class="mb-3 text-sm text-[color:var(--color-text-secondary)]">
          {{ session.aiSummary }}
        </p>
        <div class="grid gap-3 sm:grid-cols-2">
          <div>
            <p class="mb-1 text-xs font-semibold uppercase text-green-700">
              {{ t('candidates.analysisDetails.positive', 'Positive moments') }}
            </p>
            <ul v-if="session.positives.length" class="space-y-1 text-sm">
              <li
                v-for="item in session.positives"
                :key="item"
                class="text-[color:var(--color-text-secondary)]"
              >
                {{ item }}
              </li>
            </ul>
            <p v-else class="text-sm text-[color:var(--color-text-muted)]">
              {{ t('candidates.analysisDetails.nonePositive', 'No clear positives listed yet.') }}
            </p>
          </div>
          <div>
            <p class="mb-1 text-xs font-semibold uppercase text-amber-700">
              {{ t('candidates.analysisDetails.negative', 'Negative moments') }}
            </p>
            <ul v-if="session.negatives.length" class="space-y-1 text-sm">
              <li
                v-for="item in session.negatives"
                :key="item"
                class="text-[color:var(--color-text-secondary)]"
              >
                {{ item }}
              </li>
            </ul>
            <p v-else class="text-sm text-[color:var(--color-text-muted)]">
              {{ t('candidates.analysisDetails.noneNegative', 'No major concerns listed yet.') }}
            </p>
          </div>
        </div>
        <div
          v-if="session.conclusion"
          class="mt-3 border-t border-[color:var(--color-border-soft)] pt-3"
        >
          <p class="mb-1 text-xs font-semibold uppercase text-[color:var(--color-text-muted)]">
            {{ t('candidates.analysisDetails.conclusion', 'Conclusion') }}
          </p>
          <p class="text-sm text-[color:var(--color-text-secondary)]">{{ session.conclusion }}</p>
        </div>
      </section>
    </div>
  </div>
</template>
