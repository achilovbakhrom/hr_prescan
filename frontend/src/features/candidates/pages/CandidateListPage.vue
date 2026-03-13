<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import { useCandidateStore } from '../stores/candidate.store'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application } from '../types/candidate.types'

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const vacancyId = computed(() => route.params.vacancyId as string)

const statusFilter = ref<string | undefined>(undefined)
const orderingFilter = ref<string>('-created_at')

const statusOptions = [
  { label: 'All Statuses', value: undefined },
  { label: 'Applied', value: 'applied' },
  { label: 'Interview Scheduled', value: 'interview_scheduled' },
  { label: 'Interview In Progress', value: 'interview_in_progress' },
  { label: 'Interview Completed', value: 'interview_completed' },
  { label: 'Reviewing', value: 'reviewing' },
  { label: 'Shortlisted', value: 'shortlisted' },
  { label: 'Rejected', value: 'rejected' },
]

const orderingOptions = [
  { label: 'Newest first', value: '-created_at' },
  { label: 'Oldest first', value: 'created_at' },
  { label: 'Highest score', value: '-match_score' },
  { label: 'Lowest score', value: 'match_score' },
]

function fetchCandidates(): void {
  candidateStore.fetchVacancyCandidates(vacancyId.value, {
    status: statusFilter.value,
    ordering: orderingFilter.value,
  })
}

onMounted(fetchCandidates)
watch([statusFilter, orderingFilter], fetchCandidates)

function viewDetail(candidate: Application): void {
  router.push({
    name: ROUTE_NAMES.CANDIDATE_DETAIL,
    params: { id: candidate.id },
  })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-gray-500 hover:text-gray-700"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">Candidates</h1>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <div class="flex flex-wrap gap-3">
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by status"
        class="w-48"
      />
      <Dropdown
        v-model="orderingFilter"
        :options="orderingOptions"
        option-label="label"
        option-value="value"
        placeholder="Sort by"
        class="w-48"
      />
    </div>

    <DataTable
      :value="candidateStore.candidates"
      :loading="candidateStore.loading"
      striped-rows
      row-hover
      class="cursor-pointer"
      @row-click="(e: { data: Application }) => viewDetail(e.data)"
    >
      <Column field="candidateName" header="Name" sortable />
      <Column field="candidateEmail" header="Email" sortable />
      <Column header="Status">
        <template #body="{ data }">
          <ApplicationStatusBadge :status="(data as Application).status" />
        </template>
      </Column>
      <Column header="Match Score" sortable sort-field="matchScore">
        <template #body="{ data }">
          {{
            (data as Application).matchScore !== null
              ? `${(data as Application).matchScore}%`
              : 'Pending'
          }}
        </template>
      </Column>
      <Column header="Applied" sortable sort-field="createdAt">
        <template #body="{ data }">
          {{ formatDate((data as Application).createdAt) }}
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          <i class="pi pi-users mb-2 text-3xl"></i>
          <p>No candidates have applied yet</p>
        </div>
      </template>
    </DataTable>
  </div>
</template>
