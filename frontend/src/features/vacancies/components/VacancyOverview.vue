<script setup lang="ts">
import Tag from 'primevue/tag'
import type { VacancyDetail } from '../types/vacancy.types'
import { formatMoney } from '../composables/useVacancyLabels'

const props = defineProps<{
  vacancy: VacancyDetail
}>()

const employmentLabel: Record<string, string> = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  internship: 'Internship',
}

const experienceLabel: Record<string, string> = {
  junior: 'Junior',
  middle: 'Middle',
  senior: 'Senior',
  lead: 'Lead',
  director: 'Director',
}

function formatSalary(): string {
  const { salaryMin, salaryMax, salaryCurrency } = props.vacancy
  if (!salaryMin && !salaryMax) return 'Not specified'
  if (salaryMin && salaryMax) {
    return `${formatMoney(salaryMin)} - ${formatMoney(salaryMax)} ${salaryCurrency}`
  }
  if (salaryMin) return `From ${formatMoney(salaryMin)} ${salaryCurrency}`
  return `Up to ${formatMoney(salaryMax!)} ${salaryCurrency}`
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div>
        <p class="text-sm text-gray-500">Employment</p>
        <p class="font-medium">
          {{ employmentLabel[vacancy.employmentType] }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Experience</p>
        <p class="font-medium">
          {{ experienceLabel[vacancy.experienceLevel] }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Location</p>
        <p class="font-medium">
          {{ vacancy.location || 'Not specified' }}
          <Tag v-if="vacancy.isRemote" value="Remote" severity="info" class="ml-1" />
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Salary</p>
        <p class="font-medium">{{ formatSalary() }}</p>
      </div>
    </div>

    <!-- Screening Pipeline -->
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div>
        <p class="text-sm text-gray-500">Prescanning</p>
        <p class="font-medium">
          <Tag value="Always On" severity="success" />
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Interview</p>
        <p class="font-medium">
          <Tag
            :value="vacancy.interviewEnabled ? 'Enabled' : 'Disabled'"
            :severity="vacancy.interviewEnabled ? 'success' : 'secondary'"
          />
        </p>
      </div>
      <div v-if="vacancy.interviewEnabled">
        <p class="text-sm text-gray-500">Interview Mode</p>
        <p class="font-medium">
          {{ vacancy.interviewMode === 'meet' ? 'Meet (Video)' : 'Chat' }}
        </p>
      </div>
      <div v-if="vacancy.interviewEnabled && vacancy.interviewMode === 'meet'">
        <p class="text-sm text-gray-500">Interview Duration</p>
        <p class="font-medium">{{ vacancy.interviewDuration }} min</p>
      </div>
    </div>

    <div v-if="vacancy.skills.length > 0">
      <p class="mb-1 text-sm text-gray-500">Skills</p>
      <div class="flex flex-wrap gap-1">
        <Tag
          v-for="skill in vacancy.skills"
          :key="skill"
          :value="skill"
          severity="secondary"
        />
      </div>
    </div>
  </div>
</template>
