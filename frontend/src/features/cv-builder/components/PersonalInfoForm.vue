<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Editor from 'primevue/editor'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Message from 'primevue/message'
import PersonalInfoLinks from './PersonalInfoLinks.vue'
import PersonalInfoSalary from './PersonalInfoSalary.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import { validateForm } from '@/shared/utils/form-validation'
import { createPersonalInfoSchema } from '../validation/personal-info.schema'

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
const improvingHeadline = ref(false)
const improvingSection = ref(false)

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

async function handleImproveHeadline(): Promise<void> {
  if (!headline.value.trim()) return
  improvingHeadline.value = true
  try {
    headline.value = await store.improveCvSection('headline', headline.value)
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    improvingHeadline.value = false
  }
}

async function handleImproveSummary(): Promise<void> {
  if (!summary.value.trim()) return
  improvingSection.value = true
  try {
    summary.value = await store.improveCvSection('summary', summary.value)
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    improvingSection.value = false
  }
}

async function handleSave(): Promise<void> {
  successMessage.value = null
  errorMessage.value = null
  fieldErrors.value = {}

  const schema = createPersonalInfoSchema(t)
  const errors = await validateForm(schema, {
    headline: headline.value,
    summary: summary.value,
    location: location.value,
    linkedinUrl: linkedinUrl.value || undefined,
    githubUrl: githubUrl.value || undefined,
    websiteUrl: websiteUrl.value || undefined,
    desiredSalaryNegotiable: desiredSalaryNegotiable.value,
    desiredSalaryMin: desiredSalaryMin.value,
    desiredSalaryMax: desiredSalaryMax.value,
    desiredEmploymentType: desiredEmploymentType.value,
  })
  if (errors) {
    fieldErrors.value = errors
    await nextTick()
    document
      .querySelector('.p-invalid, [data-field-error="true"]')
      ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

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
    await nextTick()
    document
      .querySelector('.p-invalid, [data-field-error="true"]')
      ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

defineExpose({ save: handleSave })
</script>

<template>
  <div>
    <Message v-if="successMessage" severity="success" class="mb-4">{{ successMessage }}</Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <form class="flex flex-col gap-5" @submit.prevent="handleSave">
      <div class="flex flex-col gap-1">
        <div class="flex items-center justify-between">
          <label for="headline" class="text-sm font-medium text-gray-700"
            >{{ t('cvBuilder.personal.headline') }} <span class="text-red-500">*</span></label
          >
          <Button
            :label="t('cvBuilder.improveWithAi')"
            icon="pi pi-sparkles"
            severity="secondary"
            text
            size="small"
            :loading="improvingHeadline"
            :disabled="!headline.trim()"
            @click="handleImproveHeadline"
          />
        </div>
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
          <label for="summary" class="text-sm font-medium text-gray-700"
            >{{ t('cvBuilder.personal.summary') }} <span class="text-red-500">*</span></label
          >
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
          <label for="location" class="text-sm font-medium text-gray-700">{{
            t('cvBuilder.personal.location')
          }}</label>
          <InputText
            id="location"
            v-model="location"
            :placeholder="t('cvBuilder.personal.locationPlaceholder')"
            class="w-full"
            :invalid="hasError('location')"
          />
          <small v-if="hasError('location')" class="text-red-500">{{
            fieldError('location')
          }}</small>
        </div>
        <div class="flex flex-col gap-1">
          <label for="dateOfBirth" class="text-sm font-medium text-gray-700">{{
            t('cvBuilder.personal.dateOfBirth')
          }}</label>
          <DatePicker
            id="dateOfBirth"
            v-model="dateOfBirth"
            dateFormat="yy-mm-dd"
            :placeholder="t('cvBuilder.personal.dateOfBirthPlaceholder')"
            showIcon
            class="w-full"
            :invalid="hasError('dateOfBirth')"
          />
          <small v-if="hasError('dateOfBirth')" class="text-red-500">{{
            fieldError('dateOfBirth')
          }}</small>
        </div>
      </div>

      <PersonalInfoLinks
        v-model:linkedin-url="linkedinUrl"
        v-model:github-url="githubUrl"
        v-model:website-url="websiteUrl"
        :field-errors="fieldErrors"
      />

      <PersonalInfoSalary
        v-model:salary-min="desiredSalaryMin"
        v-model:salary-max="desiredSalaryMax"
        v-model:currency="desiredSalaryCurrency"
        v-model:negotiable="desiredSalaryNegotiable"
        v-model:employment-type="desiredEmploymentType"
        v-model:is-open-to-work="isOpenToWork"
        :field-errors="fieldErrors"
      />
    </form>
  </div>
</template>
