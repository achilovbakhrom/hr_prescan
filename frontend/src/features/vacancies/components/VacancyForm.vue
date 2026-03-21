<script setup lang="ts">
import { ref, watch } from 'vue'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import ToggleSwitch from 'primevue/toggleswitch'
import Chips from 'primevue/chips'
import Button from 'primevue/button'
import { EMPLOYMENT_OPTIONS, EXPERIENCE_OPTIONS, CURRENCY_OPTIONS, VISIBILITY_OPTIONS, SCREENING_MODE_OPTIONS } from '../constants/formOptions'
import type { CreateVacancyRequest, EmploymentType, ExperienceLevel, ScreeningMode, VacancyVisibility } from '../types/vacancy.types'

const props = defineProps<{ initialData?: Partial<CreateVacancyRequest>; loading?: boolean }>()
const emit = defineEmits<{ save: [data: CreateVacancyRequest, publish: boolean] }>()

const title = ref(props.initialData?.title ?? '')
const description = ref(props.initialData?.description ?? '')
const requirements = ref(props.initialData?.requirements ?? '')
const responsibilities = ref(props.initialData?.responsibilities ?? '')
const skills = ref<string[]>(props.initialData?.skills ?? [])
const salaryMin = ref<number | null>(props.initialData?.salaryMin ?? null)
const salaryMax = ref<number | null>(props.initialData?.salaryMax ?? null)
const salaryCurrency = ref(props.initialData?.salaryCurrency ?? 'USD')
const location = ref(props.initialData?.location ?? '')
const isRemote = ref(props.initialData?.isRemote ?? false)
const employmentType = ref<EmploymentType>(props.initialData?.employmentType ?? 'full_time')
const experienceLevel = ref<ExperienceLevel>(props.initialData?.experienceLevel ?? 'middle')
const deadline = ref<Date | null>(props.initialData?.deadline ? new Date(props.initialData.deadline) : null)
const visibility = ref<VacancyVisibility>(props.initialData?.visibility ?? 'public')
const screeningMode = ref<ScreeningMode>(props.initialData?.screeningMode ?? 'chat')
const cvRequired = ref(props.initialData?.cvRequired ?? false)
const interviewDuration = ref(props.initialData?.interviewDuration ?? 30)
const companyInfo = ref(props.initialData?.companyInfo ?? '')

watch(() => props.initialData, (d) => {
  if (!d) return
  title.value = d.title ?? ''; description.value = d.description ?? ''
  requirements.value = d.requirements ?? ''; responsibilities.value = d.responsibilities ?? ''
  skills.value = d.skills ?? []; salaryMin.value = d.salaryMin ?? null
  salaryMax.value = d.salaryMax ?? null; salaryCurrency.value = d.salaryCurrency ?? 'USD'
  location.value = d.location ?? ''; isRemote.value = d.isRemote ?? false
  employmentType.value = d.employmentType ?? 'full_time'
  experienceLevel.value = d.experienceLevel ?? 'middle'
  deadline.value = d.deadline ? new Date(d.deadline) : null
  visibility.value = d.visibility ?? 'public'; interviewDuration.value = d.interviewDuration ?? 30
  screeningMode.value = d.screeningMode ?? 'chat'; cvRequired.value = d.cvRequired ?? false
  companyInfo.value = d.companyInfo ?? ''
})

function handleSave(publish: boolean): void {
  emit('save', {
    title: title.value, description: description.value,
    requirements: requirements.value || undefined, responsibilities: responsibilities.value || undefined,
    skills: skills.value.length > 0 ? skills.value : undefined,
    salaryMin: salaryMin.value, salaryMax: salaryMax.value, salaryCurrency: salaryCurrency.value,
    location: location.value || undefined, isRemote: isRemote.value,
    employmentType: employmentType.value, experienceLevel: experienceLevel.value,
    deadline: deadline.value ? deadline.value.toISOString().split('T')[0] : null,
    visibility: visibility.value, screeningMode: screeningMode.value,
    cvRequired: cvRequired.value, interviewDuration: interviewDuration.value,
    companyInfo: companyInfo.value || undefined,
  }, publish)
}
</script>

<template>
  <form class="space-y-6" @submit.prevent="handleSave(false)">
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <h3 class="mb-4 text-lg font-semibold">Basic Information</h3>
      <div class="space-y-4">
        <div><label class="mb-1 block text-sm font-medium">Title *</label>
          <InputText v-model="title" class="w-full" placeholder="e.g. Senior Frontend Developer" /></div>
        <div><label class="mb-1 block text-sm font-medium">Description *</label>
          <Textarea v-model="description" class="w-full" rows="4" placeholder="Job description..." /></div>
        <div><label class="mb-1 block text-sm font-medium">Requirements</label>
          <Textarea v-model="requirements" class="w-full" rows="3" placeholder="Requirements..." /></div>
        <div><label class="mb-1 block text-sm font-medium">Responsibilities</label>
          <Textarea v-model="responsibilities" class="w-full" rows="3" placeholder="Responsibilities..." /></div>
      </div>
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <h3 class="mb-4 text-lg font-semibold">Skills</h3>
      <Chips v-model="skills" class="w-full" placeholder="Add skill and press Enter" />
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <h3 class="mb-4 text-lg font-semibold">Compensation</h3>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div><label class="mb-1 block text-sm font-medium">Min Salary</label>
          <InputNumber v-model="salaryMin" class="w-full" /></div>
        <div><label class="mb-1 block text-sm font-medium">Max Salary</label>
          <InputNumber v-model="salaryMax" class="w-full" /></div>
        <div><label class="mb-1 block text-sm font-medium">Currency</label>
          <Dropdown v-model="salaryCurrency" :options="CURRENCY_OPTIONS" option-label="label" option-value="value" class="w-full" /></div>
      </div>
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <h3 class="mb-4 text-lg font-semibold">Details</h3>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div><label class="mb-1 block text-sm font-medium">Location</label>
          <InputText v-model="location" class="w-full" placeholder="e.g. New York, NY" /></div>
        <div class="flex items-end gap-2"><label class="text-sm font-medium">Remote</label>
          <ToggleSwitch v-model="isRemote" /></div>
        <div><label class="mb-1 block text-sm font-medium">Employment Type</label>
          <Dropdown v-model="employmentType" :options="EMPLOYMENT_OPTIONS" option-label="label" option-value="value" class="w-full" /></div>
        <div><label class="mb-1 block text-sm font-medium">Experience Level</label>
          <Dropdown v-model="experienceLevel" :options="EXPERIENCE_OPTIONS" option-label="label" option-value="value" class="w-full" /></div>
        <div><label class="mb-1 block text-sm font-medium">Deadline</label>
          <Calendar v-model="deadline" class="w-full" date-format="yy-mm-dd" :show-icon="true" /></div>
      </div>
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <h3 class="mb-4 text-lg font-semibold">Company Information (for AI Interview)</h3>
      <p class="mb-2 text-sm text-gray-500">Optional. If provided, the AI interviewer will introduce the company to the candidate at the start of the interview.</p>
      <Textarea v-model="companyInfo" class="w-full" rows="3" placeholder="e.g. We are a leading fintech company based in Tashkent, building next-gen payment solutions..." />
    </div>
    <div class="rounded-lg border border-gray-200 bg-white p-4">
      <h3 class="mb-4 text-lg font-semibold">Settings</h3>
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div><label class="mb-1 block text-sm font-medium">Visibility</label>
          <Dropdown v-model="visibility" :options="VISIBILITY_OPTIONS" option-label="label" option-value="value" class="w-full" /></div>
        <div><label class="mb-1 block text-sm font-medium">Screening Mode</label>
          <Dropdown v-model="screeningMode" :options="SCREENING_MODE_OPTIONS" option-label="label" option-value="value" class="w-full" /></div>
        <div><label class="mb-1 block text-sm font-medium">Interview Duration (min)</label>
          <InputNumber v-model="interviewDuration" class="w-full" :min="10" :max="120" :step="5" /></div>
        <div class="flex items-end gap-2"><label class="text-sm font-medium">CV Required</label>
          <ToggleSwitch v-model="cvRequired" /></div>
      </div>
    </div>
    <div class="flex justify-end gap-3">
      <Button type="submit" label="Save as Draft" severity="secondary" :loading="loading" :disabled="!title || !description" />
      <Button type="button" label="Save & Publish" icon="pi pi-send" :loading="loading" :disabled="!title || !description" @click="handleSave(true)" />
    </div>
  </form>
</template>
