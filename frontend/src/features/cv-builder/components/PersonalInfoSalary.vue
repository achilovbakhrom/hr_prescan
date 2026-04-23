<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputNumber from 'primevue/inputnumber'
import Select from '@/shared/components/AppSelect.vue'
import ToggleSwitch from 'primevue/toggleswitch'

defineProps<{
  salaryMin: number | null
  salaryMax: number | null
  currency: string
  negotiable: boolean
  employmentType: string
  isOpenToWork: boolean
  fieldErrors: Record<string, string>
}>()

const emit = defineEmits<{
  'update:salaryMin': [value: number | null]
  'update:salaryMax': [value: number | null]
  'update:currency': [value: string]
  'update:negotiable': [value: boolean]
  'update:employmentType': [value: string]
  'update:isOpenToWork': [value: boolean]
}>()

const { t } = useI18n()

const currencyOptions = [
  { label: 'USD', value: 'USD' },
  { label: 'EUR', value: 'EUR' },
  { label: 'GBP', value: 'GBP' },
  { label: 'RUB', value: 'RUB' },
]

const employmentTypeOptions = [
  { label: t('cvBuilder.employmentTypes.fullTime'), value: 'full_time' },
  { label: t('cvBuilder.employmentTypes.partTime'), value: 'part_time' },
  { label: t('cvBuilder.employmentTypes.contract'), value: 'contract' },
  { label: t('cvBuilder.employmentTypes.internship'), value: 'internship' },
]
</script>

<template>
  <div class="flex flex-col gap-5">
    <div class="flex items-center gap-3">
      <ToggleSwitch
        :model-value="negotiable"
        @update:model-value="emit('update:negotiable', $event)"
      />
      <label class="text-sm font-medium text-gray-700">
        {{ t('cvBuilder.personal.salaryNegotiable') }}
      </label>
    </div>

    <div v-if="!negotiable" class="grid grid-cols-1 gap-5 sm:grid-cols-3">
      <div class="flex flex-col gap-1">
        <label for="salaryMin" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.salaryMin') }} <span class="text-red-500">*</span>
        </label>
        <InputNumber
          id="salaryMin"
          :model-value="salaryMin"
          :placeholder="t('cvBuilder.personal.salaryMinPlaceholder')"
          class="w-full"
          :invalid="'desiredSalaryMin' in fieldErrors"
          @update:model-value="emit('update:salaryMin', $event)"
        />
        <small v-if="'desiredSalaryMin' in fieldErrors" class="text-red-500">{{
          fieldErrors.desiredSalaryMin
        }}</small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="salaryMax" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.salaryMax') }} <span class="text-red-500">*</span>
        </label>
        <InputNumber
          id="salaryMax"
          :model-value="salaryMax"
          :placeholder="t('cvBuilder.personal.salaryMaxPlaceholder')"
          class="w-full"
          :invalid="'desiredSalaryMax' in fieldErrors"
          @update:model-value="emit('update:salaryMax', $event)"
        />
        <small v-if="'desiredSalaryMax' in fieldErrors" class="text-red-500">{{
          fieldErrors.desiredSalaryMax
        }}</small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="currency" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.currency') }}
        </label>
        <Select
          id="currency"
          :model-value="currency"
          :options="currencyOptions"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('cvBuilder.personal.currencyPlaceholder')"
          class="w-full"
          :invalid="'desiredSalaryCurrency' in fieldErrors"
          @update:model-value="emit('update:currency', $event as string)"
        />
        <small v-if="'desiredSalaryCurrency' in fieldErrors" class="text-red-500">{{
          fieldErrors.desiredSalaryCurrency
        }}</small>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="employmentType" class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.employmentType') }} <span class="text-red-500">*</span>
        </label>
        <Select
          id="employmentType"
          :model-value="employmentType"
          :options="employmentTypeOptions"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('cvBuilder.personal.employmentTypePlaceholder')"
          class="w-full"
          :invalid="'desiredEmploymentType' in fieldErrors"
          @update:model-value="emit('update:employmentType', $event as string)"
        />
        <small v-if="'desiredEmploymentType' in fieldErrors" class="text-red-500">{{
          fieldErrors.desiredEmploymentType
        }}</small>
      </div>

      <div class="flex items-center gap-3 pt-6">
        <ToggleSwitch
          :model-value="isOpenToWork"
          @update:model-value="emit('update:isOpenToWork', $event)"
        />
        <label class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.personal.openToWork') }}
        </label>
      </div>
    </div>
  </div>
</template>
