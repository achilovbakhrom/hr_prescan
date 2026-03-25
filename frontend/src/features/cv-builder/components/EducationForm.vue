<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Message from 'primevue/message'
import EducationLevelSelect from '@/shared/components/EducationLevelSelect.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import type { Education, EducationPayload } from '../types/cv-builder.types'

const { t } = useI18n()
const store = useCvBuilderStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

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

function resetForm(): void {
  institution.value = ''
  degree.value = ''
  educationLevel.value = ''
  fieldOfStudy.value = ''
  startDate.value = null
  endDate.value = null
  description.value = ''
  editingId.value = null
}

function openAddForm(): void {
  resetForm()
  showForm.value = true
}

function openEditForm(edu: Education): void {
  institution.value = edu.institution
  degree.value = edu.degree
  educationLevel.value = edu.educationLevel?.slug ?? ''
  fieldOfStudy.value = edu.fieldOfStudy
  startDate.value = edu.startDate ? new Date(edu.startDate) : null
  endDate.value = edu.endDate ? new Date(edu.endDate) : null
  description.value = edu.description
  editingId.value = edu.id
  showForm.value = true
}

function cancelForm(): void {
  showForm.value = false
  resetForm()
}

function buildPayload(): EducationPayload {
  return {
    institution: institution.value,
    degree: degree.value,
    educationLevel: educationLevel.value,
    fieldOfStudy: fieldOfStudy.value,
    startDate: formatDate(startDate.value),
    endDate: formatDate(endDate.value) || null,
    description: description.value,
  }
}

async function handleSave(): Promise<void> {
  successMessage.value = null
  errorMessage.value = null

  try {
    if (editingId.value) {
      await store.updateEducation(editingId.value, buildPayload())
      successMessage.value = t('cvBuilder.education.updateSuccess')
    } else {
      await store.createEducation(buildPayload())
      successMessage.value = t('cvBuilder.education.addSuccess')
    }
    showForm.value = false
    resetForm()
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  }
}

async function handleDelete(id: string): Promise<void> {
  successMessage.value = null
  errorMessage.value = null

  try {
    await store.deleteEducation(id)
    successMessage.value = t('cvBuilder.education.deleteSuccess')
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

    <!-- Education list -->
    <div v-if="educations.length && !showForm" class="flex flex-col gap-4">
      <div
        v-for="edu in educations"
        :key="edu.id"
        class="rounded-lg border border-gray-200 p-4"
      >
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-gray-900">{{ edu.degree }}</h3>
            <p class="text-sm text-gray-600">{{ edu.institution }}</p>
            <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
              <span v-if="edu.educationLevel">{{ edu.educationLevel.name }}</span>
              <span v-if="edu.fieldOfStudy">{{ edu.fieldOfStudy }}</span>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              {{ formatDisplayDate(edu.startDate) }}
              <template v-if="edu.endDate">
                &mdash; {{ formatDisplayDate(edu.endDate) }}
              </template>
            </p>
            <p v-if="edu.description" class="mt-2 text-sm text-gray-600">{{ edu.description }}</p>
          </div>
          <div class="ml-3 flex shrink-0 gap-1">
            <Button
              icon="pi pi-pencil"
              severity="secondary"
              text
              rounded
              size="small"
              @click="openEditForm(edu)"
              :aria-label="t('common.edit')"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="handleDelete(edu.id)"
              :aria-label="t('common.delete')"
            />
          </div>
        </div>
      </div>
    </div>

    <div v-if="!educations.length && !showForm" class="py-8 text-center text-gray-500">
      {{ t('cvBuilder.education.empty') }}
    </div>

    <!-- Add button -->
    <div v-if="!showForm" class="mt-4">
      <Button
        :label="t('cvBuilder.education.add')"
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
        {{ editingId ? t('cvBuilder.education.editTitle') : t('cvBuilder.education.addTitle') }}
      </h3>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="eduInstitution" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.education.institution') }}
          </label>
          <InputText id="eduInstitution" v-model="institution" class="w-full" />
        </div>

        <div class="flex flex-col gap-1">
          <label for="eduDegree" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.education.degree') }}
          </label>
          <InputText id="eduDegree" v-model="degree" class="w-full" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.education.educationLevel') }}
          </label>
          <EducationLevelSelect v-model="educationLevel" />
        </div>

        <div class="flex flex-col gap-1">
          <label for="eduFieldOfStudy" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.education.fieldOfStudy') }}
          </label>
          <InputText id="eduFieldOfStudy" v-model="fieldOfStudy" class="w-full" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="eduStartDate" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.education.startDate') }}
          </label>
          <DatePicker
            id="eduStartDate"
            v-model="startDate"
            dateFormat="yy-mm-dd"
            showIcon
            class="w-full"
          />
        </div>

        <div class="flex flex-col gap-1">
          <label for="eduEndDate" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.education.endDate') }}
          </label>
          <DatePicker
            id="eduEndDate"
            v-model="endDate"
            dateFormat="yy-mm-dd"
            showIcon
            class="w-full"
          />
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label for="eduDescription" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.education.description') }}
        </label>
        <Textarea id="eduDescription" v-model="description" rows="3" class="w-full" />
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
