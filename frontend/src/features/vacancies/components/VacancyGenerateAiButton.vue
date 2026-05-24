<script setup lang="ts">
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  canGenerate: boolean
  generating: boolean
  hasContext?: boolean
}>()

const emit = defineEmits<{ generate: [] }>()

const { t } = useI18n()
</script>

<template>
  <Button
    type="button"
    :label="
      props.hasContext ? t('vacancies.form.regenerateWithAI') : t('vacancies.form.generateWithAI')
    "
    icon="pi pi-sparkles"
    size="small"
    :loading="props.generating"
    :disabled="!props.canGenerate || props.generating"
    class="shrink-0 !rounded-md !border !border-indigo-200 !bg-indigo-50 !px-3 !py-1.5 !text-xs !font-semibold !text-indigo-700 !shadow-sm transition hover:!border-indigo-300 hover:!bg-indigo-100 focus:!ring-2 focus:!ring-indigo-200 dark:!border-indigo-800 dark:!bg-indigo-950/40 dark:!text-indigo-200 dark:hover:!bg-indigo-900/50"
    @click="emit('generate')"
  />
</template>
