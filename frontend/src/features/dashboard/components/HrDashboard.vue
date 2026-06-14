<script setup lang="ts">
/**
 * HrDashboard — redesigned to match the Figma dashboard composition:
 *   - 4 KPI cards (active vacancies, candidates screened, interviews, avg score)
 *   - 2-column body: Recent candidates table (left) + Upcoming interviews and
 *     Hiring funnel (right rail).
 * Data comes from the dashboard stats endpoint + company analytics (funnel).
 */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDashboardStore } from '../stores/dashboard.store'
import { useAnalyticsStore } from '../stores/analytics.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import DashboardStatsCard from './DashboardStatsCard.vue'
import RecentApplicationsTable from './RecentApplicationsTable.vue'
import UpcomingInterviewsTable from './UpcomingInterviewsTable.vue'
import HiringFunnel from './HiringFunnel.vue'

const router = useRouter()
const { t } = useI18n()
const dashboardStore = useDashboardStore()
const analyticsStore = useAnalyticsStore()

const stats = computed(() => dashboardStore.stats)
const funnel = computed(() => analyticsStore.analytics?.funnel ?? null)

const avgScore = computed(() => {
  // Backend average is 0–100; the design shows the score on a /10 scale.
  const s = stats.value?.averageMatchScore
  return s == null ? '—' : (s / 10).toFixed(1)
})

onMounted(() => {
  void dashboardStore.fetchStats()
  void analyticsStore.fetchAnalytics()
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- KPI cards -->
    <div class="grid grid-cols-2 gap-4 xl:grid-cols-4">
      <DashboardStatsCard
        icon="pi pi-briefcase"
        icon-accent="default"
        :label="t('dashboard.activeVacancies')"
        :value="stats?.activeVacanciesCount ?? 0"
        clickable
        @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
      />
      <DashboardStatsCard
        icon="pi pi-users"
        icon-accent="teal"
        :label="t('dashboard.candidatesScreened')"
        :value="stats?.totalCandidatesCount ?? 0"
        clickable
        @click="router.push({ name: ROUTE_NAMES.CANDIDATE_LIST })"
      />
      <DashboardStatsCard
        icon="pi pi-video"
        icon-accent="celebrate"
        :label="t('dashboard.pendingInterviews')"
        :value="stats?.pendingInterviewsCount ?? 0"
        :sublabel="`${stats?.completedInterviewsCount ?? 0} ${t('dashboard.stats.completed')}`"
        clickable
        @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
      />
      <DashboardStatsCard
        icon="pi pi-star"
        icon-accent="success"
        :label="t('dashboard.avgScore')"
        :value="avgScore"
      />
    </div>

    <!-- Body: recent candidates + rail -->
    <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
      <RecentApplicationsTable :applications="stats?.recentApplications ?? []" />
      <aside class="flex flex-col gap-6">
        <UpcomingInterviewsTable :interviews="stats?.upcomingInterviews ?? []" />
        <HiringFunnel :funnel="funnel" />
      </aside>
    </div>
  </div>
</template>
