<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Message from 'primevue/message'
import VacancyBasicInfoTab from './VacancyBasicInfoTab.vue'
import VacancyCompanyTab from './VacancyCompanyTab.vue'
import CreateEmployerDialog from './CreateEmployerDialog.vue'
import { useVacancyForm } from '../composables/useVacancyForm'
import { useVacancyStore } from '../stores/vacancy.store'
import type { CreateVacancyRequest, VacancyDetail } from '../types/vacancy.types'
import type { EmployerCompany } from '@/features/employers/types/employer.types'

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
  employerId: props.vacancy.employer?.id ?? undefined,
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

function handleEmployerCreated(employer: EmployerCompany): void {
  form.employersList.value.push(employer)
  form.employerId.value = employer.id
}

async function handleSave(): Promise<void> {
  saving.value = true
  try {
    const payload = form.buildPayload()
    // Only send the fields this section owns
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
      employerId: payload.employerId,
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

    <!-- Job info -->
    <section class="rounded-xl border border-gray-100 bg-white p-5">
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

    <!-- Company / Employer -->
    <section class="rounded-xl border border-gray-100 bg-white p-5">
      <h3 class="mb-4 text-sm font-semibold text-gray-900">{{ t('vacancies.details.company') }}</h3>
      <VacancyCompanyTab
        v-model:employer-id="form.employerId.value"
        :employers-list="form.employersList.value"
        :loading-employers="form.loadingEmployers.value"
        :selected-employer="form.selectedEmployer.value"
        @open-create-dialog="showCreateDialog = true"
      />
    </section>

    <div
      class="sticky bottom-0 -mx-3 flex justify-end border-t border-gray-100 bg-white/95 px-3 py-3 backdrop-blur sm:-mx-5 sm:px-5"
    >
      <Button
        type="submit"
        :label="t('common.save')"
        icon="pi pi-check"
        :loading="saving"
        :disabled="!form.canSave.value"
      />
    </div>

    <CreateEmployerDialog v-model:visible="showCreateDialog" @created="handleEmployerCreated" />
  </form>
</template>
