<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import { useInterviewStore } from '@/features/interviews/stores/interview.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Interview } from '@/features/interviews/types/interview.types'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const vacancyStore = useVacancyStore()
const interviewStore = useInterviewStore()

const role = computed(() => authStore.user?.role)

const activeVacancies = computed(
  () => vacancyStore.vacancies.filter((v) => v.status === 'published').length,
)
const draftVacancies = computed(
  () => vacancyStore.vacancies.filter((v) => v.status === 'draft').length,
)
const totalVacancies = computed(() => vacancyStore.vacancies.length)
const scheduledInterviews = computed(
  () => interviewStore.interviews.filter((i) => i.status === 'pending').length,
)
const completedInterviews = computed(
  () => interviewStore.interviews.filter((i) => i.status === 'completed').length,
)
const upcomingInterviews = computed(() =>
  interviewStore.interviews
    .filter((i) => i.status === 'pending')
    .sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
    .slice(0, 5),
)

function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = d.getTime() - now.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  if (diffDays === 0 && diffHours >= 0) return `Today at ${time}`
  if (diffDays === 1) return `Tomorrow at ${time}`
  return `${d.toLocaleDateString([], { month: 'short', day: 'numeric' })} at ${time}`
}

function goToInterview(interview: Interview): void {
  router.push({ name: ROUTE_NAMES.INTERVIEW_DETAIL, params: { id: interview.id } })
}
</script>

<template>
  <!-- Stats Cards -->
  <div class="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
    <div
      class="cursor-pointer rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5 transition-all hover:shadow-md"
      @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
    >
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
          <i class="pi pi-briefcase text-lg text-blue-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ totalVacancies }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('dashboard.activeVacancies') }}</p>
      <p class="mt-0.5 text-xs text-blue-600">
        {{ activeVacancies }} {{ t('dashboard.stats.active') }}, {{ draftVacancies }}
        {{ t('dashboard.stats.draft') }}
      </p>
    </div>

    <div
      class="cursor-pointer rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5 transition-all hover:shadow-md"
      @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
    >
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
          <i class="pi pi-calendar text-lg text-amber-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ scheduledInterviews }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('dashboard.pendingInterviews') }}</p>
      <p class="mt-0.5 text-xs text-amber-600">
        {{ completedInterviews }} {{ t('dashboard.stats.completed') }}
      </p>
    </div>

    <div class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
          <i class="pi pi-check-circle text-lg text-emerald-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ completedInterviews }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('dashboard.completedInterviews') }}</p>
      <p class="mt-0.5 text-xs text-emerald-600">{{ t('dashboard.stats.aiInterviewsDone') }}</p>
    </div>

    <div class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50">
          <i class="pi pi-users text-lg text-violet-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ interviewStore.interviews.length }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('interviews.title') }}</p>
      <p class="mt-0.5 text-xs text-violet-600">{{ t('dashboard.stats.allTime') }}</p>
    </div>
  </div>

  <div class="grid gap-6 lg:grid-cols-3">
    <!-- Quick Actions -->
    <div class="rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-6">
      <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-400">
        {{ t('dashboard.quickActions') }}
      </h2>
      <div class="space-y-2">
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.VACANCY_CREATE })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
            <i class="pi pi-plus text-sm text-blue-600"></i>
          </div>
          {{ t('dashboard.createVacancy') }}
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
            <i class="pi pi-list text-sm text-emerald-600"></i>
          </div>
          {{ t('nav.vacancies') }}
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50">
            <i class="pi pi-video text-sm text-amber-600"></i>
          </div>
          {{ t('nav.interviews') }}
        </button>
        <button
          v-if="role === 'admin'"
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.TEAM_MANAGEMENT })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
            <i class="pi pi-user-plus text-sm text-violet-600"></i>
          </div>
          {{ t('settings.team.invite') }}
        </button>
      </div>
    </div>

    <!-- Upcoming Interviews -->
    <div class="lg:col-span-2 rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 p-6">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('dashboard.upcomingInterviews') }}
        </h2>
        <Button
          :label="t('common.viewAll')"
          text
          size="small"
          severity="secondary"
          @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
        />
      </div>

      <div v-if="upcomingInterviews.length > 0" class="space-y-3">
        <div
          v-for="iv in upcomingInterviews"
          :key="iv.id"
          class="flex cursor-pointer items-center justify-between rounded-lg border border-gray-50 dark:border-gray-900 px-4 py-3 transition-colors hover:bg-gray-50"
          @click="goToInterview(iv)"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-950 text-xs font-semibold text-blue-700"
            >
              {{ iv.candidateName?.charAt(0) ?? '?' }}
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ iv.candidateName }}</p>
              <p class="text-xs text-gray-500">{{ iv.vacancyTitle }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm font-medium text-gray-700">{{ formatDateTime(iv.createdAt) }}</p>
            <p class="text-xs text-gray-400">
              {{ iv.durationMinutes }} {{ t('dashboard.stats.min') }}
            </p>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center py-8 text-center">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
          <i class="pi pi-calendar text-xl text-gray-400"></i>
        </div>
        <p class="mt-3 text-sm text-gray-500">{{ t('dashboard.noUpcomingInterviews') }}</p>
        <p class="text-xs text-gray-400">{{ t('dashboard.scheduledInterviewsHint') }}</p>
      </div>
    </div>
  </div>
</template>
