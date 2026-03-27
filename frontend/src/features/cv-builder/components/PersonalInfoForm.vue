<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Editor from 'primevue/editor'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'

const { t } = useI18n()
const store = useCvBuilderStore()

const headline = ref('')
const summary = ref('')
const location = ref('')
const dateOfBirth = ref<Date | null>(null)
const linkedinUrl = ref('')
const githubUrl = ref('')
const websiteUrl = ref('')
const desiredSalaryMin = ref<number | null>(null)
const desiredSalaryMax = ref<number | null>(null)
const desiredSalaryCurrency = ref('')
const desiredSalaryNegotiable = ref(false)
const desiredEmploymentType = ref('')
const isOpenToWork = ref(false)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<FieldErrors>({})
const improvingSection = ref(false)

const currencyOptions = [
  { label: 'USD', value: 'USD' },
  { label: 'EUR', value: 'EUR' },
  { label: 'GBP', value: 'GBP' },
  { label: 'RUB', value: 'RUB' },
]

const employmentTypeOptions = [
  { label: t('cvBuilder.employmentTypes.fullTime'), value: 'full_time' },
  { label: t('cvBuilder.employmentTypes.partTime'), value: 'part_time' },
  { label: t('cvBuilder.employmentTypes.contract'), value: 'contract' },
  { label: t('cvBuilder.employmentTypes.internship'), value: 'internship' },
]

function hasError(field: string): boolean {
  return field in fieldErrors.value
}

function fieldError(field: string): string {
  return fieldErrors.value[field] ?? ''
}

function populateForm(): void {
  const p = store.profile
  if (!p) return
  headline.value = p.headline ?? ''
  summary.value = p.summary ?? ''
  location.value = p.location ?? ''
  dateOfBirth.value = p.dateOfBirth ? new Date(p.dateOfBirth) : null
  linkedinUrl.value = p.linkedinUrl ?? ''
  githubUrl.value = p.githubUrl ?? ''
  websiteUrl.value = p.websiteUrl ?? ''
  desiredSalaryMin.value = p.desiredSalaryMin
  desiredSalaryMax.value = p.desiredSalaryMax
  desiredSalaryCurrency.value = p.desiredSalaryCurrency ?? ''
  desiredSalaryNegotiable.value = p.desiredSalaryNegotiable ?? false
  desiredEmploymentType.value = p.desiredEmploymentType ?? ''
  isOpenToWork.value = p.isOpenToWork ?? false
}

onMounted(() => {
  populateForm()
})

function formatDate(date: Date | null): string | null {
  if (!date) return null
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

async function handleImproveSummary(): Promise<void> {
  if (!summary.value.trim()) return
  improvingSection.value = true
  try {
    const improved = await store.improveCvSection('summary', summary.value)
    summary.value = improved
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    improvingSection.value = false
  }
}

async function scrollToFirstError(): Promise<void> {
  await nextTick()
  const firstInvalid = document.querySelector('.p-invalid, [data-field-error="true"]')
  if (firstInvalid) {
    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

async function handleSave(): Promise<void> {
  successMessage.value = null
  errorMessage.value = null
  fieldErrors.value = {}

  try {
    await store.updateProfile({
      headline: headline.value,
      summary: summary.value,
      location: location.value,
      dateOfBirth: formatDate(dateOfBirth.value),
      linkedinUrl: linkedinUrl.value,
      githubUrl: githubUrl.value,
      websiteUrl: websiteUrl.value,
      desiredSalaryMin: desiredSalaryMin.value,
      desiredSalaryMax: desiredSalaryMax.value,
      desiredSalaryCurrency: desiredSalaryCurrency.value || undefined,
      desiredSalaryNegotiable: desiredSalaryNegotiable.value,
      desiredEmploymentType: desiredEmploymentType.value || undefined,
      isOpenToWork: isOpenToWork.value,
    })
    successMessage.value = t('cvBuilder.personal.saveSuccess')
  } catch (err: unknown) {
    if (err instanceof ApiValidationError) {
      fieldErrors.value = err.fieldErrors
      errorMessage.value = err.message
    } else {
      errorMessage.value = err instanceof Error ? err.message : t('common.error')
    }
    scrollToFirstError()
  }
}

defineExpose({ save: handleSave })
</script>

<template>
  <div>
    <Message v-if="successMessage" severity="success" class="mb-4">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <form
      class="flex flex-col gap-5"
      @submit.prevent="handleSave"
    >
      <div class="flex flex-col gap-1">
        <label for="headline" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.headline') }}
        </label>
        <InputText
          id="headline"
          v-model="headline"
          :placeholder="t('cvBuilder.personal.headlinePlaceholder')"
          class="w-full"
          :invalid="hasError('headline')"
        />
        <small v-if="hasError('headline')" class="text-red-500">{{ fieldError('headline') }}</small>
      </div>

      <div class="flex flex-col gap-1">
        <div class="flex items-center justify-between">
          <label for="summary" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.summary') }}
          </label>
          <Button
            :label="t('cvBuilder.improveWithAi')"
            icon="pi pi-sparkles"
            severity="secondary"
            text
            size="small"
            :loading="improvingSection"
            :disabled="!summary.trim()"
            @click="handleImproveSummary"
          />
        </div>
        <Editor
          v-model="summary"
          :data-field-error="hasError('summary') || undefined"
          editorStyle="height: 150px"
          :class="{ 'border border-red-500 rounded-md': hasError('summary') }"
        />
        <small v-if="hasError('summary')" class="text-red-500">{{ fieldError('summary') }}</small>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="location" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.location') }}
          </label>
          <InputText
            id="location"
            v-model="location"
            :placeholder="t('cvBuilder.personal.locationPlaceholder')"
            class="w-full"
            :invalid="hasError('location')"
          />
          <small v-if="hasError('location')" class="text-red-500">{{ fieldError('location') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="dateOfBirth" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.dateOfBirth') }}
          </label>
          <DatePicker
            id="dateOfBirth"
            v-model="dateOfBirth"
            dateFormat="yy-mm-dd"
            :placeholder="t('cvBuilder.personal.dateOfBirthPlaceholder')"
            showIcon
            class="w-full"
            :invalid="hasError('dateOfBirth')"
          />
          <small v-if="hasError('dateOfBirth')" class="text-red-500">{{ fieldError('dateOfBirth') }}</small>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div class="flex flex-col gap-1">
          <label for="linkedinUrl" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.linkedinUrl') }}
          </label>
          <InputText
            id="linkedinUrl"
            v-model="linkedinUrl"
            placeholder="https://linkedin.com/in/..."
            class="w-full"
            :invalid="hasError('linkedinUrl')"
          />
          <small v-if="hasError('linkedinUrl')" class="text-red-500">{{ fieldError('linkedinUrl') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="githubUrl" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.githubUrl') }}
          </label>
          <InputText
            id="githubUrl"
            v-model="githubUrl"
            placeholder="https://github.com/..."
            class="w-full"
            :invalid="hasError('githubUrl')"
          />
          <small v-if="hasError('githubUrl')" class="text-red-500">{{ fieldError('githubUrl') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="websiteUrl" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.websiteUrl') }}
          </label>
          <InputText
            id="websiteUrl"
            v-model="websiteUrl"
            placeholder="https://..."
            class="w-full"
            :invalid="hasError('websiteUrl')"
          />
          <small v-if="hasError('websiteUrl')" class="text-red-500">{{ fieldError('websiteUrl') }}</small>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <ToggleSwitch v-model="desiredSalaryNegotiable" />
        <label class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.salaryNegotiable') }}
        </label>
      </div>

      <div v-if="!desiredSalaryNegotiable" class="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div class="flex flex-col gap-1">
          <label for="salaryMin" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.salaryMin') }}
          </label>
          <InputNumber
            id="salaryMin"
            v-model="desiredSalaryMin"
            :placeholder="t('cvBuilder.personal.salaryMinPlaceholder')"
            class="w-full"
            :invalid="hasError('desiredSalaryMin')"
          />
          <small v-if="hasError('desiredSalaryMin')" class="text-red-500">{{ fieldError('desiredSalaryMin') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="salaryMax" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.salaryMax') }}
          </label>
          <InputNumber
            id="salaryMax"
            v-model="desiredSalaryMax"
            :placeholder="t('cvBuilder.personal.salaryMaxPlaceholder')"
            class="w-full"
            :invalid="hasError('desiredSalaryMax')"
          />
          <small v-if="hasError('desiredSalaryMax')" class="text-red-500">{{ fieldError('desiredSalaryMax') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="currency" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.currency') }}
          </label>
          <Select
            id="currency"
            v-model="desiredSalaryCurrency"
            :options="currencyOptions"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('cvBuilder.personal.currencyPlaceholder')"
            class="w-full"
            :invalid="hasError('desiredSalaryCurrency')"
          />
          <small v-if="hasError('desiredSalaryCurrency')" class="text-red-500">{{ fieldError('desiredSalaryCurrency') }}</small>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="employmentType" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.employmentType') }}
          </label>
          <Select
            id="employmentType"
            v-model="desiredEmploymentType"
            :options="employmentTypeOptions"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('cvBuilder.personal.employmentTypePlaceholder')"
            class="w-full"
            :invalid="hasError('desiredEmploymentType')"
          />
          <small v-if="hasError('desiredEmploymentType')" class="text-red-500">{{ fieldError('desiredEmploymentType') }}</small>
        </div>

        <div class="flex items-center gap-3 pt-6">
          <ToggleSwitch v-model="isOpenToWork" />
          <label class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.personal.openToWork') }}
          </label>
        </div>
      </div>

    </form>
  </div>
</template>
