<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'

const props = defineProps<{
  canGenerate: boolean
  generating: boolean
  hasContext: boolean
}>()

const emit = defineEmits<{ generate: [] }>()

const visible = defineModel<boolean>('visible', { required: true })
const instruction = defineModel<string>('instruction', { required: true })

const { t } = useI18n()
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :draggable="false"
    :header="
      props.hasContext
        ? t('vacancies.form.aiInstructionRegenerateTitle')
        : t('vacancies.form.aiInstructionTitle')
    "
    class="mx-3 w-[calc(100vw-1.5rem)] max-w-xl"
  >
    <div class="space-y-3">
      <p class="text-sm text-gray-600 dark:text-gray-300">
        {{ t('vacancies.form.aiInstructionHint') }}
      </p>
      <Textarea
        v-model="instruction"
        class="w-full"
        rows="6"
        auto-resize
        :placeholder="t('vacancies.form.aiInstructionPlaceholder')"
      />
      <p v-if="props.hasContext" class="text-xs text-gray-500 dark:text-gray-400">
        {{ t('vacancies.form.aiInstructionContextHint') }}
      </p>
    </div>

    <template #footer>
      <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button
          type="button"
          :label="t('common.cancel')"
          severity="secondary"
          text
          :disabled="props.generating"
          @click="visible = false"
        />
        <Button
          type="button"
          :label="
            props.hasContext
              ? t('vacancies.form.regenerateWithAI')
              : t('vacancies.form.generateWithAI')
          "
          icon="pi pi-sparkles"
          :loading="props.generating"
          :disabled="!props.canGenerate"
          @click="emit('generate')"
        />
      </div>
    </template>
  </Dialog>
</template>
