<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import DatePicker from 'primevue/datepicker'

defineProps<{
  location: string
  dateOfBirth: Date | null
  fieldErrors: Record<string, string>
}>()

const emit = defineEmits<{
  'update:location': [value: string]
  'update:dateOfBirth': [value: Date | null]
}>()

const { t } = useI18n()
const maxDateOfBirth = new Date()
maxDateOfBirth.setFullYear(maxDateOfBirth.getFullYear() - 14)

function hasError(field: string, errors: Record<string, string>): boolean {
  return field in errors
}
</script>

<template>
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
    <div class="flex flex-col gap-1">
      <label for="location" class="text-sm font-medium text-gray-700">{{
        t('cvBuilder.personal.location')
      }}</label>
      <InputText
        id="location"
        :model-value="location"
        :placeholder="t('cvBuilder.personal.locationPlaceholder')"
        class="w-full"
        :invalid="hasError('location', fieldErrors)"
        @update:model-value="emit('update:location', $event ?? '')"
      />
      <small v-if="hasError('location', fieldErrors)" class="text-red-500">{{
        fieldErrors.location
      }}</small>
    </div>
    <div class="flex flex-col gap-1">
      <label for="dateOfBirth" class="text-sm font-medium text-gray-700">{{
        t('cvBuilder.personal.dateOfBirth')
      }}</label>
      <DatePicker
        id="dateOfBirth"
        :model-value="dateOfBirth"
        dateFormat="yy-mm-dd"
        :max-date="maxDateOfBirth"
        :placeholder="t('cvBuilder.personal.dateOfBirthPlaceholder')"
        showIcon
        class="w-full"
        :invalid="hasError('dateOfBirth', fieldErrors)"
        @update:model-value="emit('update:dateOfBirth', ($event as Date | null) ?? null)"
      />
      <small v-if="hasError('dateOfBirth', fieldErrors)" class="text-red-500">{{
        fieldErrors.dateOfBirth
      }}</small>
    </div>
  </div>
</template>
