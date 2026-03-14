<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { useDashboardStore } from '../stores/dashboard.store'
import StatsCard from '../components/StatsCard.vue'
import RecentApplicationsTable from '../components/RecentApplicationsTable.vue'
import UpcomingInterviewsTable from '../components/UpcomingInterviewsTable.vue'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()

const stats = computed(() => dashboardStore.stats)

const averageScoreDisplay = computed(() => {
  if (stats.value?.averageMatchScore === null || stats.value?.averageMatchScore === undefined) {
    return 'N/A'
  }
  return `${Math.round(stats.value.averageMatchScore)}%`
})

const averageScoreColor = computed(() => {
  const score = stats.value?.averageMatchScore
  if (score === null || score === undefined) return 'bg-gray-100 text-gray-600'
  if (score >= 80) return 'bg-green-100 text-green-600'
  if (score >= 60) return 'bg-blue-100 text-blue-600'
  if (score >= 40) return 'bg-yellow-100 text-yellow-600'
  return 'bg-red-100 text-red-600'
})

onMounted(() => dashboardStore.fetchStats())
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">
        Welcome, {{ authStore.user?.firstName ?? 'User' }}!
      </h1>
      <p class="mt-1 text-gray-600">Here is your recruitment overview.</p>
    </div>

    <p v-if="dashboardStore.error" class="text-sm text-red-600">
      {{ dashboardStore.error }}
    </p>

    <div
      v-if="dashboardStore.loading && !stats"
      class="py-12 text-center"
    >
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-if="stats">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatsCard
          title="Active Vacancies"
          :value="stats.activeVacanciesCount"
          icon="pi pi-briefcase"
          color="bg-blue-100 text-blue-600"
        />
        <StatsCard
          title="Total Candidates"
          :value="stats.totalCandidatesCount"
          icon="pi pi-users"
          color="bg-purple-100 text-purple-600"
        />
        <StatsCard
          title="Pending Interviews"
          :value="stats.pendingInterviewsCount"
          icon="pi pi-clock"
          color="bg-yellow-100 text-yellow-600"
        />
        <StatsCard
          title="Completed Interviews"
          :value="stats.completedInterviewsCount"
          icon="pi pi-check-circle"
          color="bg-green-100 text-green-600"
        />
        <StatsCard
          title="Avg Match Score"
          :value="averageScoreDisplay"
          icon="pi pi-chart-bar"
          :color="averageScoreColor"
        />
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RecentApplicationsTable
          :applications="stats.recentApplications"
        />
        <UpcomingInterviewsTable
          :interviews="stats.upcomingInterviews"
        />
      </div>
    </template>
  </div>
</template>
