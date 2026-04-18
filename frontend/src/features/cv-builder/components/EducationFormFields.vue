<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import EducationLevelSelect from '@/shared/components/EducationLevelSelect.vue'
import type { FieldErrors } from '@/shared/api/errors'

defineProps<{
  institution: string
  degree: string
  educationLevel: string
  fieldOfStudy: string
  startDate: Date | null
  endDate: Date | null
  description: string
  editingId: string | null
  saving: boolean
  fieldErrors: FieldErrors
}>()

const emit = defineEmits<{
  'update:institution': [v: string]
  'update:degree': [v: string]
  'update:educationLevel': [v: string]
  'update:fieldOfStudy': [v: string]
  'update:startDate': [v: Date | null]
  'update:endDate': [v: Date | null]
  'update:description': [v: string]
  save: []
  cancel: []
}>()

const { t } = useI18n()
</script>

<template>
  <form
    class="mt-4 flex flex-col gap-4 rounded-lg border border-gray-200 p-4"
    @submit.prevent="emit('save')"
  >
    <h3 class="font-semibold text-gray-900">
      {{ editingId ? t('cvBuilder.education.editTitle') : t('cvBuilder.education.addTitle') }}
    </h3>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="eduInstitution" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.education.institution') }} <span class="text-red-500">*</span></label
        >
        <InputText
          id="eduInstitution"
          :model-value="institution"
          class="w-full"
          :invalid="'institution' in fieldErrors"
          @update:model-value="emit('update:institution', $event as string)"
        />
        <small v-if="'institution' in fieldErrors" class="text-red-500">{{
          fieldErrors.institution
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="eduDegree" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.education.degree')
        }}</label>
        <InputText
          id="eduDegree"
          :model-value="degree"
          class="w-full"
          :invalid="'degree' in fieldErrors"
          @update:model-value="emit('update:degree', $event as string)"
        />
        <small v-if="'degree' in fieldErrors" class="text-red-500">{{ fieldErrors.degree }}</small>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.education.educationLevel')
        }}</label>
        <EducationLevelSelect
          :model-value="educationLevel"
          @update:model-value="emit('update:educationLevel', $event)"
        />
        <small v-if="'educationLevel' in fieldErrors" class="text-red-500">{{
          fieldErrors.educationLevel
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="eduFieldOfStudy" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.education.fieldOfStudy')
        }}</label>
        <InputText
          id="eduFieldOfStudy"
          :model-value="fieldOfStudy"
          class="w-full"
          :invalid="'fieldOfStudy' in fieldErrors"
          @update:model-value="emit('update:fieldOfStudy', $event as string)"
        />
        <small v-if="'fieldOfStudy' in fieldErrors" class="text-red-500">{{
          fieldErrors.fieldOfStudy
        }}</small>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="eduStartDate" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.education.startDate')
        }}</label>
        <DatePicker
          id="eduStartDate"
          :model-value="startDate"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :invalid="'startDate' in fieldErrors"
          @update:model-value="emit('update:startDate', $event as Date | null)"
        />
        <small v-if="'startDate' in fieldErrors" class="text-red-500">{{
          fieldErrors.startDate
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="eduEndDate" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.education.endDate')
        }}</label>
        <DatePicker
          id="eduEndDate"
          :model-value="endDate"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :invalid="'endDate' in fieldErrors"
          @update:model-value="emit('update:endDate', $event as Date | null)"
        />
        <small v-if="'endDate' in fieldErrors" class="text-red-500">{{
          fieldErrors.endDate
        }}</small>
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <label for="eduDescription" class="text-sm font-medium text-gray-700">{{
        t('cvBuilder.education.description')
      }}</label>
      <Textarea
        id="eduDescription"
        :model-value="description"
        rows="3"
        class="w-full"
        :invalid="'description' in fieldErrors"
        @update:model-value="emit('update:description', $event as string)"
      />
      <small v-if="'description' in fieldErrors" class="text-red-500">{{
        fieldErrors.description
      }}</small>
    </div>

    <div class="flex justify-end gap-2">
      <Button :label="t('common.cancel')" severity="secondary" text @click="emit('cancel')" />
      <Button type="submit" :label="t('common.save')" :loading="saving" />
    </div>
  </form>
</template>
