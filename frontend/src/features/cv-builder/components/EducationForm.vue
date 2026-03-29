<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import EducationItem from './EducationItem.vue'
import EducationFormFields from './EducationFormFields.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import type { Education, EducationPayload } from '../types/cv-builder.types'

const { t } = useI18n()
const store = useCvBuilderStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<FieldErrors>({})

const institution = ref('')
const degree = ref('')
const educationLevel = ref('')
const fieldOfStudy = ref('')
const startDate = ref<Date | null>(null)
const endDate = ref<Date | null>(null)
const description = ref('')

const educations = computed(() => store.profile?.educations ?? [])

function formatDate(date: Date | null): string {
  if (!date) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function resetForm(): void {
  institution.value = ''; degree.value = ''; educationLevel.value = ''
  fieldOfStudy.value = ''; startDate.value = null; endDate.value = null
  description.value = ''; editingId.value = null; fieldErrors.value = {}
}

function openAddForm(): void { resetForm(); showForm.value = true }

function openEditForm(edu: Education): void {
  institution.value = edu.institution; degree.value = edu.degree
  educationLevel.value = edu.educationLevel?.slug ?? ''; fieldOfStudy.value = edu.fieldOfStudy
  startDate.value = edu.startDate ? new Date(edu.startDate) : null
  endDate.value = edu.endDate ? new Date(edu.endDate) : null
  description.value = edu.description; editingId.value = edu.id; fieldErrors.value = {}
  showForm.value = true
}

function cancelForm(): void { showForm.value = false; resetForm() }

function buildPayload(): EducationPayload {
  return {
    institution: institution.value, degree: degree.value, educationLevel: educationLevel.value,
    fieldOfStudy: fieldOfStudy.value, startDate: formatDate(startDate.value),
    endDate: formatDate(endDate.value) || null, description: description.value,
  }
}

async function handleSave(): Promise<void> {
  successMessage.value = null; errorMessage.value = null; fieldErrors.value = {}
  try {
    if (editingId.value) {
      await store.updateEducation(editingId.value, buildPayload())
      successMessage.value = t('cvBuilder.education.updateSuccess')
    } else {
      await store.createEducation(buildPayload())
      successMessage.value = t('cvBuilder.education.addSuccess')
    }
    showForm.value = false; resetForm()
  } catch (err: unknown) {
    if (err instanceof ApiValidationError) { fieldErrors.value = err.fieldErrors; errorMessage.value = err.message }
    else { errorMessage.value = err instanceof Error ? err.message : t('common.error') }
    await nextTick()
    document.querySelector('.p-invalid, [data-field-error="true"]')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

async function handleDelete(id: string): Promise<void> {
  successMessage.value = null; errorMessage.value = null
  try { await store.deleteEducation(id); successMessage.value = t('cvBuilder.education.deleteSuccess') }
  catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : t('common.error') }
}
</script>

<template>
  <div>
    <Message v-if="successMessage" severity="success" class="mb-4">{{ successMessage }}</Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <div v-if="educations.length && !showForm" class="flex flex-col gap-4">
      <EducationItem v-for="edu in educations" :key="edu.id" :education="edu" @edit="openEditForm" @delete="handleDelete" />
    </div>

    <div v-if="!educations.length && !showForm" class="py-8 text-center text-gray-500">{{ t('cvBuilder.education.empty') }}</div>

    <div v-if="!showForm" class="mt-4">
      <Button :label="t('cvBuilder.education.add')" icon="pi pi-plus" severity="secondary" outlined @click="openAddForm" />
    </div>

    <EducationFormFields
      v-if="showForm"
      v-model:institution="institution" v-model:degree="degree" v-model:education-level="educationLevel"
      v-model:field-of-study="fieldOfStudy" v-model:start-date="startDate" v-model:end-date="endDate"
      v-model:description="description" :editing-id="editingId" :saving="store.saving" :field-errors="fieldErrors"
      @save="handleSave" @cancel="cancelForm"
    />
  </div>
</template>
