<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Editor from 'primevue/editor'
import Dropdown from '@/shared/components/AppSelect.vue'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import ToggleSwitch from 'primevue/toggleswitch'
import Chips from 'primevue/chips'
import {
  getEmploymentOptions,
  getExperienceOptions,
  CURRENCY_OPTIONS,
} from '../constants/formOptions'
import type { EmploymentType, ExperienceLevel } from '../types/vacancy.types'

const props = defineProps<{
  hasError: (field: string) => boolean
  fieldError: (field: string) => string
}>()
const title = defineModel<string>('title', { required: true })
const description = defineModel<string>('description', { required: true })
const requirements = defineModel<string>('requirements', { required: true })
const responsibilities = defineModel<string>('responsibilities', { required: true })
const skills = defineModel<string[]>('skills', { required: true })
const salaryMin = defineModel<number | null>('salaryMin', { required: true })
const salaryMax = defineModel<number | null>('salaryMax', { required: true })
const salaryCurrency = defineModel<string>('salaryCurrency', { required: true })
const location = defineModel<string>('location', { required: true })
const isRemote = defineModel<boolean>('isRemote', { required: true })
const employmentType = defineModel<EmploymentType>('employmentType', { required: true })
const experienceLevel = defineModel<ExperienceLevel>('experienceLevel', { required: true })
const deadline = defineModel<Date | null>('deadline', { required: true })

const { t } = useI18n()
const employmentOptions = computed(() => getEmploymentOptions(t))
const experienceOptions = computed(() => getExperienceOptions(t))
</script>

<template>
  <div class="space-y-4 py-2">
    <div>
      <label class="mb-1 block text-sm font-medium"
        >{{ t('vacancies.form.title') }} <span class="text-red-500">*</span></label
      >
      <InputText
        v-model="title"
        class="w-full"
        :placeholder="t('vacancies.form.titlePlaceholder')"
        :invalid="props.hasError('title')"
      />
      <small v-if="props.hasError('title')" class="text-red-500">{{
        props.fieldError('title')
      }}</small>
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium"
        >{{ t('vacancies.form.description') }} <span class="text-red-500">*</span></label
      >
      <Editor
        v-model="description"
        editorStyle="height: 200px"
        :class="{ 'border border-red-500 rounded-md': props.hasError('description') }"
      />
      <small v-if="props.hasError('description')" class="text-red-500">{{
        props.fieldError('description')
      }}</small>
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.requirements') }}</label>
      <Textarea
        v-model="requirements"
        class="w-full"
        rows="3"
        :placeholder="t('vacancies.form.requirementsPlaceholder')"
        :invalid="props.hasError('requirements')"
      />
      <small v-if="props.hasError('requirements')" class="text-red-500">{{
        props.fieldError('requirements')
      }}</small>
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium">{{
        t('vacancies.form.responsibilities')
      }}</label>
      <Textarea
        v-model="responsibilities"
        class="w-full"
        rows="3"
        :placeholder="t('vacancies.form.responsibilitiesPlaceholder')"
        :invalid="props.hasError('responsibilities')"
      />
      <small v-if="props.hasError('responsibilities')" class="text-red-500">{{
        props.fieldError('responsibilities')
      }}</small>
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.skills') }}</label>
      <Chips v-model="skills" class="w-full" :placeholder="t('vacancies.form.skillsPlaceholder')" />
      <small v-if="props.hasError('skills')" class="text-red-500">{{
        props.fieldError('skills')
      }}</small>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.location') }}</label>
        <InputText
          v-model="location"
          class="w-full"
          :placeholder="t('vacancies.form.locationPlaceholder')"
          :invalid="props.hasError('location')"
        />
        <small v-if="props.hasError('location')" class="text-red-500">{{
          props.fieldError('location')
        }}</small>
      </div>
      <div class="flex items-end gap-3 pb-1">
        <label class="text-sm font-medium">{{ t('vacancies.form.remote') }}</label>
        <ToggleSwitch v-model="isRemote" />
      </div>
    </div>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <label class="mb-1 block text-sm font-medium">{{
          t('vacancies.form.employmentType')
        }}</label>
        <Dropdown
          v-model="employmentType"
          :options="employmentOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :invalid="props.hasError('employmentType')"
        />
        <small v-if="props.hasError('employmentType')" class="text-red-500">{{
          props.fieldError('employmentType')
        }}</small>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">{{
          t('vacancies.form.experienceLevel')
        }}</label>
        <Dropdown
          v-model="experienceLevel"
          :options="experienceOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          :invalid="props.hasError('experienceLevel')"
        />
        <small v-if="props.hasError('experienceLevel')" class="text-red-500">{{
          props.fieldError('experienceLevel')
        }}</small>
      </div>
    </div>
    <div>
      <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.deadline') }}</label>
      <Calendar
        v-model="deadline"
        class="w-full md:w-1/2"
        date-format="yy-mm-dd"
        :show-icon="true"
        :invalid="props.hasError('deadline')"
      />
      <small v-if="props.hasError('deadline')" class="text-red-500">{{
        props.fieldError('deadline')
      }}</small>
    </div>

    <h4 class="pt-2 text-sm font-semibold text-gray-700">{{ t('vacancies.form.compensation') }}</h4>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.salaryMin') }}</label>
        <InputNumber v-model="salaryMin" class="w-full" :invalid="props.hasError('salaryMin')" />
        <small v-if="props.hasError('salaryMin')" class="text-red-500">{{
          props.fieldError('salaryMin')
        }}</small>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.salaryMax') }}</label>
        <InputNumber v-model="salaryMax" class="w-full" :invalid="props.hasError('salaryMax')" />
        <small v-if="props.hasError('salaryMax')" class="text-red-500">{{
          props.fieldError('salaryMax')
        }}</small>
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.currency') }}</label>
        <Dropdown
          v-model="salaryCurrency"
          :options="CURRENCY_OPTIONS"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>
    </div>
  </div>
</template>
