<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Textarea from 'primevue/textarea'
import Dropdown from '@/shared/components/AppSelect.vue'

defineProps<{
  hasError: (field: string) => boolean
  fieldError: (field: string) => string
}>()
const prescanningPrompt = defineModel<string>('prescanningPrompt', { required: true })
const prescanningLanguage = defineModel<string>('prescanningLanguage', { required: true })

const { t } = useI18n()

const languageOptions = [
  { label: 'English', value: 'en' },
  { label: 'Русский', value: 'ru' },
  { label: `O'zbekcha`, value: 'uz' },
]
</script>

<template>
  <div class="space-y-4 py-2">
    <div class="rounded-lg border border-teal-200 bg-teal-50/40 p-4">
      <div class="flex items-center gap-2">
        <i class="pi pi-comments text-teal-600"></i>
        <span class="text-sm font-semibold text-teal-800">{{
          t('vacancies.form.prescanningAlwaysEnabled')
        }}</span>
      </div>
      <p class="mt-2 text-sm text-gray-600">{{ t('vacancies.form.prescanningHint') }}</p>
    </div>

    <div>
      <label class="mb-1 block text-sm font-medium">{{
        t('vacancies.form.prescanningLanguage')
      }}</label>
      <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.prescanningLanguageHint') }}</p>
      <Dropdown
        v-model="prescanningLanguage"
        :options="languageOptions"
        option-label="label"
        option-value="value"
        class="w-full sm:w-60"
      />
    </div>

    <div>
      <label class="mb-1 block text-sm font-medium"
        >{{ t('vacancies.form.prescanningPrompt') }} ({{ t('common.optional') }})</label
      >
      <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.prescanningPromptHint') }}</p>
      <Textarea
        v-model="prescanningPrompt"
        class="w-full"
        rows="5"
        :placeholder="t('vacancies.form.prescanningPromptPlaceholder')"
        :invalid="hasError('prescanningPrompt')"
      />
      <small v-if="hasError('prescanningPrompt')" class="text-red-500">{{
        fieldError('prescanningPrompt')
      }}</small>
    </div>
  </div>
</template>
