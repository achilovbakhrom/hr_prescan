<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Interview, InterviewStatus } from '../types/interview.types'

const router = useRouter()
const interviewStore = useInterviewStore()
const statusFilter = ref<string | undefined>(undefined)

const statusOptions = [
  { label: 'All Statuses', value: undefined },
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' },
  { label: 'Expired', value: 'expired' },
]

const interviews = computed(() => interviewStore.interviews)

onMounted(() => interviewStore.fetchInterviews())

function handleFilterChange(): void {
  interviewStore.fetchInterviews(
    statusFilter.value ? { status: statusFilter.value } : undefined,
  )
}

function handleRowClick(event: { data: Interview }): void {
  router.push({
    name: ROUTE_NAMES.INTERVIEW_DETAIL,
    params: { id: event.data.id },
  })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}

function formatScore(score: number | null): string {
  return score !== null ? `${score}/100` : '-'
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Interviews</h1>
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by status"
        class="w-48"
        @change="handleFilterChange"
      />
    </div>

    <p v-if="interviewStore.error" class="text-sm text-red-600">
      {{ interviewStore.error }}
    </p>

    <DataTable
      :value="interviews"
      :loading="interviewStore.loading"
      striped-rows
      hoverable-rows
      class="cursor-pointer"
      @row-click="handleRowClick"
    >
      <Column field="candidateName" header="Candidate" sortable />
      <Column field="vacancyTitle" header="Vacancy" sortable />
      <Column header="Created" sortable sort-field="createdAt">
        <template #body="{ data }">
          {{ formatDate((data as Interview).createdAt) }}
        </template>
      </Column>
      <Column header="Status" sort-field="status">
        <template #body="{ data }">
          <InterviewStatusBadge :status="(data as Interview).status" />
        </template>
      </Column>
      <Column header="Score">
        <template #body="{ data }">
          {{ formatScore((data as Interview).overallScore) }}
        </template>
      </Column>

      <template #empty>
        <div class="py-8 text-center text-gray-500">
          No interviews found.
        </div>
      </template>
    </DataTable>
  </div>
</template>
