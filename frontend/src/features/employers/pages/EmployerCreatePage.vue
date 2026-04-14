<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import SelectButton from 'primevue/selectbutton'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useEmployerStore } from '../stores/employer.store'

const { t } = useI18n()
const router = useRouter()
const employerStore = useEmployerStore()

type SourceMode = 'manual' | 'file' | 'website'

const sourceMode = ref<SourceMode>('manual')
const sourceModeOptions = [
  { label: t('employers.manual'), value: 'manual' },
  { label: t('employers.file'), value: 'file' },
  { label: t('employers.fromWebsite'), value: 'website' },
]

const name = ref('')
const industry = ref('')
const website = ref('')
const description = ref('')
const fileUrl = ref('')
const saving = ref(false)

async function handleFileUpload(event: { files: File | File[] }): Promise<void> {
  const files = Array.isArray(event.files) ? event.files : [event.files]
  const file = files[0]
  if (!file || !name.value) return

  saving.value = true
  try {
    const employer = await employerStore.createEmployerFromFile(name.value, file)
    router.push({ name: ROUTE_NAMES.EMPLOYER_DETAIL, params: { id: employer.id } })
  } catch {
    // error is displayed via store
  } finally {
    saving.value = false
  }
}

async function handleFetchFromUrl(): Promise<void> {
  if (!name.value || !fileUrl.value) return

  saving.value = true
  try {
    const employer = await employerStore.createEmployerFromUrl(name.value, fileUrl.value)
    router.push({ name: ROUTE_NAMES.EMPLOYER_DETAIL, params: { id: employer.id } })
  } catch {
    // error is displayed via store
  } finally {
    saving.value = false
  }
}

async function handleSave(): Promise<void> {
  if (!name.value) return

  saving.value = true
  try {
    const employer = await employerStore.createEmployer({
      name: name.value,
      industry: industry.value || undefined,
      website: website.value || undefined,
      description: description.value || undefined,
      source: 'manual',
    })
    router.push({ name: ROUTE_NAMES.EMPLOYER_DETAIL, params: { id: employer.id } })
  } catch {
    // error is displayed via store
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <!-- Back -->
    <button
      class="mb-4 flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-900"
      @click="router.push({ name: ROUTE_NAMES.EMPLOYER_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <h1 class="mb-6 text-2xl font-bold text-gray-900">{{ t('employers.create') }}</h1>

    <!-- Error -->
    <div
      v-if="employerStore.error"
      class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600"
    >
      {{ employerStore.error }}
    </div>

    <!-- Source toggle -->
    <div class="mb-6">
      <label class="mb-2 block text-sm font-medium">{{ t('employers.source') }}</label>
      <SelectButton
        v-model="sourceMode"
        :options="sourceModeOptions"
        option-label="label"
        option-value="value"
      />
    </div>

    <!-- Company name (always required) -->
    <div class="mb-4">
      <label class="mb-1 block text-sm font-medium"
        >{{ t('employers.name') }} <span class="text-red-500">*</span></label
      >
      <InputText v-model="name" class="w-full" :placeholder="t('employers.namePlaceholder')" />
    </div>

    <!-- Manual mode -->
    <template v-if="sourceMode === 'manual'">
      <div class="mb-4">
        <label class="mb-1 block text-sm font-medium">{{ t('employers.industry') }}</label>
        <InputText v-model="industry" class="w-full" />
      </div>
      <div class="mb-4">
        <label class="mb-1 block text-sm font-medium">{{ t('employers.website') }}</label>
        <InputText v-model="website" class="w-full" placeholder="https://..." />
      </div>
      <div class="mb-6">
        <label class="mb-1 block text-sm font-medium">{{ t('employers.description') }}</label>
        <Textarea v-model="description" class="w-full" rows="6" />
      </div>
      <div class="flex justify-end">
        <Button
          :label="t('common.save')"
          icon="pi pi-check"
          :loading="saving"
          :disabled="!name"
          @click="handleSave"
        />
      </div>
    </template>

    <!-- File upload mode -->
    <template v-if="sourceMode === 'file'">
      <div class="mb-6">
        <label class="mb-2 block text-sm font-medium">{{ t('employers.uploadFile') }}</label>
        <p class="mb-2 text-xs text-gray-400">PDF, DOCX, TXT. Max 10MB.</p>
        <FileUpload
          mode="basic"
          accept=".pdf,.docx,.doc,.txt"
          :max-file-size="10000000"
          :choose-label="t('employers.uploadFile')"
          :auto="true"
          :custom-upload="true"
          :disabled="!name || saving"
          @uploader="handleFileUpload"
          class="text-sm"
        />
        <span v-if="saving" class="mt-2 flex items-center gap-2 text-sm text-gray-500">
          <i class="pi pi-spinner pi-spin"></i> {{ t('common.loading') }}
        </span>
      </div>
    </template>

    <!-- Website URL mode -->
    <template v-if="sourceMode === 'website'">
      <div class="mb-6">
        <label class="mb-1 block text-sm font-medium">{{ t('employers.website') }}</label>
        <div class="flex gap-2">
          <InputText
            v-model="fileUrl"
            class="flex-1"
            :placeholder="t('employers.urlPlaceholder')"
            :disabled="saving"
          />
          <Button
            type="button"
            :label="t('employers.fetchFromUrl')"
            icon="pi pi-globe"
            :loading="saving"
            :disabled="!name || !fileUrl"
            @click="handleFetchFromUrl"
          />
        </div>
      </div>
    </template>
  </div>
</template>
