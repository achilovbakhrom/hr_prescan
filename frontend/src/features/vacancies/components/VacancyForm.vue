<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Message from 'primevue/message'
import type { FieldErrors } from '@/shared/api/errors'
import type { Company } from '@/features/companies/types/company.types'
import type { CreateVacancyRequest } from '../types/vacancy.types'
import { useVacancyForm } from '../composables/useVacancyForm'
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
          v-model:deadline="form.deadline.value"
          :has-error="form.hasError"
          :field-error="form.fieldError"
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
