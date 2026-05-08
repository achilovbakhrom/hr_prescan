<script setup lang="ts">
import Button from 'primevue/button'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  canGenerate: boolean
  generating: boolean
}>()

const emit = defineEmits<{ generate: [] }>()

const { t } = useI18n()
</script>

<template>
  <div class="mt-3">
    <Button
      type="button"
      :label="t('vacancies.form.generateWithAI')"
      icon="pi pi-sparkles"
      :loading="props.generating"
      :disabled="!props.canGenerate || props.generating"
      class="w-full justify-center !rounded-md !border !border-indigo-200 !bg-indigo-50 !px-4 !py-2.5 !font-semibold !text-indigo-700 !shadow-sm transition hover:!border-indigo-300 hover:!bg-indigo-100 focus:!ring-2 focus:!ring-indigo-200 sm:w-auto dark:!border-indigo-800 dark:!bg-indigo-950/40 dark:!text-indigo-200 dark:hover:!bg-indigo-900/50"
      @click="emit('generate')"
    />
  </div>
</template>
