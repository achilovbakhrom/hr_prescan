<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import type { WorkExperience, WorkExperiencePayload } from '../types/cv-builder.types'

const { t } = useI18n()
const store = useCvBuilderStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<FieldErrors>({})

const companyName = ref('')
const position = ref('')
const employmentType = ref('')
const location = ref('')
const startDate = ref<Date | null>(null)
const endDate = ref<Date | null>(null)
const isCurrent = ref(false)
const description = ref('')
const improvingDescription = ref(false)

const employmentTypeOptions = [
  { label: t('cvBuilder.employmentTypes.fullTime'), value: 'full_time' },
  { label: t('cvBuilder.employmentTypes.partTime'), value: 'part_time' },
  { label: t('cvBuilder.employmentTypes.contract'), value: 'contract' },
  { label: t('cvBuilder.employmentTypes.internship'), value: 'internship' },
]

const experiences = computed(() => store.profile?.workExperiences ?? [])

function hasError(field: string): boolean {
  return field in fieldErrors.value
}

function fieldError(field: string): string {
  return fieldErrors.value[field] ?? ''
}

function formatDate(date: Date | null): string {
  if (!date) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatDisplayDate(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short' })
}

function getEmploymentLabel(value: string): string {
  const opt = employmentTypeOptions.find((o) => o.value === value)
  return opt?.label ?? value
}

function resetForm(): void {
  companyName.value = ''
  position.value = ''
  employmentType.value = ''
  location.value = ''
  startDate.value = null
  endDate.value = null
  isCurrent.value = false
  description.value = ''
  editingId.value = null
  fieldErrors.value = {}
}

function openAddForm(): void {
  resetForm()
  showForm.value = true
}

function openEditForm(exp: WorkExperience): void {
  companyName.value = exp.companyName
  position.value = exp.position
  employmentType.value = exp.employmentType
  location.value = exp.location
  startDate.value = exp.startDate ? new Date(exp.startDate) : null
  endDate.value = exp.endDate ? new Date(exp.endDate) : null
  isCurrent.value = exp.isCurrent
  description.value = exp.description
  editingId.value = exp.id
  fieldErrors.value = {}
  showForm.value = true
}

function cancelForm(): void {
  showForm.value = false
  resetForm()
}

function buildPayload(): WorkExperiencePayload {
  return {
    companyName: companyName.value,
    position: position.value,
    employmentType: employmentType.value,
    location: location.value,
    startDate: formatDate(startDate.value),
    endDate: isCurrent.value ? null : formatDate(endDate.value) || null,
    isCurrent: isCurrent.value,
    description: description.value,
  }
}

async function handleImproveDescription(): Promise<void> {
  if (!description.value.trim()) return
  improvingDescription.value = true
  try {
    const improved = await store.improveCvSection('experience_description', description.value)
    description.value = improved
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    improvingDescription.value = false
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
    if (editingId.value) {
      await store.updateWorkExperience(editingId.value, buildPayload())
      successMessage.value = t('cvBuilder.experience.updateSuccess')
    } else {
      await store.createWorkExperience(buildPayload())
      successMessage.value = t('cvBuilder.experience.addSuccess')
    }
    showForm.value = false
    resetForm()
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

async function handleDelete(id: string): Promise<void> {
  successMessage.value = null
  errorMessage.value = null

  try {
    await store.deleteWorkExperience(id)
    successMessage.value = t('cvBuilder.experience.deleteSuccess')
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  }
}
</script>

<template>
  <div>
    <Message v-if="successMessage" severity="success" class="mb-4">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <!-- Experience list -->
    <div v-if="experiences.length && !showForm" class="flex flex-col gap-4">
      <div
        v-for="exp in experiences"
        :key="exp.id"
        class="rounded-lg border border-gray-200 p-4"
      >
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-gray-900">{{ exp.position }}</h3>
            <p class="text-sm text-gray-600">{{ exp.companyName }}</p>
            <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
              <span v-if="exp.employmentType">{{ getEmploymentLabel(exp.employmentType) }}</span>
              <span v-if="exp.location">{{ exp.location }}</span>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              {{ formatDisplayDate(exp.startDate) }}
              &mdash;
              {{ exp.isCurrent ? t('cvBuilder.experience.present') : formatDisplayDate(exp.endDate) }}
            </p>
            <p v-if="exp.description" class="mt-2 text-sm text-gray-600">{{ exp.description }}</p>
          </div>
          <div class="ml-3 flex shrink-0 gap-1">
            <Button
              icon="pi pi-pencil"
              severity="secondary"
              text
              rounded
              size="small"
              @click="openEditForm(exp)"
              :aria-label="t('common.edit')"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="handleDelete(exp.id)"
              :aria-label="t('common.delete')"
            />
          </div>
        </div>
      </div>
    </div>

    <div v-if="!experiences.length && !showForm" class="py-8 text-center text-gray-500">
      {{ t('cvBuilder.experience.empty') }}
    </div>

    <!-- Add button -->
    <div v-if="!showForm" class="mt-4">
      <Button
        :label="t('cvBuilder.experience.add')"
        icon="pi pi-plus"
        severity="secondary"
        outlined
        @click="openAddForm"
      />
    </div>

    <!-- Inline form -->
    <form
      v-if="showForm"
      class="mt-4 flex flex-col gap-4 rounded-lg border border-gray-200 p-4"
      @submit.prevent="handleSave"
    >
      <h3 class="font-semibold text-gray-900">
        {{ editingId ? t('cvBuilder.experience.editTitle') : t('cvBuilder.experience.addTitle') }}
      </h3>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="expCompany" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.companyName') }} <span class="text-red-500">*</span>
          </label>
          <InputText id="expCompany" v-model="companyName" class="w-full" :invalid="hasError('companyName')" />
          <small v-if="hasError('companyName')" class="text-red-500">{{ fieldError('companyName') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="expPosition" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.position') }} <span class="text-red-500">*</span>
          </label>
          <InputText id="expPosition" v-model="position" class="w-full" :invalid="hasError('position')" />
          <small v-if="hasError('position')" class="text-red-500">{{ fieldError('position') }}</small>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="expType" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.employmentType') }}
          </label>
          <Select
            id="expType"
            v-model="employmentType"
            :options="employmentTypeOptions"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('cvBuilder.experience.employmentTypePlaceholder')"
            class="w-full"
            :invalid="hasError('employmentType')"
          />
          <small v-if="hasError('employmentType')" class="text-red-500">{{ fieldError('employmentType') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="expLocation" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.location') }}
          </label>
          <InputText id="expLocation" v-model="location" class="w-full" :invalid="hasError('location')" />
          <small v-if="hasError('location')" class="text-red-500">{{ fieldError('location') }}</small>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="expStartDate" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.startDate') }} <span class="text-red-500">*</span>
          </label>
          <DatePicker
            id="expStartDate"
            v-model="startDate"
            dateFormat="yy-mm-dd"
            showIcon
            class="w-full"
            :invalid="hasError('startDate')"
          />
          <small v-if="hasError('startDate')" class="text-red-500">{{ fieldError('startDate') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="expEndDate" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.endDate') }}
          </label>
          <DatePicker
            id="expEndDate"
            v-model="endDate"
            dateFormat="yy-mm-dd"
            showIcon
            :disabled="isCurrent"
            class="w-full"
            :invalid="hasError('endDate')"
          />
          <small v-if="hasError('endDate')" class="text-red-500">{{ fieldError('endDate') }}</small>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <Checkbox id="expIsCurrent" v-model="isCurrent" :binary="true" />
        <label for="expIsCurrent" class="text-sm text-gray-700">
          {{ t('cvBuilder.experience.currentlyWorking') }}
        </label>
      </div>

      <div class="flex flex-col gap-1">
        <div class="flex items-center justify-between">
          <label for="expDescription" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.experience.description') }}
          </label>
          <Button
            :label="t('cvBuilder.improveWithAi')"
            icon="pi pi-sparkles"
            severity="secondary"
            text
            size="small"
            :loading="improvingDescription"
            :disabled="!description.trim()"
            @click="handleImproveDescription"
          />
        </div>
        <Textarea id="expDescription" v-model="description" rows="3" class="w-full" :invalid="hasError('description')" />
        <small v-if="hasError('description')" class="text-red-500">{{ fieldError('description') }}</small>
      </div>

      <div class="flex justify-end gap-2">
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          text
          @click="cancelForm"
        />
        <Button
          type="submit"
          :label="t('common.save')"
          :loading="store.saving"
        />
      </div>
    </form>
  </div>
</template>
