<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import { useCvBuilderStore } from '../stores/cv-builder.store'

const { t } = useI18n()
const store = useCvBuilderStore()

const visible = ref(false)
const selectedTemplate = ref('classic')
const cvName = ref('My CV')
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

interface TemplateOption {
  value: string
  icon: string
}

const templates: TemplateOption[] = [
  { value: 'classic', icon: 'pi pi-file' },
  { value: 'modern', icon: 'pi pi-th-large' },
  { value: 'minimal', icon: 'pi pi-minus' },
]

function open(): void {
  successMessage.value = null
  errorMessage.value = null
  visible.value = true
}

function selectTemplate(value: string): void {
  selectedTemplate.value = value
}

async function handleGenerate(): Promise<void> {
  successMessage.value = null
  errorMessage.value = null

  try {
    const result = await store.generatePdf(selectedTemplate.value, cvName.value)
    successMessage.value = t('cvBuilder.cvGenerate.success')
    if (result.downloadUrl) {
      window.open(result.downloadUrl, '_blank')
    }
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  }
}

defineExpose({ open })
</script>

<template>
  <Button
    :label="t('cvBuilder.cvGenerate.generateButton')"
    icon="pi pi-file-pdf"
    size="small"
    @click="open"
  />

  <Dialog
    v-model:visible="visible"
    :header="t('cvBuilder.cvGenerate.title')"
    modal
    :style="{ width: '550px' }"
    :breakpoints="{ '640px': '95vw' }"
    :closable="!store.generating"
  >
    <div class="space-y-4">
      <p class="text-sm text-gray-500">
        {{ t('cvBuilder.cvGenerate.description') }}
      </p>

      <Message v-if="successMessage" severity="success">{{ successMessage }}</Message>
      <Message v-if="errorMessage" severity="error">{{ errorMessage }}</Message>

      <!-- Template cards -->
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div
          v-for="tpl in templates"
          :key="tpl.value"
          class="cursor-pointer rounded-lg border-2 p-4 text-center transition-colors"
          :class="
            selectedTemplate === tpl.value
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300'
          "
          @click="selectTemplate(tpl.value)"
        >
          <i :class="tpl.icon" class="mb-2 text-2xl text-gray-600"></i>
          <div class="text-sm font-semibold text-gray-800">
            {{ t(`cvBuilder.cvGenerate.templates.${tpl.value}.name`) }}
          </div>
          <div class="mt-1 text-xs text-gray-500">
            {{ t(`cvBuilder.cvGenerate.templates.${tpl.value}.description`) }}
          </div>
        </div>
      </div>

      <!-- CV Name -->
      <div class="flex flex-col gap-1">
        <label for="cvName" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.cvGenerate.cvName') }}
        </label>
        <InputText
          id="cvName"
          v-model="cvName"
          :placeholder="t('cvBuilder.cvGenerate.cvNamePlaceholder')"
          class="w-full"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          text
          :disabled="store.generating"
          @click="visible = false"
        />
        <Button
          :label="t('cvBuilder.cvGenerate.generateButton')"
          icon="pi pi-file-pdf"
          :loading="store.generating"
          @click="handleGenerate"
        />
      </div>
    </template>
  </Dialog>
</template>
