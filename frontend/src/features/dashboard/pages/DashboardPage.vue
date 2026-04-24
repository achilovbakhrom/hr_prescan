<script setup lang="ts">
/**
 * DashboardPage — main landing after login.
 * Per spec §9: glass greeting header + role-specific dashboard
 * (HrDashboard = 2-col glass, CandidateDashboard = 1-col).
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { useVacancyStore } from '@/features/vacancies/stores/vacancy.store'
import { useInterviewStore } from '@/features/interviews/stores/interview.store'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { useDashboardStore } from '@/features/dashboard/stores/dashboard.store'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useAIAssistant } from '@/shared/composables/useAIAssistant'
import TrialBanner from '@/features/dashboard/components/TrialBanner.vue'
import HrDashboard from '@/features/dashboard/components/HrDashboard.vue'
import CandidateDashboard from '@/features/dashboard/components/CandidateDashboard.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const vacancyStore = useVacancyStore()
const interviewStore = useInterviewStore()
const candidateStore = useCandidateStore()
const dashboardStore = useDashboardStore()
const aiAssistant = useAIAssistant()

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
const totalApplications = computed(
  () => dashboardStore.candidateStats?.totalApplications ?? candidateStore.myApplications.length,
)
const profileCompleteness = computed(() => dashboardStore.candidateStats?.profileCompleteness ?? 0)

const heroStats = computed(() =>
  role.value === 'candidate'
    ? [
        { label: t('dashboard.candidate.total'), value: totalApplications.value },
        {
          label: t('dashboard.candidate.inProgress'),
          value: dashboardStore.candidateStats?.prescanned ?? 0,
        },
        {
          label: t('dashboard.candidate.profileCompleteness'),
          value: `${profileCompleteness.value}%`,
        },
      ]
    : [
        { label: t('dashboard.activeVacancies'), value: vacancyStore.vacancies.length },
        {
          label: t('dashboard.pendingInterviews'),
          value: interviewStore.interviews.filter((item) => item.status === 'pending').length,
        },
        {
          label: t('dashboard.completedInterviews'),
          value: interviewStore.interviews.filter((item) => item.status === 'completed').length,
        },
      ],
)

const heroActions = computed(() =>
  role.value === 'candidate'
    ? [
        { label: t('nav.browseJobs'), icon: 'pi pi-search', route: ROUTE_NAMES.JOB_BOARD },
        {
          label: t('dashboard.candidate.editCv'),
          icon: 'pi pi-file-edit',
          route: ROUTE_NAMES.CV_BUILDER,
        },
      ]
    : [
        {
          label: t('dashboard.createVacancy'),
          icon: 'pi pi-plus',
          route: ROUTE_NAMES.VACANCY_CREATE,
        },
        {
          label: t('dashboard.viewCandidates'),
          icon: 'pi pi-users',
          route: ROUTE_NAMES.CANDIDATE_LIST,
        },
      ],
)

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
    <GlassCard class="mb-6 overflow-hidden sm:mb-8">
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_290px]">
        <div>
          <div
            class="mb-4 inline-flex items-center gap-2 rounded-full border border-[color:var(--color-border-glass)] bg-[color:var(--color-surface-raised)] px-3 py-1 text-[11px] font-mono uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
          >
            <span class="h-2 w-2 rounded-full bg-[color:var(--color-success)]"></span>
            {{ today }}
          </div>
          <h1
            class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
          >
            {{ greeting }}, {{ authStore.user?.firstName ?? 'User' }}
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
        </div>

        <div
          class="rounded-[24px] border border-[color:var(--color-border-glass)] bg-[linear-gradient(180deg,color-mix(in_srgb,var(--color-accent-ai)_14%,white),transparent)] p-5 dark:border-violet-300/20 dark:bg-[linear-gradient(180deg,rgba(124,58,237,0.18),rgba(30,41,59,0.42))]"
        >
          <p class="text-xs uppercase tracking-[0.16em] text-[color:var(--color-accent-ai)]">
            {{ t('aiAssistant.title') }}
          </p>
          <h2 class="mt-3 text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('dashboard.ai.title') }}
          </h2>
          <p class="mt-2 text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
            {{ t('dashboard.ai.subtitle') }}
          </p>
          <button
            type="button"
            class="mt-5 flex w-full cursor-pointer items-center justify-between rounded-[18px] border border-[color:var(--color-border-glass)] bg-white/70 px-4 py-3 text-left text-sm text-[color:var(--color-text-muted)] transition-colors hover:border-[color:var(--color-accent-ai)] hover:text-[color:var(--color-text-primary)] dark:border-violet-300/20 dark:bg-violet-300/10 dark:text-slate-200 dark:hover:border-violet-300/45 dark:hover:bg-violet-300/15"
            @click="aiAssistant.open()"
          >
            <span class="flex items-center gap-2">
              <i class="pi pi-sparkles text-[color:var(--color-accent-ai)]"></i>
              {{ t('dashboard.ai.placeholder') }}
            </span>
            <span class="font-mono text-[10px]">⌘K</span>
          </button>
        </div>
      </div>
    </GlassCard>

    <TrialBanner class="mb-6" />

    <div v-if="loadingStats" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <HrDashboard v-else-if="role === 'hr' || role === 'admin'" />
    <CandidateDashboard v-else-if="role === 'candidate'" />
  </div>
</template>
