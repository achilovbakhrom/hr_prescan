<script setup lang="ts">
/**
 * DashboardPage — main landing after login.
 * HR/admin: simple header + KPI/recent/funnel composition (see HrDashboard).
 * Candidate: greeting card + CandidateDashboard.
 */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { useDashboardStore } from '@/features/dashboard/stores/dashboard.store'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import TrialBanner from '@/features/dashboard/components/TrialBanner.vue'
import HrDashboard from '@/features/dashboard/components/HrDashboard.vue'
import CandidateDashboard from '@/features/dashboard/components/CandidateDashboard.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const candidateStore = useCandidateStore()
const dashboardStore = useDashboardStore()

const role = computed(() => authStore.currentAccessRole)
const isHr = computed(() => role.value === 'hr' || role.value === 'admin')
const firstName = computed(() => authStore.user?.firstName ?? 'User')
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return t('dashboard.greeting.morning')
  if (hour < 18) return t('dashboard.greeting.afternoon')
  return t('dashboard.greeting.evening')
})

const totalApplications = computed(
  () => dashboardStore.candidateStats?.totalApplications ?? candidateStore.myApplications.length,
)
const profileCompleteness = computed(() => dashboardStore.candidateStats?.profileCompleteness ?? 0)

const heroStats = computed(() => [
  { label: t('dashboard.candidate.total'), value: totalApplications.value },
  {
    label: t('dashboard.candidate.inProgress'),
    value: dashboardStore.candidateStats?.prescanned ?? 0,
  },
  { label: t('dashboard.candidate.profileCompleteness'), value: `${profileCompleteness.value}%` },
])
const heroActions = computed(() => [
  { label: t('nav.browseJobs'), icon: 'pi pi-search', route: ROUTE_NAMES.JOB_BOARD },
  {
    label: t('dashboard.candidate.editCv'),
    icon: 'pi pi-file-edit',
    route: ROUTE_NAMES.CV_BUILDER,
  },
])

onMounted(async () => {
  if (role.value === 'candidate') {
    try {
      await Promise.all([
        candidateStore.fetchMyApplications(),
        dashboardStore.fetchCandidateStats(),
      ])
    } catch {
      /* silent */
    }
  }
})
</script>

<template>
  <div class="w-full">
    <!-- HR / admin -->
    <template v-if="isHr">
      <header class="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1
            class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
          >
            {{ greeting }}, {{ firstName }} 👋
          </h1>
          <p class="mt-2 text-sm text-[color:var(--color-text-secondary)] sm:text-base">
            {{ t('dashboard.subtitle') }}
          </p>
        </div>
        <button
          type="button"
          class="inline-flex shrink-0 items-center gap-2 rounded-full bg-[linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)] px-5 py-2.5 text-sm font-semibold text-white shadow-[0_8px_24px_rgba(124,58,237,0.35)] transition-transform hover:-translate-y-0.5"
          @click="router.push({ name: ROUTE_NAMES.VACANCY_CREATE })"
        >
          <i class="pi pi-plus text-xs"></i>
          {{ t('dashboard.createVacancy') }}
        </button>
      </header>
      <TrialBanner class="mb-6" />
      <HrDashboard />
    </template>

    <!-- Candidate -->
    <template v-else>
      <GlassCard class="mb-6 overflow-hidden sm:mb-8">
        <h1
          class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
        >
          {{ greeting }}, {{ firstName }} 👋
        </h1>
        <p class="mt-3 max-w-2xl text-sm text-[color:var(--color-text-secondary)] sm:text-base">
          {{ t('dashboard.subtitle') }}
        </p>
        <div class="mt-5 flex flex-wrap gap-3">
          <Button
            v-for="action in heroActions"
            :key="action.route"
            :label="action.label"
            :icon="action.icon"
            severity="secondary"
            @click="router.push({ name: action.route })"
          />
        </div>
        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div
            v-for="stat in heroStats"
            :key="stat.label"
            class="rounded-[20px] border border-[color:var(--color-border-glass)] bg-[color:var(--color-surface-raised)] px-4 py-4"
          >
            <p class="text-xs uppercase tracking-[0.16em] text-[color:var(--color-text-muted)]">
              {{ stat.label }}
            </p>
            <p
              class="mt-2 font-mono text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]"
            >
              {{ stat.value }}
            </p>
          </div>
        </div>
      </GlassCard>
      <CandidateDashboard />
    </template>
  </div>
</template>
