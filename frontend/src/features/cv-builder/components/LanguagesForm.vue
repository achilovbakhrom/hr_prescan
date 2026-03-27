<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Message from 'primevue/message'
import LanguageAutocomplete from '@/shared/components/LanguageAutocomplete.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import type { LanguageEntry, LanguagePayload } from '../types/cv-builder.types'

const { t } = useI18n()
const store = useCvBuilderStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<FieldErrors>({})

const languageCode = ref('')
const proficiency = ref('')

const proficiencyOptions = [
  { label: t('cvBuilder.proficiencies.beginner'), value: 'beginner' },
  { label: t('cvBuilder.proficiencies.elementary'), value: 'elementary' },
  { label: t('cvBuilder.proficiencies.intermediate'), value: 'intermediate' },
  { label: t('cvBuilder.proficiencies.upperIntermediate'), value: 'upper_intermediate' },
  { label: t('cvBuilder.proficiencies.advanced'), value: 'advanced' },
  { label: t('cvBuilder.proficiencies.native'), value: 'native' },
]

const languages = computed(() => store.profile?.languages ?? [])

function hasError(field: string): boolean {
  return field in fieldErrors.value
}

function fieldError(field: string): string {
  return fieldErrors.value[field] ?? ''
}

function getProficiencyLabel(value: string): string {
  const opt = proficiencyOptions.find((o) => o.value === value)
  return opt?.label ?? value
}

function getProficiencySeverity(value: string): "success" | "info" | "warn" | "secondary" {
  if (value === 'native' || value === 'advanced') return 'success'
  if (value === 'upper_intermediate' || value === 'intermediate') return 'info'
  if (value === 'elementary') return 'warn'
  return 'secondary'
}

function resetForm(): void {
  languageCode.value = ''
  proficiency.value = ''
  editingId.value = null
  fieldErrors.value = {}
}

function openAddForm(): void {
  resetForm()
  showForm.value = true
}

function openEditForm(entry: LanguageEntry): void {
  languageCode.value = entry.language.code
  proficiency.value = entry.proficiency
  editingId.value = entry.id
  fieldErrors.value = {}
  showForm.value = true
}

function cancelForm(): void {
  showForm.value = false
  resetForm()
}

function buildPayload(): LanguagePayload {
  return {
    language: languageCode.value,
    proficiency: proficiency.value,
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
      await store.updateLanguage(editingId.value, buildPayload())
      successMessage.value = t('cvBuilder.languages.updateSuccess')
    } else {
      await store.createLanguage(buildPayload())
      successMessage.value = t('cvBuilder.languages.addSuccess')
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
    await store.deleteLanguage(id)
    successMessage.value = t('cvBuilder.languages.deleteSuccess')
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

    <!-- Languages list -->
    <div v-if="languages.length && !showForm" class="flex flex-col gap-3">
      <div
        v-for="entry in languages"
        :key="entry.id"
        class="flex items-center justify-between rounded-lg border border-gray-200 px-4 py-3"
      >
        <div class="flex items-center gap-3">
          <span class="font-medium text-gray-900">{{ entry.language.name }}</span>
          <Tag
            :value="getProficiencyLabel(entry.proficiency)"
            :severity="getProficiencySeverity(entry.proficiency)"
          />
        </div>
        <div class="flex gap-1">
          <Button
            icon="pi pi-pencil"
            severity="secondary"
            text
            rounded
            size="small"
            @click="openEditForm(entry)"
            :aria-label="t('common.edit')"
          />
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            rounded
            size="small"
            @click="handleDelete(entry.id)"
            :aria-label="t('common.delete')"
          />
        </div>
      </div>
    </div>

    <div v-if="!languages.length && !showForm" class="py-8 text-center text-gray-500">
      {{ t('cvBuilder.languages.empty') }}
    </div>

    <!-- Add button -->
    <div v-if="!showForm" class="mt-4">
      <Button
        :label="t('cvBuilder.languages.add')"
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
        {{ editingId ? t('cvBuilder.languages.editTitle') : t('cvBuilder.languages.addTitle') }}
      </h3>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.languages.language') }} <span class="text-red-500">*</span>
          </label>
          <LanguageAutocomplete v-model="languageCode" />
          <small v-if="hasError('language')" class="text-red-500">{{ fieldError('language') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="langProficiency" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.languages.proficiency') }} <span class="text-red-500">*</span>
          </label>
          <Select
            id="langProficiency"
            v-model="proficiency"
            :options="proficiencyOptions"
            optionLabel="label"
            optionValue="value"
            :placeholder="t('cvBuilder.languages.proficiencyPlaceholder')"
            class="w-full"
            :invalid="hasError('proficiency')"
          />
          <small v-if="hasError('proficiency')" class="text-red-500">{{ fieldError('proficiency') }}</small>
        </div>
      </div>

      <!-- Non-field errors (e.g. "This language has already been added") -->
      <small v-if="hasError('nonFieldErrors')" class="text-red-500">{{ fieldError('nonFieldErrors') }}</small>

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
