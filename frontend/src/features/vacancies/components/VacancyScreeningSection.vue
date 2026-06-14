<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import QuestionList from './QuestionList.vue'
import CriteriaList from './CriteriaList.vue'
import AiInstructionsPanel from './AiInstructionsPanel.vue'
import type { InterviewQuestion, VacancyCriteria, VacancyDetail } from '../types/vacancy.types'

defineProps<{
  vacancy: VacancyDetail
  step: 'prescanning' | 'interview'
  questions: InterviewQuestion[]
  criteria: VacancyCriteria[]
  loading: boolean
}>()

const emit = defineEmits<{
  addQuestion: [data: { text: string; category?: string; step?: string }]
  updateQuestion: [questionId: string, data: Partial<InterviewQuestion>]
  deleteQuestion: [questionId: string]
  generateQuestions: []
  addCriteria: [data: { name: string; description?: string; weight?: number; step?: string }]
  updateCriteria: [criteriaId: string, data: Partial<VacancyCriteria>]
  deleteCriteria: [criteriaId: string]
  translateQuestions: []
  translateCriteria: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="space-y-6">
    <AiInstructionsPanel :vacancy="vacancy" :step="step" />

    <details
      class="rounded-xl border border-gray-100 bg-white p-5 dark:border-gray-800 dark:bg-gray-800"
    >
      <summary class="cursor-pointer text-sm font-semibold text-gray-900">
        {{ t('vacancies.instructions.advancedQuestions') }}
      </summary>
      <p class="mt-2 text-xs text-gray-500">
        {{ t('vacancies.instructions.advancedQuestionsHint') }}
      </p>
      <div class="mt-4">
        <QuestionList
          :questions="questions"
          :loading="loading"
          @add="(d) => emit('addQuestion', { ...d, step })"
          @update="(qId, d) => emit('updateQuestion', qId, d)"
          @delete="(qId) => emit('deleteQuestion', qId)"
          @generate="() => emit('generateQuestions')"
          @translate-all="() => emit('translateQuestions')"
        />
      </div>
    </details>

    <!-- Block 3: Criteria -->
    <section
      class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5"
    >
      <CriteriaList
        :criteria="criteria"
        :loading="loading"
        @add="(d) => emit('addCriteria', { ...d, step })"
        @update="(cId, d) => emit('updateCriteria', cId, d)"
        @delete="(cId) => emit('deleteCriteria', cId)"
        @translate-all="() => emit('translateCriteria')"
      />
    </section>
  </div>
</template>
