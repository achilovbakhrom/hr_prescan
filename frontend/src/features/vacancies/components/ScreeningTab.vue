<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import QuestionList from './QuestionList.vue'
import CriteriaList from './CriteriaList.vue'
import type { InterviewQuestion, VacancyCriteria } from '../types/vacancy.types'

defineProps<{
  vacancyId: string
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
}>()

const { t } = useI18n()
</script>

<template>
  <div class="py-3 sm:py-4">
    <TabView>
      <TabPanel value="0">
        <template #header>
          <span class="text-xs sm:text-sm"
            ><i class="pi pi-list mr-1"></i>{{ t('vacancies.questions') }}</span
          >
        </template>
        <div class="py-3">
          <QuestionList
            :questions="questions"
            :loading="loading"
            @add="(d) => emit('addQuestion', { ...d, step })"
            @update="(qId, d) => emit('updateQuestion', qId, d)"
            @delete="(qId) => emit('deleteQuestion', qId)"
            @generate="() => emit('generateQuestions')"
          />
        </div>
      </TabPanel>
      <TabPanel value="1">
        <template #header>
          <span class="text-xs sm:text-sm"
            ><i class="pi pi-chart-bar mr-1"></i>{{ t('vacancies.criteria') }}</span
          >
        </template>
        <div class="py-3">
          <CriteriaList
            :criteria="criteria"
            :loading="loading"
            @add="(d) => emit('addCriteria', { ...d, step })"
            @update="(cId, d) => emit('updateCriteria', cId, d)"
            @delete="(cId) => emit('deleteCriteria', cId)"
          />
        </div>
      </TabPanel>
    </TabView>
  </div>
</template>
