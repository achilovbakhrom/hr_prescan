<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import { useCvBuilderStore } from '../stores/cv-builder.store'

interface FileUploadSelectEvent {
  files: File[]
}

const { t } = useI18n()
const store = useCvBuilderStore()

const selectedFile = ref<File | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

function onFileSelect(event: FileUploadSelectEvent): void {
  if (event.files && event.files.length > 0) {
    selectedFile.value = event.files[0]
  }
}

function onFileClear(): void {
  selectedFile.value = null
}

async function handleParse(): Promise<void> {
  if (!selectedFile.value) return

  successMessage.value = null
  errorMessage.value = null

  try {
    await store.parseCv(selectedFile.value)
    successMessage.value = t('cvBuilder.cvParse.success')
    selectedFile.value = null
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  }
}
</script>

<template>
  <div class="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-4 sm:p-6">
    <div class="mb-3 flex items-center gap-2">
      <i class="pi pi-upload text-primary text-lg"></i>
      <h3 class="text-base font-semibold text-gray-800">
        {{ t('cvBuilder.cvParse.title') }}
      </h3>
    </div>
    <p class="mb-4 text-sm text-gray-500">
      {{ t('cvBuilder.cvParse.description') }}
    </p>

    <Message v-if="successMessage" severity="success" class="mb-4">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <div v-if="store.parsing" class="flex flex-col items-center gap-3 py-6">
      <ProgressSpinner
        style="width: 40px; height: 40px"
        strokeWidth="4"
      />
      <p class="text-sm text-gray-500">{{ t('cvBuilder.cvParse.parsing') }}</p>
    </div>

    <div v-else>
      <FileUpload
        mode="basic"
        accept=".pdf,.docx"
        :maxFileSize="10000000"
        :chooseLabel="t('cvBuilder.cvParse.chooseFile')"
        :auto="false"
        @select="onFileSelect"
        @clear="onFileClear"
        class="mb-3"
      />

      <Button
        v-if="selectedFile"
        :label="t('cvBuilder.cvParse.parseButton')"
        icon="pi pi-sparkles"
        :loading="store.parsing"
        @click="handleParse"
        class="mt-2"
      />
    </div>
  </div>
</template>
