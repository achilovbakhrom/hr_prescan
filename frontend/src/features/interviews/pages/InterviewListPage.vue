<script setup lang="ts">
/**
 * InterviewListPage — HR-facing interview list.
 * Glass toolbar + GlassCard wrapping a solid DataTable.
 * Spec: docs/design/spec.md §9 Interviews (HR list).
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Dropdown from 'primevue/dropdown'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import InterviewListTable from '../components/InterviewListTable.vue'
import { useInterviewStore } from '../stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

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
        placeholder="Filter by status"
        class="w-full sm:w-48"
        @change="handleFilterChange"
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
