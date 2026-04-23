<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import ToggleSwitch from 'primevue/toggleswitch'
import { getInterviewModeOptions } from '../constants/formOptions'
import type { InterviewMode } from '../types/vacancy.types'

defineProps<{
  hasError: (field: string) => boolean
  fieldError: (field: string) => string
}>()
const interviewEnabled = defineModel<boolean>('interviewEnabled', { required: true })
const interviewMode = defineModel<InterviewMode>('interviewMode', { required: true })
const interviewDuration = defineModel<number>('interviewDuration', { required: true })
const interviewPrompt = defineModel<string>('interviewPrompt', { required: true })

const { t } = useI18n()
const interviewModeOptions = computed(() => getInterviewModeOptions(t))
</script>

<template>
  <div class="space-y-4 py-2">
    <div
      class="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50/40 p-4"
    >
      <div>
        <div class="flex items-center gap-2">
          <i class="pi pi-video text-emerald-600"></i>
          <span class="text-sm font-semibold text-emerald-800">{{
            t('vacancies.form.interviewOptional')
          }}</span>
        </div>
        <p class="mt-1 text-sm text-gray-600">{{ t('vacancies.form.interviewHint') }}</p>
      </div>
      <ToggleSwitch v-model="interviewEnabled" />
    </div>

    <div v-if="interviewEnabled" class="space-y-4">
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm font-medium">{{
            t('vacancies.form.interviewMode')
          }}</label>
          <Dropdown
            v-model="interviewMode"
            :options="interviewModeOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            :invalid="hasError('interviewMode')"
          />
          <small v-if="hasError('interviewMode')" class="text-red-500">{{
            fieldError('interviewMode')
          }}</small>
        </div>
        <div v-if="interviewMode === 'meet'">
          <label class="mb-1 block text-sm font-medium">{{
            t('vacancies.form.interviewDuration')
          }}</label>
          <InputNumber
            v-model="interviewDuration"
            class="w-full"
            :min="10"
            :max="120"
            :step="5"
            :invalid="hasError('interviewDuration')"
          />
          <small v-if="hasError('interviewDuration')" class="text-red-500">{{
            fieldError('interviewDuration')
          }}</small>
        </div>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium"
          >{{ t('vacancies.form.interviewPrompt') }} ({{ t('common.optional') }})</label
        >
        <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.interviewPromptHint') }}</p>
        <Textarea
          v-model="interviewPrompt"
          class="w-full"
          rows="5"
          :placeholder="t('vacancies.form.interviewPromptPlaceholder')"
          :invalid="hasError('interviewPrompt')"
        />
        <small v-if="hasError('interviewPrompt')" class="text-red-500">{{
          fieldError('interviewPrompt')
        }}</small>
      </div>
    </div>
  </div>
</template>
