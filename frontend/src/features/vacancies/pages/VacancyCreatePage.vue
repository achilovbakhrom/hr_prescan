<script setup lang="ts">
/**
 * VacancyCreatePage — multi-step wizard presented inside a GlassCard.
 * The VacancyForm component already uses a 5-tab TabView; we render a
 * glass-chip progress bar above it as a redundant visual breadcrumb. The
 * user can still navigate via the underlying tabs as before — no business-
 * logic change.
 * Spec: docs/design/spec.md §9 Vacancies (wizard).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import GlassCard from '@/shared/components/GlassCard.vue'
import VacancyForm from '../components/VacancyForm.vue'
import VacancyWizardSteps from '../components/VacancyWizardSteps.vue'
import { useVacancyStore } from '../stores/vacancy.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CreateVacancyRequest } from '../types/vacancy.types'

const { t } = useI18n()
const router = useRouter()
const vacancyStore = useVacancyStore()

const steps = computed(() => [
  { key: 'basics', label: t('vacancies.form.basicInfo') },
  { key: 'company', label: t('vacancies.form.companyInfo') },
  { key: 'prescanning', label: t('vacancies.form.prescanning') },
  { key: 'interview', label: t('vacancies.form.interview') },
  { key: 'review', label: t('vacancies.form.settings') },
])

async function handleSave(data: CreateVacancyRequest): Promise<void> {
  try {
    const vacancy = await vacancyStore.createVacancy(data)
    router.push({
      name: ROUTE_NAMES.VACANCY_DETAIL,
      params: { id: vacancy.id },
    })
  } catch {
    /* errors shown via fieldErrors / error passed to VacancyForm */
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-[color:var(--color-text-muted)] transition-colors hover:text-[color:var(--color-text-primary)]"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
        {{ t('vacancies.createTitle') }}
      </h1>
    </div>

    <!-- Progress breadcrumb — purely visual; the TabView below owns focus -->
    <VacancyWizardSteps :steps="steps" :active-index="0" :max-reached="steps.length - 1" />

    <GlassCard>
      <VacancyForm
        :loading="vacancyStore.loading"
        :field-errors="vacancyStore.fieldErrors"
        :error-message="vacancyStore.error"
        @save="handleSave"
      />
    </GlassCard>
  </div>
</template>
