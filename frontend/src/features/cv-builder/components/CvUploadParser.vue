<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import FileUpload from 'primevue/fileupload'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'

interface FileUploadSelectEvent {
  files: File[]
}

const { t } = useI18n()
const store = useCvBuilderStore()

const visible = ref(false)
const selectedFile = ref<File | null>(null)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

function open(): void {
  selectedFile.value = null
  successMessage.value = null
  errorMessage.value = null
  visible.value = true
}

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
    setTimeout(() => {
      visible.value = false
    }, 1500)
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  }
}

defineExpose({ open })
</script>

<template>
  <Button :label="t('cvBuilder.cvParse.title')" icon="pi pi-upload" size="small" @click="open" />

  <Dialog
    v-model:visible="visible"
    :header="t('cvBuilder.cvParse.title')"
    modal
    :style="{ width: '500px' }"
    :breakpoints="{ '640px': '95vw' }"
    :closable="!store.parsing"
  >
    <div class="space-y-4">
      <p class="text-sm text-gray-500">
        {{ t('cvBuilder.cvParse.description') }}
      </p>

      <Message v-if="successMessage" severity="success">{{ successMessage }}</Message>
      <Message v-if="errorMessage" severity="error">{{ errorMessage }}</Message>

      <div v-if="store.parsing" class="flex flex-col items-center gap-3 py-8">
        <i class="pi pi-spinner pi-spin text-4xl text-blue-500"></i>
        <p class="text-sm font-medium text-gray-600">{{ t('cvBuilder.cvParse.parsing') }}</p>
      </div>

      <template v-if="!store.parsing && !successMessage">
        <FileUpload
          mode="basic"
          accept=".pdf,.docx"
          :maxFileSize="10000000"
          :chooseLabel="t('cvBuilder.cvParse.chooseFile')"
          :auto="false"
          @select="onFileSelect"
          @clear="onFileClear"
        />
      </template>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          text
          :disabled="store.parsing"
          @click="visible = false"
        />
        <Button
          v-if="selectedFile && !successMessage"
          :label="t('cvBuilder.cvParse.parseButton')"
          icon="pi pi-sparkles"
          :loading="store.parsing"
          @click="handleParse"
        />
      </div>
    </template>
  </Dialog>
</template>
