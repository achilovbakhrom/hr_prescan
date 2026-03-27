<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { ApiValidationError } from '@/shared/api/errors'
import type { FieldErrors } from '@/shared/api/errors'
import type { Certification, CertificationPayload } from '../types/cv-builder.types'

const { t } = useI18n()
const store = useCvBuilderStore()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const fieldErrors = ref<FieldErrors>({})

const name = ref('')
const issuingOrganization = ref('')
const issueDate = ref<Date | null>(null)
const expiryDate = ref<Date | null>(null)
const credentialUrl = ref('')

const certifications = computed(() => store.profile?.certifications ?? [])

function hasError(field: string): boolean {
  return field in fieldErrors.value
}

function fieldError(field: string): string {
  return fieldErrors.value[field] ?? ''
}

function formatDate(date: Date | null): string | null {
  if (!date) return null
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
  name.value = ''
  issuingOrganization.value = ''
  issueDate.value = null
  expiryDate.value = null
  credentialUrl.value = ''
  editingId.value = null
  fieldErrors.value = {}
}

function openAddForm(): void {
  resetForm()
  showForm.value = true
}

function openEditForm(cert: Certification): void {
  name.value = cert.name
  issuingOrganization.value = cert.issuingOrganization
  issueDate.value = cert.issueDate ? new Date(cert.issueDate) : null
  expiryDate.value = cert.expiryDate ? new Date(cert.expiryDate) : null
  credentialUrl.value = cert.credentialUrl
  editingId.value = cert.id
  fieldErrors.value = {}
  showForm.value = true
}

function cancelForm(): void {
  showForm.value = false
  resetForm()
}

function buildPayload(): CertificationPayload {
  return {
    name: name.value,
    issuingOrganization: issuingOrganization.value,
    issueDate: formatDate(issueDate.value),
    expiryDate: formatDate(expiryDate.value),
    credentialUrl: credentialUrl.value,
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
      await store.updateCertification(editingId.value, buildPayload())
      successMessage.value = t('cvBuilder.certifications.updateSuccess')
    } else {
      await store.createCertification(buildPayload())
      successMessage.value = t('cvBuilder.certifications.addSuccess')
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
    await store.deleteCertification(id)
    successMessage.value = t('cvBuilder.certifications.deleteSuccess')
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

    <!-- Certifications list -->
    <div v-if="certifications.length && !showForm" class="flex flex-col gap-4">
      <div
        v-for="cert in certifications"
        :key="cert.id"
        class="rounded-lg border border-gray-200 p-4"
      >
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-gray-900">{{ cert.name }}</h3>
            <p class="text-sm text-gray-600">{{ cert.issuingOrganization }}</p>
            <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
              <span v-if="cert.issueDate">
                {{ t('cvBuilder.certifications.issued') }}: {{ formatDisplayDate(cert.issueDate) }}
              </span>
              <span v-if="cert.expiryDate">
                {{ t('cvBuilder.certifications.expires') }}: {{ formatDisplayDate(cert.expiryDate) }}
              </span>
            </div>
            <a
              v-if="cert.credentialUrl"
              :href="cert.credentialUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-1 inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              <i class="pi pi-external-link text-xs"></i>
              {{ t('cvBuilder.certifications.viewCredential') }}
            </a>
          </div>
          <div class="ml-3 flex shrink-0 gap-1">
            <Button
              icon="pi pi-pencil"
              severity="secondary"
              text
              rounded
              size="small"
              @click="openEditForm(cert)"
              :aria-label="t('common.edit')"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="handleDelete(cert.id)"
              :aria-label="t('common.delete')"
            />
          </div>
        </div>
      </div>
    </div>

    <div v-if="!certifications.length && !showForm" class="py-8 text-center text-gray-500">
      {{ t('cvBuilder.certifications.empty') }}
    </div>

    <!-- Add button -->
    <div v-if="!showForm" class="mt-4">
      <Button
        :label="t('cvBuilder.certifications.add')"
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
        {{ editingId ? t('cvBuilder.certifications.editTitle') : t('cvBuilder.certifications.addTitle') }}
      </h3>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="certName" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.certifications.name') }} <span class="text-red-500">*</span>
          </label>
          <InputText id="certName" v-model="name" class="w-full" :invalid="hasError('name')" />
          <small v-if="hasError('name')" class="text-red-500">{{ fieldError('name') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="certOrg" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.certifications.issuingOrganization') }}
          </label>
          <InputText id="certOrg" v-model="issuingOrganization" class="w-full" :invalid="hasError('issuingOrganization')" />
          <small v-if="hasError('issuingOrganization')" class="text-red-500">{{ fieldError('issuingOrganization') }}</small>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="flex flex-col gap-1">
          <label for="certIssueDate" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.certifications.issueDate') }}
          </label>
          <DatePicker
            id="certIssueDate"
            v-model="issueDate"
            dateFormat="yy-mm-dd"
            showIcon
            class="w-full"
            :invalid="hasError('issueDate')"
          />
          <small v-if="hasError('issueDate')" class="text-red-500">{{ fieldError('issueDate') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="certExpiryDate" class="text-sm font-medium text-gray-700">
            {{ t('cvBuilder.certifications.expiryDate') }}
          </label>
          <DatePicker
            id="certExpiryDate"
            v-model="expiryDate"
            dateFormat="yy-mm-dd"
            showIcon
            class="w-full"
            :invalid="hasError('expiryDate')"
          />
          <small v-if="hasError('expiryDate')" class="text-red-500">{{ fieldError('expiryDate') }}</small>
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label for="certUrl" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.certifications.credentialUrl') }}
        </label>
        <InputText
          id="certUrl"
          v-model="credentialUrl"
          placeholder="https://..."
          class="w-full"
          :invalid="hasError('credentialUrl')"
        />
        <small v-if="hasError('credentialUrl')" class="text-red-500">{{ fieldError('credentialUrl') }}</small>
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
