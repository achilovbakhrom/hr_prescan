<script setup lang="ts">
/**
 * HrDashboard — 2-column glass layout per spec §9.
 * Main column: quick-stat metric cards + pipeline overview.
 * Rail column: AI assistant teaser + recent activity feed.
 *
 * Data values and computed metrics preserved from previous version.
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import { useInterviewStore } from '@/features/interviews/stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import DashboardStatsCard from './DashboardStatsCard.vue'
import DashboardPipelineOverview from './DashboardPipelineOverview.vue'
import DashboardActivityFeed from './DashboardActivityFeed.vue'

const router = useRouter()
const { t } = useI18n()
const vacancyStore = useVacancyStore()
const interviewStore = useInterviewStore()

const activeVacancies = computed(
  () => vacancyStore.vacancies.filter((v) => v.status === 'published').length,
)
const draftVacancies = computed(
  () => vacancyStore.vacancies.filter((v) => v.status === 'draft').length,
)
const pausedVacancies = computed(
  () => vacancyStore.vacancies.filter((v) => v.status === 'paused').length,
)
const totalVacancies = computed(() => vacancyStore.vacancies.length)
const scheduledInterviews = computed(
  () => interviewStore.interviews.filter((i) => i.status === 'pending').length,
)
const completedInterviews = computed(
  () => interviewStore.interviews.filter((i) => i.status === 'completed').length,
)
const totalInterviews = computed(() => interviewStore.interviews.length)

const recentInterviews = computed(() =>
  [...interviewStore.interviews]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 6),
)

const statsSublabel = computed(
  () =>
    `${activeVacancies.value} ${t('dashboard.stats.active')} · ${draftVacancies.value} ${t('dashboard.stats.draft')}` +
    (pausedVacancies.value > 0
      ? ` · ${pausedVacancies.value} ${t('vacancies.status.paused').toLowerCase()}`
      : ''),
)
</script>

<template>
  <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
    <!-- Main column -->
    <div class="flex flex-col gap-6">
      <!-- Stats grid -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <DashboardStatsCard
          icon="pi pi-briefcase"
          icon-accent="default"
          :label="t('dashboard.activeVacancies')"
          :value="totalVacancies"
          :sublabel="statsSublabel"
          clickable
          @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
        />
        <DashboardStatsCard
          icon="pi pi-calendar"
          icon-accent="warning"
          :label="t('dashboard.pendingInterviews')"
          :value="scheduledInterviews"
          :sublabel="`${completedInterviews} ${t('dashboard.stats.completed')}`"
          clickable
          @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
        />
        <DashboardStatsCard
          icon="pi pi-check-circle"
          icon-accent="success"
          :label="t('dashboard.completedInterviews')"
          :value="completedInterviews"
          :sublabel="t('dashboard.stats.aiInterviewsDone')"
        />
        <DashboardStatsCard
          icon="pi pi-users"
          icon-accent="ai"
          :label="t('interviews.title')"
          :value="totalInterviews"
          :sublabel="t('dashboard.stats.allTime')"
        />
      </div>

      <!-- Pipeline overview -->
      <DashboardPipelineOverview :vacancies="vacancyStore.vacancies" />
    </div>

    <!-- Rail -->
    <aside class="flex flex-col gap-6">
      <DashboardActivityFeed :interviews="recentInterviews" />
    </aside>
  </div>
</template>
