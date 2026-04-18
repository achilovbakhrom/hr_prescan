<script setup lang="ts">
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
  <div>
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ greeting }}, {{ authStore.user?.firstName ?? 'User' }}
      </h1>
      <p class="mt-1 text-sm text-gray-500">{{ t('dashboard.subtitle') }}</p>
    </div>

    <!-- Trial Banner -->
    <TrialBanner class="mb-6" />

    <!-- Loading -->
    <div v-if="loadingStats" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
    </div>

    <!-- HR / Admin Dashboard -->
    <HrDashboard v-else-if="role === 'hr' || role === 'admin'" />

    <!-- Candidate Dashboard -->
    <CandidateDashboard v-else-if="role === 'candidate'" />
  </div>
</template>
