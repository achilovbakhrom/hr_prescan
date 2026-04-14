<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Tag from 'primevue/tag'
import { useInterviewStore } from '../stores/interview.store'
import InterviewStatusBadge from '../components/InterviewStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Interview } from '../types/interview.types'

const { t } = useI18n()

const router = useRouter()
const interviewStore = useInterviewStore()
const statusFilter = ref<string | undefined>(undefined)

const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: undefined },
  { label: t('interviews.status.pending'), value: 'pending' },
  { label: t('interviews.status.inProgress'), value: 'in_progress' },
  { label: t('interviews.status.completed'), value: 'completed' },
  { label: t('interviews.status.cancelled'), value: 'cancelled' },
  { label: t('interviews.status.expired'), value: 'expired' },
])

const interviews = computed(() => interviewStore.interviews)

onMounted(() => interviewStore.fetchInterviews())

function handleFilterChange(): void {
  interviewStore.fetchInterviews(statusFilter.value ? { status: statusFilter.value } : undefined)
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
  return score !== null ? `${score}/10` : '-'
}

function formatSessionType(type: string): string {
  return type === 'prescanning' ? t('candidates.prescanning') : t('candidates.interview')
}

function sessionTypeSeverity(type: string): string {
  return type === 'prescanning' ? 'info' : 'success'
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-lg font-bold md:text-2xl">{{ t('interviews.title') }}</h1>
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by status"
        class="w-full sm:w-48"
        @change="handleFilterChange"
      />
    </div>

    <p v-if="interviewStore.error" class="text-sm text-red-600">
      {{ interviewStore.error }}
    </p>

    <!-- Mobile card view -->
    <div class="space-y-3 md:hidden">
      <div v-if="interviewStore.loading" class="py-8 text-center">
        <i class="pi pi-spinner pi-spin text-2xl text-gray-300"></i>
      </div>
      <div v-else-if="interviews.length === 0" class="py-8 text-center text-gray-500">
        {{ t('common.noResults') }}
      </div>
      <div
        v-for="interview in interviews"
        :key="interview.id"
        class="cursor-pointer rounded-xl border border-gray-100 bg-white p-4 transition-all hover:shadow-sm"
        @click="router.push({ name: ROUTE_NAMES.INTERVIEW_DETAIL, params: { id: interview.id } })"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0 flex-1">
            <p class="font-medium text-gray-900">{{ interview.candidateName }}</p>
            <p class="text-xs text-gray-500">{{ interview.vacancyTitle }}</p>
          </div>
          <div class="flex flex-col items-end gap-1">
            <Tag
              :value="formatSessionType(interview.sessionType)"
              :severity="sessionTypeSeverity(interview.sessionType)"
              class="text-[10px]"
            />
            <InterviewStatusBadge :status="interview.status" />
          </div>
        </div>
        <div class="mt-2 flex items-center justify-between text-xs text-gray-400">
          <span>{{ formatDate(interview.createdAt) }}</span>
          <span v-if="interview.overallScore !== null" class="font-semibold text-gray-700">{{
            formatScore(interview.overallScore)
          }}</span>
        </div>
      </div>
    </div>

    <!-- Desktop table view -->
    <div class="hidden md:block">
      <DataTable
        :value="interviews"
        :loading="interviewStore.loading"
        striped-rows
        hoverable-rows
        class="cursor-pointer"
        @row-click="handleRowClick"
      >
        <Column field="candidateName" :header="t('nav.candidates')" sortable />
        <Column field="vacancyTitle" :header="t('nav.vacancies')" sortable />
        <Column :header="t('interviews.title')" sort-field="sessionType">
          <template #body="{ data }">
            <Tag
              :value="formatSessionType((data as Interview).sessionType)"
              :severity="sessionTypeSeverity((data as Interview).sessionType)"
            />
          </template>
        </Column>
        <Column :header="t('common.createdAt')" sortable sort-field="createdAt">
          <template #body="{ data }">
            {{ formatDate((data as Interview).createdAt) }}
          </template>
        </Column>
        <Column :header="t('common.status')" sort-field="status">
          <template #body="{ data }">
            <InterviewStatusBadge :status="(data as Interview).status" />
          </template>
        </Column>
        <Column :header="t('interviews.overallScore')">
          <template #body="{ data }">
            {{ formatScore((data as Interview).overallScore) }}
          </template>
        </Column>

        <template #empty>
          <div class="py-8 text-center text-gray-500">
            {{ t('common.noResults') }}
          </div>
        </template>
      </DataTable>
    </div>
  </div>
</template>
