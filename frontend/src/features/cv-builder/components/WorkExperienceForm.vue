<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import type { WorkExperience, WorkExperiencePayload } from '../types/cv-builder.types'
import { validateForm } from '@/shared/utils/form-validation'
import { createWorkExperienceSchema } from '../validation/work-experience.schema'
import WorkExperienceItem from './WorkExperienceItem.vue'
import WorkExperienceEditForm from './WorkExperienceEditForm.vue'

const { t } = useI18n()
const store = useCvBuilderStore()

const showForm = ref(false)
const editingExp = ref<WorkExperience | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<FieldErrors>({})
const improvingDescription = ref(false)
const formRef = ref<InstanceType<typeof WorkExperienceEditForm> | null>(null)

const experiences = computed(() => store.profile?.workExperiences ?? [])

function openAddForm(): void {
  editingExp.value = null
  fieldErrors.value = {}
  showForm.value = true
}

function openEditForm(exp: WorkExperience): void {
  editingExp.value = exp
  fieldErrors.value = {}
  showForm.value = true
}

function cancelForm(): void {
  showForm.value = false
  editingExp.value = null
}

async function scrollToFirstError(): Promise<void> {
  await nextTick()
  const el = document.querySelector('.p-invalid, [data-field-error="true"]')
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function handleImproveDescription(text: string): Promise<void> {
  if (!text.trim()) return
  improvingDescription.value = true
  try {
    const improved = await store.improveCvSection('experience_description', text)
    formRef.value?.setDescription(improved)
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    improvingDescription.value = false
  }
}

async function handleSave(payload: WorkExperiencePayload, editingId: string | null): Promise<void> {
  successMessage.value = null
  errorMessage.value = null
  fieldErrors.value = {}

  const schema = createWorkExperienceSchema(t)
  const errors = await validateForm(schema, payload as unknown as Record<string, unknown>)
  if (errors) { fieldErrors.value = errors; scrollToFirstError(); return }

  try {
    if (editingId) {
      await store.updateWorkExperience(editingId, payload)
      successMessage.value = t('cvBuilder.experience.updateSuccess')
    } else {
      await store.createWorkExperience(payload)
      successMessage.value = t('cvBuilder.experience.addSuccess')
    }
    showForm.value = false
    editingExp.value = null
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
    <Message v-if="successMessage" severity="success" class="mb-4">{{ successMessage }}</Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <div v-if="experiences.length && !showForm" class="flex flex-col gap-4">
      <WorkExperienceItem
        v-for="exp in experiences" :key="exp.id"
        :experience="exp"
        @edit="openEditForm"
        @delete="handleDelete"
      />
    </div>

    <div v-if="!experiences.length && !showForm" class="py-8 text-center text-gray-500">
      {{ t('cvBuilder.experience.empty') }}
    </div>

    <div v-if="!showForm" class="mt-4">
      <Button :label="t('cvBuilder.experience.add')" icon="pi pi-plus" severity="secondary" outlined @click="openAddForm" />
    </div>

    <WorkExperienceEditForm
      v-if="showForm"
      ref="formRef"
      :editing-exp="editingExp"
      :saving="store.saving"
      :improving-description="improvingDescription"
      :field-errors="fieldErrors"
      @save="handleSave"
      @cancel="cancelForm"
      @improve-description="handleImproveDescription"
    />
  </div>
</template>
