<script setup lang="ts">
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import type {
  ApplicationDetail,
  ApplicationStatus,
} from '../types/candidate.types'

const props = defineProps<{
  candidate: ApplicationDetail
  loading: boolean
}>()

const emit = defineEmits<{
  statusChange: [status: ApplicationStatus]
  downloadCv: []
}>()

const statusOptions = [
  { label: 'Applied', value: 'applied' },
  { label: 'Interview Scheduled', value: 'interview_scheduled' },
  { label: 'Interview In Progress', value: 'interview_in_progress' },
  { label: 'Interview Completed', value: 'interview_completed' },
  { label: 'Reviewing', value: 'reviewing' },
  { label: 'Shortlisted', value: 'shortlisted' },
  { label: 'Rejected', value: 'rejected' },
]

function handleStatusChange(event: { value: ApplicationStatus }): void {
  emit('statusChange', event.value)
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div>
        <p class="text-sm text-gray-500">Name</p>
        <p class="font-medium">{{ props.candidate.candidateName }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Email</p>
        <p class="font-medium">{{ props.candidate.candidateEmail }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Phone</p>
        <p class="font-medium">
          {{ props.candidate.candidatePhone || 'Not provided' }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Vacancy</p>
        <p class="font-medium">{{ props.candidate.vacancyTitle }}</p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Applied</p>
        <p class="font-medium">
          {{ new Date(props.candidate.createdAt).toLocaleDateString() }}
        </p>
      </div>
      <div>
        <p class="text-sm text-gray-500">Match Score</p>
        <p class="font-medium">
          {{
            props.candidate.matchScore !== null
              ? `${props.candidate.matchScore}%`
              : 'Pending'
          }}
        </p>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-3">
      <div>
        <p class="mb-1 text-sm text-gray-500">Status</p>
        <div class="flex items-center gap-2">
          <ApplicationStatusBadge :status="props.candidate.status" />
          <Dropdown
            :model-value="props.candidate.status"
            :options="statusOptions"
            option-label="label"
            option-value="value"
            placeholder="Change status"
            class="w-52"
            :disabled="props.loading"
            @change="handleStatusChange"
          />
        </div>
      </div>
      <div>
        <p class="mb-1 text-sm text-gray-500">CV File</p>
        <Button
          :label="props.candidate.cvOriginalFilename || 'Download CV'"
          icon="pi pi-download"
          size="small"
          outlined
          @click="emit('downloadCv')"
        />
      </div>
    </div>
  </div>
</template>
