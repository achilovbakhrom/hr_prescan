<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import type { FieldErrors } from '@/shared/api/errors'
import type { WorkExperience, WorkExperiencePayload } from '../types/cv-builder.types'

const props = defineProps<{
  editingExp?: WorkExperience | null
  saving: boolean
  improvingDescription: boolean
  fieldErrors: FieldErrors
}>()

const emit = defineEmits<{
  save: [payload: WorkExperiencePayload, editingId: string | null]
  cancel: []
  improveDescription: [text: string]
}>()

const { t } = useI18n()

const companyName = ref(props.editingExp?.companyName ?? '')
const position = ref(props.editingExp?.position ?? '')
const employmentType = ref(props.editingExp?.employmentType ?? '')
const location = ref(props.editingExp?.location ?? '')
const startDate = ref<Date | null>(
  props.editingExp?.startDate ? new Date(props.editingExp.startDate) : null,
)
const endDate = ref<Date | null>(
  props.editingExp?.endDate ? new Date(props.editingExp.endDate) : null,
)
const isCurrent = ref(props.editingExp?.isCurrent ?? false)
const description = ref(props.editingExp?.description ?? '')

const employmentTypeOptions = [
  { label: t('cvBuilder.employmentTypes.fullTime'), value: 'full_time' },
  { label: t('cvBuilder.employmentTypes.partTime'), value: 'part_time' },
  { label: t('cvBuilder.employmentTypes.contract'), value: 'contract' },
  { label: t('cvBuilder.employmentTypes.internship'), value: 'internship' },
]

const editingId = computed(() => props.editingExp?.id ?? null)

function hasError(field: string): boolean {
  return field in props.fieldErrors
}
function fieldError(field: string): string {
  return props.fieldErrors[field] ?? ''
}

function formatDateStr(date: Date | null): string {
  if (!date) return ''
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function handleSubmit(): void {
  emit(
    'save',
    {
      companyName: companyName.value,
      position: position.value,
      employmentType: employmentType.value,
      location: location.value,
      startDate: formatDateStr(startDate.value),
      endDate: isCurrent.value ? null : formatDateStr(endDate.value) || null,
      isCurrent: isCurrent.value,
      description: description.value,
    },
    editingId.value,
  )
}

function setDescription(val: string): void {
  description.value = val
}

defineExpose({ setDescription })
</script>

<template>
  <form
    class="mt-4 flex flex-col gap-4 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
    @submit.prevent="handleSubmit"
  >
    <h3 class="font-semibold text-gray-900">
      {{ editingId ? t('cvBuilder.experience.editTitle') : t('cvBuilder.experience.addTitle') }}
    </h3>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="expCompany" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.experience.companyName') }} <span class="text-red-500">*</span></label
        >
        <InputText
          id="expCompany"
          v-model="companyName"
          class="w-full"
          :invalid="hasError('companyName')"
        />
        <small v-if="hasError('companyName')" class="text-red-500">{{
          fieldError('companyName')
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="expPosition" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.experience.position') }} <span class="text-red-500">*</span></label
        >
        <InputText
          id="expPosition"
          v-model="position"
          class="w-full"
          :invalid="hasError('position')"
        />
        <small v-if="hasError('position')" class="text-red-500">{{ fieldError('position') }}</small>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="expType" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.experience.employmentType')
        }}</label>
        <Select
          id="expType"
          v-model="employmentType"
          :options="employmentTypeOptions"
          optionLabel="label"
          optionValue="value"
          :placeholder="t('cvBuilder.experience.employmentTypePlaceholder')"
          class="w-full"
          :invalid="hasError('employmentType')"
        />
        <small v-if="hasError('employmentType')" class="text-red-500">{{
          fieldError('employmentType')
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="expLocation" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.experience.location')
        }}</label>
        <InputText
          id="expLocation"
          v-model="location"
          class="w-full"
          :invalid="hasError('location')"
        />
        <small v-if="hasError('location')" class="text-red-500">{{ fieldError('location') }}</small>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="expStartDate" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.experience.startDate') }} <span class="text-red-500">*</span></label
        >
        <DatePicker
          id="expStartDate"
          v-model="startDate"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :invalid="hasError('startDate')"
        />
        <small v-if="hasError('startDate')" class="text-red-500">{{
          fieldError('startDate')
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="expEndDate" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.experience.endDate')
        }}</label>
        <DatePicker
          id="expEndDate"
          v-model="endDate"
          dateFormat="yy-mm-dd"
          showIcon
          :disabled="isCurrent"
          class="w-full"
          :invalid="hasError('endDate')"
        />
        <small v-if="hasError('endDate')" class="text-red-500">{{ fieldError('endDate') }}</small>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <Checkbox id="expIsCurrent" v-model="isCurrent" :binary="true" />
      <label for="expIsCurrent" class="text-sm text-gray-700">{{
        t('cvBuilder.experience.currentlyWorking')
      }}</label>
    </div>

    <div class="flex flex-col gap-1">
      <div class="flex items-center justify-between">
        <label for="expDescription" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.experience.description')
        }}</label>
        <Button
          :label="t('cvBuilder.improveWithAi')"
          icon="pi pi-sparkles"
          severity="secondary"
          text
          size="small"
          :loading="improvingDescription"
          :disabled="!description.trim()"
          @click="emit('improveDescription', description)"
        />
      </div>
      <Textarea
        id="expDescription"
        v-model="description"
        rows="3"
        class="w-full"
        :invalid="hasError('description')"
      />
      <small v-if="hasError('description')" class="text-red-500">{{
        fieldError('description')
      }}</small>
    </div>

    <div class="flex justify-end gap-2">
      <Button :label="t('common.cancel')" severity="secondary" text @click="emit('cancel')" />
      <Button type="submit" :label="t('common.save')" :loading="saving" />
    </div>
  </form>
</template>
