<script setup lang="ts">
/**
 * DashboardPage — main landing after login.
 * Per spec §9: glass greeting header + role-specific dashboard
 * (HrDashboard = 2-col glass, CandidateDashboard = 1-col).
 */
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import { useInterviewStore } from '@/features/interviews/stores/interview.store'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { useDashboardStore } from '@/features/dashboard/stores/dashboard.store'
import TrialBanner from '@/features/dashboard/components/TrialBanner.vue'
import HrDashboard from '@/features/dashboard/components/HrDashboard.vue'
import CandidateDashboard from '@/features/dashboard/components/CandidateDashboard.vue'

const authStore = useAuthStore()
const { t } = useI18n()
const vacancyStore = useVacancyStore()
const interviewStore = useInterviewStore()
const candidateStore = useCandidateStore()
const dashboardStore = useDashboardStore()

const role = computed(() => authStore.user?.role)
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return t('dashboard.greeting.morning')
  if (hour < 18) return t('dashboard.greeting.afternoon')
  return t('dashboard.greeting.evening')
})

const today = computed(() =>
  new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  }),
)

const loadingStats = ref(true)

onMounted(async () => {
  loadingStats.value = true
  try {
    if (role.value === 'hr' || role.value === 'admin') {
      await Promise.all([vacancyStore.fetchVacancies(), interviewStore.fetchInterviews()])
    } else if (role.value === 'candidate') {
      await Promise.all([
        candidateStore.fetchMyApplications(),
        dashboardStore.fetchCandidateStats(),
      ])
    }
  } catch {
    /* silent */
  } finally {
    loadingStats.value = false
  }
})
</script>

<template>
  <div class="mx-auto w-full max-w-7xl">
    <!-- Greeting header -->
    <header class="mb-6 flex flex-col gap-1 sm:mb-8">
      <p
        class="font-mono text-[11px] uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
      >
        {{ today }}
      </p>
      <h1
        class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
      >
        {{ greeting }}, {{ authStore.user?.firstName ?? 'User' }}
      </h1>
      <p class="text-sm text-[color:var(--color-text-secondary)] sm:text-base">
        {{ t('dashboard.subtitle') }}
      </p>
    </header>

    <TrialBanner class="mb-6" />

    <div v-if="loadingStats" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <HrDashboard v-else-if="role === 'hr' || role === 'admin'" />
    <CandidateDashboard v-else-if="role === 'candidate'" />
  </div>
</template>
