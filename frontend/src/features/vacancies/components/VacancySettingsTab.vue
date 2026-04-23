<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'
import ToggleSwitch from 'primevue/toggleswitch'
import { getVisibilityOptions } from '../constants/formOptions'
import type { VacancyVisibility } from '../types/vacancy.types'

defineProps<{
  hasError: (field: string) => boolean
  fieldError: (field: string) => string
}>()
const visibility = defineModel<VacancyVisibility>('visibility', { required: true })
const cvRequired = defineModel<boolean>('cvRequired', { required: true })

const { t } = useI18n()
const visibilityOptions = computed(() => getVisibilityOptions(t))
</script>

<template>
  <div class="space-y-5 py-2">
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.visibility') }}</label>
        <Dropdown
          v-model="visibility"
          :options="visibilityOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :invalid="hasError('visibility')"
        />
        <small v-if="hasError('visibility')" class="text-red-500">{{
          fieldError('visibility')
        }}</small>
        <p class="mt-1 text-xs text-gray-400">{{ t('vacancies.form.visibilityPublicHint') }}</p>
      </div>
      <div class="flex items-start gap-3 pt-6">
        <ToggleSwitch v-model="cvRequired" />
        <div>
          <label class="text-sm font-medium">{{ t('vacancies.form.cvRequired') }}</label>
          <p class="text-xs text-gray-400">{{ t('vacancies.form.cvRequiredHint') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
