<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import CertificationItem from './CertificationItem.vue'
import CertificationFormFields from './CertificationFormFields.vue'
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

const certName = ref('')
const issuingOrganization = ref('')
const issueDate = ref<Date | null>(null)
const expiryDate = ref<Date | null>(null)
const credentialUrl = ref('')

const certifications = computed(() => store.profile?.certifications ?? [])

function formatDate(date: Date | null): string | null {
  if (!date) return null
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function resetForm(): void {
  certName.value = ''; issuingOrganization.value = ''; issueDate.value = null
  expiryDate.value = null; credentialUrl.value = ''; editingId.value = null; fieldErrors.value = {}
}

function openAddForm(): void { resetForm(); showForm.value = true }

function openEditForm(cert: Certification): void {
  certName.value = cert.name; issuingOrganization.value = cert.issuingOrganization
  issueDate.value = cert.issueDate ? new Date(cert.issueDate) : null
  expiryDate.value = cert.expiryDate ? new Date(cert.expiryDate) : null
  credentialUrl.value = cert.credentialUrl; editingId.value = cert.id; fieldErrors.value = {}
  showForm.value = true
}

function cancelForm(): void { showForm.value = false; resetForm() }

function buildPayload(): CertificationPayload {
  return { name: certName.value, issuingOrganization: issuingOrganization.value, issueDate: formatDate(issueDate.value), expiryDate: formatDate(expiryDate.value), credentialUrl: credentialUrl.value }
}

async function handleSave(): Promise<void> {
  successMessage.value = null; errorMessage.value = null; fieldErrors.value = {}
  try {
    if (editingId.value) {
      await store.updateCertification(editingId.value, buildPayload())
      successMessage.value = t('cvBuilder.certifications.updateSuccess')
    } else {
      await store.createCertification(buildPayload())
      successMessage.value = t('cvBuilder.certifications.addSuccess')
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
  try { await store.deleteCertification(id); successMessage.value = t('cvBuilder.certifications.deleteSuccess') }
  catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : t('common.error') }
}
</script>

<template>
  <div>
    <Message v-if="successMessage" severity="success" class="mb-4">{{ successMessage }}</Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <div v-if="certifications.length && !showForm" class="flex flex-col gap-4">
      <CertificationItem v-for="cert in certifications" :key="cert.id" :certification="cert" @edit="openEditForm" @delete="handleDelete" />
    </div>

    <div v-if="!certifications.length && !showForm" class="py-8 text-center text-gray-500">{{ t('cvBuilder.certifications.empty') }}</div>

    <div v-if="!showForm" class="mt-4">
      <Button :label="t('cvBuilder.certifications.add')" icon="pi pi-plus" severity="secondary" outlined @click="openAddForm" />
    </div>

    <CertificationFormFields
      v-if="showForm"
      v-model:name="certName" v-model:issuing-organization="issuingOrganization"
      v-model:issue-date="issueDate" v-model:expiry-date="expiryDate"
      v-model:credential-url="credentialUrl" :editing-id="editingId" :saving="store.saving" :field-errors="fieldErrors"
      @save="handleSave" @cancel="cancelForm"
    />
  </div>
</template>
