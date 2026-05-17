<script setup lang="ts">
/**
 * InterviewListPage — HR-facing interview list.
 * Glass toolbar + GlassCard wrapping a solid DataTable.
 * Spec: docs/design/spec.md §9 Interviews (HR list).
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import VacancyAutocomplete from '@/features/vacancies/components/VacancyAutocomplete.vue'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import InterviewListTable from '../components/InterviewListTable.vue'
import { useInterviewStore } from '../stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Vacancy } from '@/features/vacancies/types/vacancy.types'

const { t } = useI18n()

const router = useRouter()
const interviewStore = useInterviewStore()
const vacancyStore = useVacancyStore()
const statusFilter = ref<string | undefined>(undefined)
const selectedVacancy = ref<Vacancy | null>(null)

const statusOptions = computed(() => [
  { label: t('vacancies.allStatuses'), value: undefined },
  { label: t('interviews.status.pending'), value: 'pending' },
  { label: t('interviews.status.inProgress'), value: 'in_progress' },
  { label: t('interviews.status.completed'), value: 'completed' },
  { label: t('interviews.status.cancelled'), value: 'cancelled' },
  { label: t('interviews.status.expired'), value: 'expired' },
])

const interviews = computed(() => interviewStore.interviews)
const vacancyOptions = computed(() => vacancyStore.vacancies.filter((v) => v.status !== 'archived'))

onMounted(() => {
  handleFilterChange()
  vacancyStore.fetchVacancies()
})
watch(selectedVacancy, handleFilterChange)

function handleFilterChange(): void {
  interviewStore.fetchInterviews({
    status: statusFilter.value,
    vacancyId: selectedVacancy.value?.id,
  })
}

function openDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.INTERVIEW_DETAIL, params: { id } })
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ t('interviews.title') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ interviews.length }} {{ t('interviews.title').toLowerCase() }}
        </p>
      </div>
    </div>

    <GlassSurface class="flex flex-wrap items-center gap-3 rounded-lg p-3" level="1">
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('candidates.filterByStatus')"
        class="w-full sm:w-48"
        @change="handleFilterChange"
      />
      <VacancyAutocomplete
        v-model="selectedVacancy"
        :vacancies="vacancyOptions"
        :placeholder="t('vacancies.filterByVacancy', 'Filter by vacancy')"
      />
    </GlassSurface>

    <p
      v-if="interviewStore.error"
      class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 px-4 py-2 text-sm text-[color:var(--color-danger)]"
    >
      {{ interviewStore.error }}
    </p>

    <GlassCard class="!p-0 overflow-hidden">
      <InterviewListTable
        :interviews="interviews"
        :loading="interviewStore.loading"
        @open="openDetail"
      />
    </GlassCard>
  </div>
</template>
