<script setup lang="ts">
import { isAxiosError } from 'axios'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Message from 'primevue/message'
import type { FieldErrors } from '@/shared/api/errors'
import type { Company } from '@/features/companies/types/company.types'
import type { CreateVacancyRequest } from '../types/vacancy.types'
import { useVacancyForm } from '../composables/useVacancyForm'
import { vacancyService } from '../services/vacancy.service'
import VacancyBasicInfoTab from './VacancyBasicInfoTab.vue'
import VacancyCompanyTab from './VacancyCompanyTab.vue'
import VacancyPrescanningTab from './VacancyPrescanningTab.vue'
import VacancyInterviewTab from './VacancyInterviewTab.vue'
import VacancySettingsTab from './VacancySettingsTab.vue'
import CreateCompanyDialog from './CreateCompanyDialog.vue'

const props = defineProps<{
  initialData?: Partial<CreateVacancyRequest>
  loading?: boolean
  fieldErrors?: FieldErrors
  errorMessage?: string | null
}>()

const emit = defineEmits<{ save: [data: CreateVacancyRequest] }>()

const { t } = useI18n()
const toast = useToast()

const form = useVacancyForm(
  () => props.initialData,
  () => props.fieldErrors,
)

watch(
  () => props.initialData,
  (d) => {
    if (d) form.syncFromInitialData(d)
  },
)

const showCreateDialog = ref(false)
const generatingBasicInfo = ref(false)
const canGenerateBasicInfo = computed(() => form.title.value.trim().length >= 5)

function generationErrorMessage(error: unknown): string {
  if (isAxiosError<{ detail?: string }>(error)) {
    return error.response?.data?.detail || t('vacancies.form.generateWithAIError')
  }
  return t('vacancies.form.generateWithAIError')
}

async function handleCompanyCreated(company: Company): Promise<void> {
  // Re-fetch memberships so the new company is in the dropdown with correct is_default state.
  form.companiesList.value = [
    ...form.companiesList.value,
    { ...company, isDefault: form.companiesList.value.length === 0, role: 'admin' },
  ]
  form.companyId.value = company.id
}

function handleSave(): void {
  emit('save', form.buildPayload())
}

async function handleGenerateBasicInfo(): Promise<void> {
  if (!canGenerateBasicInfo.value || generatingBasicInfo.value) return
  generatingBasicInfo.value = true
  try {
    const content = await vacancyService.generateContent({
      title: form.title.value.trim(),
      skills: form.skills.value,
      salaryMin: form.salaryMin.value,
      salaryMax: form.salaryMax.value,
      salaryCurrency: form.salaryCurrency.value,
      location: form.location.value || undefined,
      isRemote: form.isRemote.value,
      employmentType: form.employmentType.value,
      experienceLevel: form.experienceLevel.value,
    })
    if (content.description) form.description.value = content.description
    if (content.requirements) form.requirements.value = content.requirements
    if (content.responsibilities) form.responsibilities.value = content.responsibilities
    if (!content.description && !content.requirements && !content.responsibilities) {
      throw new Error(t('vacancies.form.generateWithAIError'))
    }
    toast.add({
      severity: 'success',
      summary: t('vacancies.form.generateWithAISuccess'),
      life: 2500,
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: t('vacancies.form.generateWithAIError'),
      detail: generationErrorMessage(error),
      life: 4000,
    })
  } finally {
    generatingBasicInfo.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSave">
    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <TabView v-model:activeIndex="form.activeTab.value">
      <TabPanel value="0" :header="t('vacancies.form.basicInfo')">
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
          :show-generate-ai="true"
          :can-generate-ai="canGenerateBasicInfo"
          :generating-ai="generatingBasicInfo"
          :has-error="form.hasError"
          :field-error="form.fieldError"
          @generate-ai="handleGenerateBasicInfo"
        />
      </TabPanel>

      <TabPanel value="1" :header="t('vacancies.form.companyInfo')">
        <VacancyCompanyTab
          v-model:company-id="form.companyId.value"
          :companies-list="form.companiesList.value"
          :loading-companies="form.loadingCompanies.value"
          :selected-company="form.selectedCompany.value"
          @open-create-dialog="showCreateDialog = true"
        />
      </TabPanel>

      <TabPanel value="2" :header="t('vacancies.form.prescanning')">
        <VacancyPrescanningTab
          v-model:prescanning-prompt="form.prescanningPrompt.value"
          v-model:prescanning-language="form.prescanningLanguage.value"
          :has-error="form.hasError"
          :field-error="form.fieldError"
        />
      </TabPanel>

      <TabPanel value="3" :header="t('vacancies.form.interview')">
        <VacancyInterviewTab
          v-model:interview-enabled="form.interviewEnabled.value"
          v-model:interview-mode="form.interviewMode.value"
          v-model:interview-duration="form.interviewDuration.value"
          v-model:interview-prompt="form.interviewPrompt.value"
          :has-error="form.hasError"
          :field-error="form.fieldError"
        />
      </TabPanel>

      <TabPanel value="4" :header="t('vacancies.form.settings')">
        <VacancySettingsTab
          v-model:visibility="form.visibility.value"
          v-model:cv-required="form.cvRequired.value"
          :has-error="form.hasError"
          :field-error="form.fieldError"
        />
      </TabPanel>
    </TabView>

    <div class="mt-4 flex justify-end border-t border-gray-100 dark:border-gray-800 pt-4">
      <Button
        type="submit"
        :label="t('common.save')"
        icon="pi pi-check"
        :loading="loading"
        :disabled="!form.canSave.value"
      />
    </div>
  </form>

  <CreateCompanyDialog v-model:visible="showCreateDialog" @created="handleCompanyCreated" />
</template>
