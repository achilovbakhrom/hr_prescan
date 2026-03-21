<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import { useInterviewStore } from '@/features/interviews/stores/interview.store'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Interview } from '@/features/interviews/types/interview.types'

const router = useRouter()
const authStore = useAuthStore()
const vacancyStore = useVacancyStore()
const interviewStore = useInterviewStore()
const candidateStore = useCandidateStore()

const role = computed(() => authStore.user?.role)
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const loadingStats = ref(true)

onMounted(async () => {
  loadingStats.value = true
  try {
    if (role.value === 'hr' || role.value === 'admin') {
      await Promise.all([
        vacancyStore.fetchVacancies(),
        interviewStore.fetchInterviews(),
      ])
    } else if (role.value === 'candidate') {
      await candidateStore.fetchMyApplications()
    }
  } catch { /* silent */ } finally {
    loadingStats.value = false
  }
})

// HR computed stats
const activeVacancies = computed(() =>
  vacancyStore.vacancies.filter((v) => v.status === 'published').length,
)
const draftVacancies = computed(() =>
  vacancyStore.vacancies.filter((v) => v.status === 'draft').length,
)
const totalVacancies = computed(() => vacancyStore.vacancies.length)
const scheduledInterviews = computed(() =>
  interviewStore.interviews.filter((i) => i.status === 'pending').length,
)
const completedInterviews = computed(() =>
  interviewStore.interviews.filter((i) => i.status === 'completed').length,
)
const upcomingInterviews = computed(() =>
  interviewStore.interviews
    .filter((i) => i.status === 'pending')
    .sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
    .slice(0, 5),
)

// Candidate computed stats
const totalApplications = computed(() => candidateStore.myApplications.length)
const pendingApplications = computed(() =>
  candidateStore.myApplications.filter((a) => a.status === 'applied').length,
)
const interviewedApplications = computed(() =>
  candidateStore.myApplications.filter((a) =>
    ['interview_in_progress', 'interview_completed'].includes(a.status),
  ).length,
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
  <div>
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ greeting }}, {{ authStore.user?.firstName ?? 'User' }}
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        Here's what's happening today
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loadingStats" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
    </div>

    <!-- ==================== HR / ADMIN DASHBOARD ==================== -->
    <template v-else-if="role === 'hr' || role === 'admin'">
      <!-- Stats Cards -->
      <div class="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div
          class="cursor-pointer rounded-xl border border-gray-100 bg-white p-5 transition-all hover:shadow-md"
          @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
        >
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
              <i class="pi pi-briefcase text-lg text-blue-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ totalVacancies }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Total Vacancies</p>
          <p class="mt-0.5 text-xs text-blue-600">{{ activeVacancies }} active, {{ draftVacancies }} draft</p>
        </div>

        <div
          class="cursor-pointer rounded-xl border border-gray-100 bg-white p-5 transition-all hover:shadow-md"
          @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
        >
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
              <i class="pi pi-calendar text-lg text-amber-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ scheduledInterviews }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Scheduled Interviews</p>
          <p class="mt-0.5 text-xs text-amber-600">{{ completedInterviews }} completed</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
              <i class="pi pi-check-circle text-lg text-emerald-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ completedInterviews }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Completed</p>
          <p class="mt-0.5 text-xs text-emerald-600">AI interviews done</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50">
              <i class="pi pi-users text-lg text-violet-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ interviewStore.interviews.length }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Total Interviews</p>
          <p class="mt-0.5 text-xs text-violet-600">All time</p>
        </div>
      </div>

      <div class="grid gap-6 lg:grid-cols-3">
        <!-- Quick Actions -->
        <div class="rounded-xl border border-gray-100 bg-white p-6">
          <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-400">Quick Actions</h2>
          <div class="space-y-2">
            <button
              class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              @click="router.push({ name: ROUTE_NAMES.VACANCY_CREATE })"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                <i class="pi pi-plus text-sm text-blue-600"></i>
              </div>
              Create New Vacancy
            </button>
            <button
              class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
                <i class="pi pi-list text-sm text-emerald-600"></i>
              </div>
              View All Vacancies
            </button>
            <button
              class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50">
                <i class="pi pi-video text-sm text-amber-600"></i>
              </div>
              View Interviews
            </button>
            <button
              v-if="role === 'admin'"
              class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              @click="router.push({ name: ROUTE_NAMES.TEAM_MANAGEMENT })"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
                <i class="pi pi-user-plus text-sm text-violet-600"></i>
              </div>
              Invite Team Member
            </button>
          </div>
        </div>

        <!-- Upcoming Interviews -->
        <div class="lg:col-span-2 rounded-xl border border-gray-100 bg-white p-6">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-400">Upcoming Interviews</h2>
            <Button
              label="View all"
              text
              size="small"
              severity="secondary"
              @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
            />
          </div>

          <div v-if="upcomingInterviews.length > 0" class="space-y-3">
            <div
              v-for="interview in upcomingInterviews" :key="interview.id"
              class="flex cursor-pointer items-center justify-between rounded-lg border border-gray-50 px-4 py-3 transition-colors hover:bg-gray-50"
              @click="goToInterview(interview)"
            >
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                  {{ interview.candidateName?.charAt(0) ?? '?' }}
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ interview.candidateName }}</p>
                  <p class="text-xs text-gray-500">{{ interview.vacancyTitle }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-700">{{ formatDateTime(interview.createdAt) }}</p>
                <p class="text-xs text-gray-400">{{ interview.durationMinutes }} min</p>
              </div>
            </div>
          </div>

          <div v-else class="flex flex-col items-center py-8 text-center">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
              <i class="pi pi-calendar text-xl text-gray-400"></i>
            </div>
            <p class="mt-3 text-sm text-gray-500">No upcoming interviews</p>
            <p class="text-xs text-gray-400">Scheduled interviews will appear here</p>
          </div>
        </div>
      </div>
    </template>

    <!-- ==================== CANDIDATE DASHBOARD ==================== -->
    <template v-else-if="role === 'candidate'">
      <!-- Stats Cards -->
      <div class="mb-8 grid grid-cols-3 gap-4">
        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
              <i class="pi pi-file text-lg text-blue-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ totalApplications }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Applications</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
              <i class="pi pi-clock text-lg text-amber-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ pendingApplications }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Pending</p>
        </div>

        <div class="rounded-xl border border-gray-100 bg-white p-5">
          <div class="flex items-center justify-between">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
              <i class="pi pi-video text-lg text-emerald-600"></i>
            </div>
            <span class="text-2xl font-bold text-gray-900">{{ interviewedApplications }}</span>
          </div>
          <p class="mt-3 text-sm font-medium text-gray-500">Interviewed</p>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          class="group cursor-pointer rounded-xl border border-gray-100 bg-white p-6 transition-all hover:border-blue-200 hover:shadow-md"
          @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
        >
          <div class="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 transition-colors group-hover:bg-blue-100">
            <i class="pi pi-search text-lg text-blue-600"></i>
          </div>
          <h3 class="text-base font-semibold text-gray-900">Browse Jobs</h3>
          <p class="mt-1 text-sm text-gray-500">Find and apply to open positions</p>
        </div>

        <div
          class="group cursor-pointer rounded-xl border border-gray-100 bg-white p-6 transition-all hover:border-emerald-200 hover:shadow-md"
          @click="router.push({ name: ROUTE_NAMES.MY_APPLICATIONS })"
        >
          <div class="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 transition-colors group-hover:bg-emerald-100">
            <i class="pi pi-list text-lg text-emerald-600"></i>
          </div>
          <h3 class="text-base font-semibold text-gray-900">My Applications</h3>
          <p class="mt-1 text-sm text-gray-500">Track your application status</p>
        </div>

        <div
          class="group cursor-pointer rounded-xl border border-gray-100 bg-white p-6 transition-all hover:border-violet-200 hover:shadow-md"
          @click="router.push({ name: ROUTE_NAMES.PROFILE })"
        >
          <div class="mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-violet-50 transition-colors group-hover:bg-violet-100">
            <i class="pi pi-user text-lg text-violet-600"></i>
          </div>
          <h3 class="text-base font-semibold text-gray-900">My Profile</h3>
          <p class="mt-1 text-sm text-gray-500">View and edit your profile</p>
        </div>
      </div>
    </template>
  </div>
</template>
