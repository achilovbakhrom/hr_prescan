<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { VacancyDetail } from '../types/vacancy.types'
import { formatMoney } from '../composables/useVacancyLabels'
import { useEmploymentLabels, useExperienceLabels } from '../composables/useVacancyLabels'

const { t } = useI18n()

const props = defineProps<{
  vacancy: VacancyDetail
}>()

const employmentLabel = useEmploymentLabels()
const experienceLabel = useExperienceLabels()

function formatSalary(): string {
  const { salaryMin, salaryMax, salaryCurrency } = props.vacancy
  if (!salaryMin && !salaryMax) return t('vacancies.overview.salaryNotSpecified')
  if (salaryMin && salaryMax) {
    return t('vacancies.overview.salaryRange', { min: formatMoney(salaryMin), max: formatMoney(salaryMax), currency: salaryCurrency })
  }
  if (salaryMin) return t('vacancies.overview.salaryFrom', { amount: formatMoney(salaryMin), currency: salaryCurrency })
  return t('vacancies.overview.salaryUpTo', { amount: formatMoney(salaryMax!), currency: salaryCurrency })
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div>
        <p class="text-sm text-gray-500">{{ t('vacancies.overview.employmentType') }}</p>
        <p class="font-medium">
          {{ employmentLabel[vacancy.employmentType] }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('vacancies.overview.experienceLevel') }}</p>
        <p class="font-medium">
          {{ experienceLabel[vacancy.experienceLevel] }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('vacancies.overview.location') }}</p>
        <p class="font-medium">
          {{ vacancy.location || t('vacancies.overview.notSpecified') }}
          <Tag v-if="vacancy.isRemote" :value="t('vacancies.overview.remote')" severity="info" class="ml-1" />
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('vacancies.overview.salary') }}</p>
        <p class="font-medium">{{ formatSalary() }}</p>
      </div>
    </div>

    <!-- Screening Pipeline -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div>
        <p class="text-sm text-gray-500">{{ t('vacancies.overview.prescanning') }}</p>
        <p class="font-medium">
          <Tag :value="t('vacancies.form.prescanningAlwaysEnabled')" severity="success" />
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">{{ t('vacancies.form.interviewOptional') }}</p>
        <p class="font-medium">
          <Tag
            :value="vacancy.interviewEnabled ? 'Enabled' : 'Disabled'"
            :severity="vacancy.interviewEnabled ? 'success' : 'secondary'"
          />
        </p>
      </div>
      <div v-if="vacancy.interviewEnabled">
        <p class="text-sm text-gray-500">{{ t('vacancies.form.interviewMode') }}</p>
        <p class="font-medium">
          {{ vacancy.interviewMode === 'meet' ? t('vacancies.interviewMode.meet') : t('vacancies.interviewMode.chat') }}
        </p>
      </div>
      <div v-if="vacancy.interviewEnabled && vacancy.interviewMode === 'meet'">
        <p class="text-sm text-gray-500">{{ t('vacancies.form.interviewDuration') }}</p>
        <p class="font-medium">{{ vacancy.interviewDuration }} min</p>
      </div>
    </div>

    <div v-if="vacancy.skills.length > 0">
      <p class="mb-1 text-sm text-gray-500">{{ t('vacancies.overview.skills') }}</p>
      <div class="flex flex-wrap gap-1">
        <Tag
          v-for="skill in vacancy.skills"
          :key="skill"
          :value="skill"
          severity="secondary"
        />
      </div>
    </div>
  </div>
</template>
