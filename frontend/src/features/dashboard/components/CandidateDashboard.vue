<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { useDashboardStore } from '@/features/dashboard/stores/dashboard.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

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

function formatEmploymentType(type: string): string {
  const map: Record<string, string> = {
    full_time: t('vacancies.employment.fullTime'),
    part_time: t('vacancies.employment.partTime'),
    contract: t('vacancies.employment.contract'),
    internship: t('vacancies.employment.internship'),
  }
  return map[type] || type
}
</script>

<template>
  <!-- Profile Completeness -->
  <div class="mb-6 rounded-xl border border-gray-100 bg-white p-5">
    <div class="mb-2 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
          <i class="pi pi-user text-lg text-blue-600"></i>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-900">
            {{ t('dashboard.candidate.profileCompleteness') }}
          </h3>
          <p class="text-xs text-gray-500">{{ t('dashboard.candidate.completeProfileHint') }}</p>
        </div>
      </div>
      <span
        class="text-lg font-bold"
        :class="
          profileCompleteness >= 80
            ? 'text-emerald-600'
            : profileCompleteness >= 50
              ? 'text-amber-600'
              : 'text-red-500'
        "
      >
        {{ profileCompleteness }}%
      </span>
    </div>
    <ProgressBar
      :value="profileCompleteness"
      :showValue="false"
      style="height: 8px"
      :class="
        profileCompleteness >= 80
          ? '[&_.p-progressbar-value]:!bg-emerald-500'
          : profileCompleteness >= 50
            ? '[&_.p-progressbar-value]:!bg-amber-500'
            : '[&_.p-progressbar-value]:!bg-red-500'
      "
    />
  </div>

  <!-- Stats Cards -->
  <div class="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-5">
    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50">
          <i class="pi pi-file text-lg text-blue-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ totalApplications }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('dashboard.candidate.total') }}</p>
    </div>

    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50">
          <i class="pi pi-clock text-lg text-amber-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ appliedApplications }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('dashboard.candidate.applied') }}</p>
    </div>

    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50">
          <i class="pi pi-video text-lg text-violet-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ inProgressApplications }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">
        {{ t('dashboard.candidate.inProgress') }}
      </p>
    </div>

    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
          <i class="pi pi-star text-lg text-emerald-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ shortlistedApplications }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">
        {{ t('dashboard.candidate.shortlisted') }}
      </p>
    </div>

    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-50">
          <i class="pi pi-check-circle text-lg text-green-600"></i>
        </div>
        <span class="text-2xl font-bold text-gray-900">{{ hiredApplications }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('dashboard.candidate.hired') }}</p>
    </div>
  </div>

  <div class="grid gap-6 lg:grid-cols-3">
    <!-- Quick Actions -->
    <div class="rounded-xl border border-gray-100 bg-white p-6">
      <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-400">
        {{ t('dashboard.quickActions') }}
      </h2>
      <div class="space-y-2">
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
            <i class="pi pi-search text-sm text-blue-600"></i>
          </div>
          {{ t('nav.browseJobs') }}
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.MY_APPLICATIONS })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
            <i class="pi pi-list text-sm text-emerald-600"></i>
          </div>
          {{ t('nav.myApplications') }}
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
            <i class="pi pi-file-edit text-sm text-violet-600"></i>
          </div>
          {{ t('dashboard.candidate.editCv') }}
        </button>
        <button
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.PROFILE })"
        >
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50">
            <i class="pi pi-user text-sm text-amber-600"></i>
          </div>
          {{ t('nav.profile') }}
        </button>
      </div>
    </div>

    <!-- Recommended Jobs -->
    <div class="lg:col-span-2 rounded-xl border border-gray-100 bg-white p-6">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('dashboard.candidate.recommendedJobs') }}
        </h2>
        <Button
          :label="t('common.viewAll')"
          text
          size="small"
          severity="secondary"
          @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
        />
      </div>

      <div v-if="recommendedVacancies.length > 0" class="space-y-3">
        <div
          v-for="vacancy in recommendedVacancies"
          :key="vacancy.id"
          class="flex cursor-pointer items-center justify-between rounded-lg border border-gray-50 px-4 py-3 transition-colors hover:bg-gray-50"
          @click="router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id: vacancy.id } })"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700"
            >
              {{ vacancy.companyName?.charAt(0) ?? '?' }}
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ vacancy.title }}</p>
              <p class="text-xs text-gray-500">{{ vacancy.companyName }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm font-medium text-gray-700">
              {{ vacancy.isRemote ? t('vacancies.overview.remote') : vacancy.location }}
            </p>
            <p class="text-xs text-gray-400">{{ formatEmploymentType(vacancy.employmentType) }}</p>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center py-8 text-center">
        <div class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
          <i class="pi pi-briefcase text-xl text-gray-400"></i>
        </div>
        <p class="mt-3 text-sm text-gray-500">{{ t('dashboard.candidate.noRecommendations') }}</p>
        <p class="text-xs text-gray-400">{{ t('dashboard.candidate.noRecommendationsHint') }}</p>
      </div>
    </div>
  </div>
</template>
