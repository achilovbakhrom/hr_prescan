<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Message from 'primevue/message'
import VacancyBasicInfoTab from './VacancyBasicInfoTab.vue'
import VacancyCompanyTab from './VacancyCompanyTab.vue'
import CreateCompanyDialog from './CreateCompanyDialog.vue'
import { useVacancyForm } from '../composables/useVacancyForm'
import { useVacancyStore } from '../stores/vacancy.store'
import type { CreateVacancyRequest, VacancyDetail } from '../types/vacancy.types'
import type { Company } from '@/features/companies/types/company.types'

const props = defineProps<{
  vacancy: VacancyDetail
}>()

const { t } = useI18n()
const toast = useToast()
const vacancyStore = useVacancyStore()

const initialData = (): Partial<CreateVacancyRequest> => ({
  title: props.vacancy.title,
  description: props.vacancy.description,
  requirements: props.vacancy.requirements,
  responsibilities: props.vacancy.responsibilities,
  skills: props.vacancy.skills,
  salaryMin: props.vacancy.salaryMin,
  salaryMax: props.vacancy.salaryMax,
  salaryCurrency: props.vacancy.salaryCurrency,
  location: props.vacancy.location,
  isRemote: props.vacancy.isRemote,
  employmentType: props.vacancy.employmentType,
  experienceLevel: props.vacancy.experienceLevel,
  deadline: props.vacancy.deadline,
  companyId: props.vacancy.company?.id ?? undefined,
})

const form = useVacancyForm(initialData, () => vacancyStore.fieldErrors)

watch(
  () => props.vacancy,
  () => {
    form.syncFromInitialData(initialData())
  },
  { deep: true },
)

const showCreateDialog = ref(false)
const saving = ref(false)

function handleCompanyCreated(company: Company): void {
  form.companiesList.value = [
    ...form.companiesList.value,
    { ...company, isDefault: form.companiesList.value.length === 0, role: 'admin' },
  ]
  form.companyId.value = company.id
}

async function handleSave(): Promise<void> {
  saving.value = true
  try {
    const payload = form.buildPayload()
    await vacancyStore.updateVacancy(props.vacancy.id, {
      title: payload.title,
      description: payload.description,
      requirements: payload.requirements,
      responsibilities: payload.responsibilities,
      skills: payload.skills,
      salaryMin: payload.salaryMin,
      salaryMax: payload.salaryMax,
      salaryCurrency: payload.salaryCurrency,
      location: payload.location,
      isRemote: payload.isRemote,
      employmentType: payload.employmentType,
      experienceLevel: payload.experienceLevel,
      deadline: payload.deadline,
    })
    toast.add({ severity: 'success', summary: t('common.saved'), life: 2500 })
  } catch {
    toast.add({ severity: 'error', summary: t('common.error'), life: 4000 })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <form class="space-y-6" @submit.prevent="handleSave">
    <Message
      v-if="vacancyStore.error && Object.keys(vacancyStore.fieldErrors).length === 0"
      severity="error"
    >
      {{ vacancyStore.error }}
    </Message>

    <section class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <h3 class="mb-4 text-sm font-semibold text-gray-900">{{ t('vacancies.details.jobInfo') }}</h3>
      <VacancyBasicInfoTab
        v-model:title="form.title.value"
        v-model:description="form.description.value"
        v-model:requirements="form.requirements.value"
        v-model:responsibilities="form.responsibilities.value"
        v-model:skills="form.skills.value"
        v-model:salary-min="form.salaryMin.value"
        v-model:salary-max="form.salaryMax.value"
        v-model:salary-currency="form.salaryCurrency.value"
        v-model:location="form.location.value"
        v-model:is-remote="form.isRemote.value"
        v-model:employment-type="form.employmentType.value"
        v-model:experience-level="form.experienceLevel.value"
        v-model:deadline="form.deadline.value"
        :has-error="form.hasError"
        :field-error="form.fieldError"
      />
    </section>

    <section class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <h3 class="mb-4 text-sm font-semibold text-gray-900">{{ t('vacancies.details.company') }}</h3>
      <VacancyCompanyTab
        v-model:company-id="form.companyId.value"
        :companies-list="form.companiesList.value"
        :loading-companies="form.loadingCompanies.value"
        :selected-company="form.selectedCompany.value"
        @open-create-dialog="showCreateDialog = true"
      />
    </section>

    <div
      class="sticky bottom-0 -mx-3 flex justify-end border-t border-gray-100 dark:border-gray-800 bg-white/95 dark:bg-gray-900/95 px-3 py-3 backdrop-blur sm:-mx-5 sm:px-5"
    >
      <Button
        type="submit"
        :label="t('common.save')"
        icon="pi pi-check"
        :loading="saving"
        :disabled="!form.canSave.value"
      />
    </div>

    <CreateCompanyDialog v-model:visible="showCreateDialog" @created="handleCompanyCreated" />
  </form>
</template>
