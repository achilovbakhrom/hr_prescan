<script setup lang="ts">
/**
 * CandidateDashboard — single-column glass layout for candidate role.
 * Profile completeness + stat grid + quick actions + recommended jobs.
 * All values preserved from previous implementation.
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ProgressBar from 'primevue/progressbar'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { useDashboardStore } from '@/features/dashboard/stores/dashboard.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import GlassCard from '@/shared/components/GlassCard.vue'
import DashboardStatsCard from './DashboardStatsCard.vue'
import RecommendedVacancies from './RecommendedVacancies.vue'

const router = useRouter()
const { t } = useI18n()
const candidateStore = useCandidateStore()
const dashboardStore = useDashboardStore()

const candidateDash = computed(() => dashboardStore.candidateStats)
const totalApplications = computed(
  () => candidateDash.value?.totalApplications ?? candidateStore.myApplications.length,
)
const appliedApplications = computed(
  () =>
    candidateDash.value?.applied ??
    candidateStore.myApplications.filter((a) => a.status === 'applied').length,
)
const inProgressApplications = computed(
  () =>
    (candidateDash.value?.prescanned ?? 0) + (candidateDash.value?.interviewed ?? 0) ||
    candidateStore.myApplications.filter((a) => ['prescanned', 'interviewed'].includes(a.status))
      .length,
)
const shortlistedApplications = computed(() => candidateDash.value?.shortlisted ?? 0)
const hiredApplications = computed(() => candidateDash.value?.hired ?? 0)
const profileCompleteness = computed(() => candidateDash.value?.profileCompleteness ?? 0)
const recommendedVacancies = computed(() => candidateDash.value?.recommendedVacancies ?? [])

const profileColor = computed(() => {
  if (profileCompleteness.value >= 80) return 'var(--color-success)'
  if (profileCompleteness.value >= 50) return 'var(--color-warning)'
  return 'var(--color-danger)'
})

const quickActions = [
  { route: ROUTE_NAMES.JOB_BOARD, icon: 'pi pi-search', key: 'nav.browseJobs' },
  { route: ROUTE_NAMES.MY_APPLICATIONS, icon: 'pi pi-list', key: 'nav.myApplications' },
  { route: ROUTE_NAMES.CV_BUILDER, icon: 'pi pi-file-edit', key: 'dashboard.candidate.editCv' },
  { route: ROUTE_NAMES.PROFILE, icon: 'pi pi-user', key: 'nav.profile' },
]
</script>

<template>
  <!-- Profile completeness -->
  <GlassCard class="mb-6">
    <div class="mb-2 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div
          class="flex h-10 w-10 items-center justify-center rounded-[--radius-sm] bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
        >
          <i class="pi pi-user text-lg"></i>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-[color:var(--color-text-primary)]">
            {{ t('dashboard.candidate.profileCompleteness') }}
          </h3>
          <p class="text-xs text-[color:var(--color-text-muted)]">
            {{ t('dashboard.candidate.completeProfileHint') }}
          </p>
        </div>
      </div>
      <span class="font-mono text-xl font-semibold" :style="{ color: profileColor }"
        >{{ profileCompleteness }}%</span
      >
    </div>
    <ProgressBar :value="profileCompleteness" :showValue="false" style="height: 8px" />
  </GlassCard>

  <!-- Stats grid -->
  <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
    <DashboardStatsCard
      icon="pi pi-file"
      icon-accent="default"
      :label="t('dashboard.candidate.total')"
      :value="totalApplications"
    />
    <DashboardStatsCard
      icon="pi pi-clock"
      icon-accent="warning"
      :label="t('dashboard.candidate.applied')"
      :value="appliedApplications"
    />
    <DashboardStatsCard
      icon="pi pi-video"
      icon-accent="ai"
      :label="t('dashboard.candidate.inProgress')"
      :value="inProgressApplications"
    />
    <DashboardStatsCard
      icon="pi pi-star"
      icon-accent="success"
      :label="t('dashboard.candidate.shortlisted')"
      :value="shortlistedApplications"
    />
    <DashboardStatsCard
      icon="pi pi-check-circle"
      icon-accent="celebrate"
      :label="t('dashboard.candidate.hired')"
      :value="hiredApplications"
    />
  </div>

  <div class="grid gap-6 lg:grid-cols-3">
    <!-- Quick Actions -->
    <GlassCard>
      <template #header>
        <h2
          class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('dashboard.quickActions') }}
        </h2>
      </template>
      <div class="flex flex-col gap-1">
        <button
          v-for="action in quickActions"
          :key="action.route"
          class="flex w-full items-center gap-3 rounded-[--radius-sm] px-3 py-2.5 text-left text-sm font-medium text-[color:var(--color-text-secondary)] transition-colors hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]"
          @click="router.push({ name: action.route })"
        >
          <i :class="action.icon" class="text-sm text-[color:var(--color-accent)]"></i>
          {{ t(action.key) }}
        </button>
      </div>
    </GlassCard>

    <RecommendedVacancies :vacancies="recommendedVacancies" />
  </div>
</template>
