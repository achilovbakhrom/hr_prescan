<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import type { VacancyDetail } from '../types/vacancy.types'
import { formatMoney } from '../composables/useVacancyLabels'
import { useEmploymentLabels, useExperienceLabels } from '../composables/useVacancyLabels'
import { vacancyService } from '../services/vacancy.service'

const props = defineProps<{
  vacancy: VacancyDetail
}>()

const emit = defineEmits<{
  (e: 'keywords-updated', keywords: string[]): void
}>()

const { t } = useI18n()

const employmentLabel = useEmploymentLabels()
const experienceLabel = useExperienceLabels()

const regeneratingKeywords = ref(false)

async function regenerateKeywords(): Promise<void> {
  regeneratingKeywords.value = true
  try {
    const result = await vacancyService.regenerateKeywords(props.vacancy.id)
    emit('keywords-updated', result.keywords)
  } catch {
    /* silent */
  } finally {
    regeneratingKeywords.value = false
  }
}

function formatSalary(): string {
  const { salaryMin, salaryMax, salaryCurrency } = props.vacancy
  if (!salaryMin && !salaryMax) return t('vacancies.overview.salaryNotSpecified')
  if (salaryMin && salaryMax) {
    return t('vacancies.overview.salaryRange', {
      min: formatMoney(salaryMin),
      max: formatMoney(salaryMax),
      currency: salaryCurrency,
    })
  }
  if (salaryMin)
    return t('vacancies.overview.salaryFrom', {
      amount: formatMoney(salaryMin),
      currency: salaryCurrency,
    })
  return t('vacancies.overview.salaryUpTo', {
    amount: formatMoney(salaryMax!),
    currency: salaryCurrency,
  })
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
          <Tag
            v-if="vacancy.isRemote"
            :value="t('vacancies.overview.remote')"
            severity="info"
            class="ml-1"
          />
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
          {{
            vacancy.interviewMode === 'meet'
              ? t('vacancies.interviewMode.meet')
              : t('vacancies.interviewMode.chat')
          }}
        </p>
      </div>
      <div v-if="vacancy.interviewEnabled && vacancy.interviewMode === 'meet'">
        <p class="text-sm text-gray-500">{{ t('vacancies.form.interviewDuration') }}</p>
        <p class="font-medium">{{ vacancy.interviewDuration }} min</p>
      </div>
    </div>

    <!-- Employer card -->
    <div v-if="vacancy.employer" class="rounded-lg border border-gray-200 bg-gray-50 p-4">
      <p class="mb-2 text-sm text-gray-500">{{ t('vacancies.form.companyInfo') }}</p>
      <div class="flex items-center gap-3">
        <div
          v-if="vacancy.employer.logo"
          class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white"
        >
          <img
            :src="vacancy.employer.logo"
            :alt="vacancy.employer.name"
            class="h-full w-full object-contain"
          />
        </div>
        <div
          v-else
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600"
        >
          <i class="pi pi-building text-lg"></i>
        </div>
        <div class="min-w-0">
          <p class="font-semibold text-gray-900">{{ vacancy.employer.name }}</p>
          <p v-if="vacancy.employer.industry" class="text-sm text-gray-500">
            {{ vacancy.employer.industry }}
          </p>
          <a
            v-if="vacancy.employer.website"
            :href="vacancy.employer.website"
            target="_blank"
            rel="noopener noreferrer"
            class="text-sm text-blue-600 hover:underline"
          >
            {{ vacancy.employer.website }}
          </a>
        </div>
      </div>
    </div>

    <div v-if="vacancy.skills.length > 0">
      <p class="mb-1 text-sm text-gray-500">{{ t('vacancies.overview.skills') }}</p>
      <div class="flex flex-wrap gap-1">
        <Tag v-for="skill in vacancy.skills" :key="skill" :value="skill" severity="secondary" />
      </div>
    </div>

    <!-- Keywords -->
    <div>
      <div class="mb-1 flex items-center gap-2">
        <p class="text-sm text-gray-500">{{ t('vacancies.keywords') }}</p>
        <Button
          :label="t('vacancies.regenerateKeywords')"
          icon="pi pi-refresh"
          size="small"
          severity="secondary"
          text
          :loading="regeneratingKeywords"
          @click="regenerateKeywords"
        />
      </div>
      <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.keywordsHint') }}</p>
      <div v-if="vacancy.keywords?.length" class="flex flex-wrap gap-1">
        <Tag v-for="keyword in vacancy.keywords" :key="keyword" :value="keyword" severity="info" />
      </div>
      <p v-else class="text-sm text-gray-400">{{ t('vacancies.overview.notSpecified') }}</p>
    </div>
  </div>
</template>
