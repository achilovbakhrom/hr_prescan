<script setup lang="ts">
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { UpcomingInterview } from '../types/dashboard.types'

defineProps<{
  interviews: UpcomingInterview[]
}>()

const router = useRouter()

function viewDetail(interview: UpcomingInterview): void {
  router.push({
    name: ROUTE_NAMES.INTERVIEW_DETAIL,
    params: { id: interview.id },
  })
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white">
    <div class="border-b border-gray-200 px-5 py-3">
      <h3 class="text-sm font-semibold text-gray-700">Upcoming Interviews</h3>
    </div>
    <DataTable
      :value="interviews"
      striped-rows
      row-hover
      class="cursor-pointer"
      @row-click="(e) => viewDetail(e.data)"
    >
      <Column field="candidateName" header="Candidate" />
      <Column field="vacancyTitle" header="Vacancy" />
      <Column header="Date/Time">
        <template #body="{ data }">
          {{ formatDateTime((data as UpcomingInterview).scheduledAt) }}
        </template>
      </Column>
      <Column field="status" header="Status" />
      <template #empty>
        <div class="py-4 text-center text-sm text-gray-500">
          No upcoming interviews
        </div>
      </template>
    </DataTable>
  </div>
</template>
