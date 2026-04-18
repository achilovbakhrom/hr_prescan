<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Editor from 'primevue/editor'
import Button from 'primevue/button'
import { useCvBuilderStore } from '../stores/cv-builder.store'

const props = defineProps<{
  headline: string
  summary: string
  fieldErrors: Record<string, string>
}>()

const emit = defineEmits<{
  'update:headline': [value: string]
  'update:summary': [value: string]
  error: [message: string]
}>()

const { t } = useI18n()
const store = useCvBuilderStore()

const improvingHeadline = ref(false)
const improvingSummary = ref(false)

function hasError(field: string): boolean {
  return field in props.fieldErrors
}

function fieldError(field: string): string {
  return props.fieldErrors[field] ?? ''
}

async function handleImproveHeadline(): Promise<void> {
  if (!props.headline.trim()) return
  improvingHeadline.value = true
  try {
    const improved = await store.improveCvSection('headline', props.headline)
    emit('update:headline', improved)
  } catch (err: unknown) {
    emit('error', err instanceof Error ? err.message : t('common.error'))
  } finally {
    improvingHeadline.value = false
  }
}

async function handleImproveSummary(): Promise<void> {
  if (!props.summary.trim()) return
  improvingSummary.value = true
  try {
    const improved = await store.improveCvSection('summary', props.summary)
    emit('update:summary', improved)
  } catch (err: unknown) {
    emit('error', err instanceof Error ? err.message : t('common.error'))
  } finally {
    improvingSummary.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <div class="flex flex-col gap-1">
      <div class="flex items-center justify-between">
        <label for="headline" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.personal.headline') }} <span class="text-red-500">*</span></label
        >
        <Button
          :label="t('cvBuilder.improveWithAi')"
          icon="pi pi-sparkles"
          severity="secondary"
          text
          size="small"
          :loading="improvingHeadline"
          :disabled="!headline.trim()"
          @click="handleImproveHeadline"
        />
      </div>
      <InputText
        id="headline"
        :model-value="headline"
        :placeholder="t('cvBuilder.personal.headlinePlaceholder')"
        class="w-full"
        :invalid="hasError('headline')"
        @update:model-value="emit('update:headline', $event ?? '')"
      />
      <small v-if="hasError('headline')" class="text-red-500">{{ fieldError('headline') }}</small>
    </div>

    <div class="flex flex-col gap-1">
      <div class="flex items-center justify-between">
        <label for="summary" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.personal.summary') }} <span class="text-red-500">*</span></label
        >
        <Button
          :label="t('cvBuilder.improveWithAi')"
          icon="pi pi-sparkles"
          severity="secondary"
          text
          size="small"
          :loading="improvingSummary"
          :disabled="!summary.trim()"
          @click="handleImproveSummary"
        />
      </div>
      <Editor
        :model-value="summary"
        :data-field-error="hasError('summary') || undefined"
        editorStyle="height: 150px"
        :class="{ 'border border-red-500 rounded-md': hasError('summary') }"
        @update:model-value="emit('update:summary', $event ?? '')"
      />
      <small v-if="hasError('summary')" class="text-red-500">{{ fieldError('summary') }}</small>
    </div>
  </div>
</template>
