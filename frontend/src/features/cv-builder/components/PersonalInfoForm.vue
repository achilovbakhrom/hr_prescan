<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import PersonalInfoBasics from './PersonalInfoBasics.vue'
import PersonalInfoLinks from './PersonalInfoLinks.vue'
import PersonalInfoLocation from './PersonalInfoLocation.vue'
import PersonalInfoPhoto from './PersonalInfoPhoto.vue'
import PersonalInfoSalary from './PersonalInfoSalary.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import { validateForm } from '@/shared/utils/form-validation'
import { createPersonalInfoSchema } from '../validation/personal-info.schema'

const { t } = useI18n()
const toast = useToast()
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
const fieldErrors = ref<FieldErrors>({})

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

// Keep the in-memory profile in sync with edits so the live preview updates
// as the user types (no API call until Save).
watch(
  [headline, summary, location, isOpenToWork],
  () => {
    store.patchProfileLocal({
      headline: headline.value,
      summary: summary.value,
      location: location.value,
      isOpenToWork: isOpenToWork.value,
    })
  },
  { flush: 'post' },
)

function formatDate(date: Date | null): string | null {
  if (!date) return null
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function scrollToFirstError(): void {
  document
    .querySelector('.p-invalid, [data-field-error="true"]')
    ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function handleSave(): Promise<void> {
  fieldErrors.value = {}

  const schema = createPersonalInfoSchema(t)
  const errors = await validateForm(schema, {
    headline: headline.value,
    summary: summary.value,
    location: location.value,
    dateOfBirth: formatDate(dateOfBirth.value),
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
    toast.add({
      severity: 'warn',
      summary: t('cvBuilder.personal.fixErrors'),
      life: 4000,
    })
    await nextTick()
    scrollToFirstError()
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
    toast.add({
      severity: 'success',
      summary: t('cvBuilder.personal.saveSuccess'),
      life: 2500,
    })
  } catch (err: unknown) {
    let message: string
    if (err instanceof ApiValidationError) {
      fieldErrors.value = err.fieldErrors
      message = err.message
    } else {
      message = err instanceof Error ? err.message : t('common.error')
    }
    toast.add({ severity: 'error', summary: message, life: 4000 })
    await nextTick()
    scrollToFirstError()
  }
}

function onPhotoSuccess(message: string): void {
  toast.add({ severity: 'success', summary: message, life: 2500 })
}

function onPhotoError(message: string): void {
  toast.add({ severity: 'error', summary: message, life: 4000 })
}

defineExpose({ save: handleSave })
</script>

<template>
  <div>
    <form class="flex flex-col gap-5" @submit.prevent="handleSave">
      <PersonalInfoPhoto @success="onPhotoSuccess" @error="onPhotoError" />

      <PersonalInfoBasics
        v-model:headline="headline"
        v-model:summary="summary"
        :field-errors="fieldErrors"
        @error="onPhotoError"
      />

      <PersonalInfoLocation
        v-model:location="location"
        v-model:date-of-birth="dateOfBirth"
        :field-errors="fieldErrors"
      />

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
