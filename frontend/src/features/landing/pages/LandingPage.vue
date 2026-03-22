<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { EMPLOYMENT_LABELS, formatSalaryRange, formatDate } from '@/features/vacancies/composables/useVacancyLabels'
import type { Vacancy } from '@/shared/types/vacancy.types'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const jobs = ref<Vacancy[]>([])
const jobsLoading = ref(false)

onMounted(async () => {
  jobsLoading.value = true
  try {
    jobs.value = await vacancyService.getPublicList({})
  } catch { /* silent */ } finally {
    jobsLoading.value = false
  }
})

function goToRegister(): void {
  router.push({ name: ROUTE_NAMES.REGISTER })
}
function goToLogin(): void {
  router.push({ name: ROUTE_NAMES.LOGIN })
}
function goToPricing(): void {
  router.push({ name: ROUTE_NAMES.PRICING })
}
function goToJobs(): void {
  router.push({ name: ROUTE_NAMES.JOB_BOARD })
}
function goToJobDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id } })
}

interface Feature {
  icon: string
  title: string
  description: string
  color: string
}
interface Step {
  number: string
  title: string
  description: string
}

const features = computed<Feature[]>(() => [
  {
    icon: 'pi pi-microphone',
    title: t('landing.features.aiInterviews'),
    description: t('landing.features.aiInterviewsDesc'),
    color: 'blue',
  },
  {
    icon: 'pi pi-chart-bar',
    title: t('landing.features.smartScoring'),
    description: t('landing.features.analyticsDesc'),
    color: 'emerald',
  },
  {
    icon: 'pi pi-shield',
    title: t('landing.features.antiCheating'),
    description: t('landing.features.antiCheatingDesc'),
    color: 'amber',
  },
  {
    icon: 'pi pi-briefcase',
    title: t('landing.features.easyManagement'),
    description: t('landing.features.easyManagementDesc'),
    color: 'violet',
  },
])

const steps = computed<Step[]>(() => [
  { number: '01', title: t('landing.howItWorks.step1'), description: t('landing.howItWorks.step1Desc') },
  { number: '02', title: t('landing.howItWorks.step2'), description: t('landing.howItWorks.step2Desc') },
  { number: '03', title: t('landing.howItWorks.step4'), description: t('landing.howItWorks.step4Desc') },
])
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <nav class="sticky top-0 z-50 border-b border-gray-100 bg-white/95 backdrop-blur-md">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <RouterLink to="/" class="flex items-center gap-2.5">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-sm">
            <i class="pi pi-bolt text-sm text-white"></i>
          </div>
          <span class="text-xl font-bold tracking-tight text-gray-900">HR PreScan</span>
        </RouterLink>
        <div class="hidden items-center gap-8 md:flex">
          <a href="#features" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">{{ t('landing.footer.features') }}</a>
          <a href="#how-it-works" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">{{ t('landing.howItWorks.title') }}</a>
          <a href="#jobs" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">{{ t('landing.latestJobs') }}</a>
          <a href="#pricing" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">{{ t('landing.footer.pricing') }}</a>
        </div>
        <div class="flex items-center gap-3">
          <template v-if="authStore.isAuthenticated">
            <Button :label="t('nav.dashboard')" icon="pi pi-th-large" text severity="secondary" size="small" @click="router.push({ name: ROUTE_NAMES.DASHBOARD })" />
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700">
              {{ authStore.user?.firstName?.charAt(0) }}{{ authStore.user?.lastName?.charAt(0) }}
            </div>
          </template>
          <template v-else>
            <Button :label="t('nav.signIn')" text severity="secondary" class="hidden sm:flex" @click="goToLogin" />
            <Button :label="t('landing.hero.getStarted')" size="small" @click="goToRegister" />
          </template>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative overflow-hidden px-6 py-20 sm:py-28">
      <div class="absolute inset-0 bg-gradient-to-br from-blue-50/80 via-white to-indigo-50/60"></div>
      <div class="absolute -top-24 right-0 h-96 w-96 rounded-full bg-blue-200/30 blur-3xl"></div>
      <div class="absolute -bottom-24 left-0 h-96 w-96 rounded-full bg-indigo-200/30 blur-3xl"></div>
      <div class="relative mx-auto max-w-4xl text-center">
        <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700">
          <i class="pi pi-bolt text-xs"></i> {{ t('landing.badge.poweredBy') }}
        </div>
        <h1 class="mb-6 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
          {{ t('landing.hero.title') }}
        </h1>
        <p class="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-gray-600">
          {{ t('landing.hero.subtitle') }}
        </p>
        <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button :label="t('landing.hero.cta')" icon="pi pi-arrow-right" icon-pos="right" size="large" @click="goToRegister" />
          <Button :label="t('landing.hero.browseJobs')" icon="pi pi-search" severity="secondary" outlined size="large" @click="goToJobs" />
        </div>
        <p class="mt-4 text-sm text-gray-400">{{ t('landing.promo.noCreditCard') }} &middot; {{ t('landing.promo.freeTrial') }}</p>
      </div>
    </section>

    <!-- Stats Bar -->
    <section class="border-y border-gray-100 bg-gray-50/50">
      <div class="mx-auto grid max-w-5xl grid-cols-3 divide-x divide-gray-200 py-10">
        <div class="text-center">
          <div class="text-3xl font-extrabold text-gray-900">10x</div>
          <div class="mt-1 text-sm text-gray-500">{{ t('landing.stats.fasterScreening') }}</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-extrabold text-gray-900">90%</div>
          <div class="mt-1 text-sm text-gray-500">{{ t('landing.stats.timeSaved') }}</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-extrabold text-gray-900">24/7</div>
          <div class="mt-1 text-sm text-gray-500">{{ t('landing.stats.available') }}</div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="px-6 py-20">
      <div class="mx-auto max-w-7xl">
        <div class="mb-14 text-center">
          <h2 class="mb-3 text-3xl font-bold text-gray-900">{{ t('landing.features.title') }}</h2>
          <p class="mx-auto max-w-xl text-gray-500">{{ t('landing.howItWorks.subtitle') }}</p>
        </div>
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="feature in features" :key="feature.title"
            class="group rounded-2xl border border-gray-100 p-7 transition-all duration-200 hover:border-gray-200 hover:shadow-lg"
          >
            <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
              <i :class="feature.icon" class="text-xl"></i>
            </div>
            <h3 class="mb-2 text-lg font-semibold text-gray-900">{{ feature.title }}</h3>
            <p class="text-sm leading-relaxed text-gray-500">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="bg-gray-50 px-6 py-20">
      <div class="mx-auto max-w-5xl">
        <div class="mb-14 text-center">
          <h2 class="mb-3 text-3xl font-bold text-gray-900">{{ t('landing.howItWorks.title') }}</h2>
          <p class="mx-auto max-w-xl text-gray-500">{{ t('landing.howItWorks.subtitle') }}</p>
        </div>
        <div class="grid gap-8 lg:grid-cols-3">
          <div v-for="step in steps" :key="step.number" class="relative rounded-2xl bg-white p-8 shadow-sm">
            <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
              {{ step.number }}
            </div>
            <h3 class="mb-2 text-lg font-semibold text-gray-900">{{ step.title }}</h3>
            <p class="text-sm leading-relaxed text-gray-500">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Open Positions Section -->
    <section id="jobs" class="px-6 py-20">
      <div class="mx-auto max-w-5xl">
        <div class="mb-10 flex items-end justify-between">
          <div>
            <h2 class="mb-2 text-3xl font-bold text-gray-900">{{ t('landing.latestJobs') }}</h2>
            <p class="text-gray-500">{{ t('landing.latestJobsSubtitle') }}</p>
          </div>
          <Button :label="t('landing.viewAllJobs')" icon="pi pi-arrow-right" icon-pos="right" text severity="secondary" @click="goToJobs" />
        </div>

        <div v-if="jobsLoading" class="py-12 text-center">
          <i class="pi pi-spinner pi-spin text-3xl text-gray-300"></i>
        </div>

        <div v-else-if="jobs.length > 0" class="space-y-3">
          <div
            v-for="job in jobs.slice(0, 6)" :key="job.id"
            class="flex cursor-pointer items-center justify-between rounded-xl border border-gray-100 bg-white p-5 transition-all hover:border-gray-200 hover:shadow-md"
            @click="goToJobDetail(job.id)"
          >
            <div class="min-w-0 flex-1">
              <h3 class="text-base font-semibold text-gray-900">{{ job.title }}</h3>
              <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
                <span v-if="job.location"><i class="pi pi-map-marker mr-1 text-xs"></i>{{ job.location }}</span>
                <span><i class="pi pi-briefcase mr-1 text-xs"></i>{{ EMPLOYMENT_LABELS[job.employmentType] }}</span>
                <Tag v-if="job.isRemote" :value="t('landing.remote')" severity="info" class="text-xs" />
              </div>
            </div>
            <div class="ml-4 flex flex-col items-end gap-1">
              <span v-if="formatSalaryRange(job, t) !== t('vacancies.overview.salaryNotSpecified')" class="text-sm font-semibold text-emerald-600">
                {{ formatSalaryRange(job, t) }}
              </span>
              <span class="text-xs text-gray-400">{{ formatDate(job.createdAt) }}</span>
            </div>
          </div>
        </div>

        <div v-else class="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
          <i class="pi pi-briefcase mb-3 text-4xl text-gray-300"></i>
          <p class="text-gray-500">{{ t('landing.noJobsYet') }}</p>
          <p class="mt-1 text-sm text-gray-400">{{ t('landing.noJobsCheckBack') }}</p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section id="pricing" class="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-20">
      <div class="mx-auto max-w-3xl text-center">
        <h2 class="mb-4 text-3xl font-bold text-white">{{ t('landing.cta.title') }}</h2>
        <p class="mx-auto mb-8 max-w-lg text-lg text-blue-100">
          {{ t('landing.cta.subtitle') }}
        </p>
        <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button :label="t('landing.cta.startFree')" icon="pi pi-arrow-right" icon-pos="right" size="large" severity="contrast" @click="goToRegister" />
          <Button :label="t('landing.cta.viewPricing')" text size="large" class="text-white hover:text-blue-100" @click="goToPricing" />
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-800 bg-gray-900 px-6 py-12">
      <div class="mx-auto max-w-7xl">
        <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <div class="mb-3 flex items-center gap-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
                <i class="pi pi-bolt text-sm text-white"></i>
              </div>
              <span class="text-lg font-bold text-white">HR PreScan</span>
            </div>
            <p class="text-sm text-gray-400">{{ t('landing.footer.tagline') }}</p>
          </div>
          <div>
            <h4 class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('landing.footer.product') }}</h4>
            <ul class="space-y-2">
              <li><a href="#features" class="text-sm text-gray-400 hover:text-white">{{ t('landing.footer.features') }}</a></li>
              <li><a href="#how-it-works" class="text-sm text-gray-400 hover:text-white">{{ t('landing.howItWorks.title') }}</a></li>
              <li><RouterLink to="/pricing" class="text-sm text-gray-400 hover:text-white">{{ t('landing.footer.pricing') }}</RouterLink></li>
            </ul>
          </div>
          <div>
            <h4 class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('landing.footer.company') }}</h4>
            <ul class="space-y-2">
              <li><RouterLink to="/privacy" class="text-sm text-gray-400 hover:text-white">{{ t('landing.footer.privacy') }}</RouterLink></li>
              <li><RouterLink to="/terms" class="text-sm text-gray-400 hover:text-white">{{ t('landing.footer.terms') }}</RouterLink></li>
            </ul>
          </div>
          <div>
            <h4 class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">{{ t('landing.hero.getStarted') }}</h4>
            <ul class="space-y-2">
              <li><RouterLink to="/login" class="text-sm text-gray-400 hover:text-white">{{ t('nav.signIn') }}</RouterLink></li>
              <li><RouterLink to="/register" class="text-sm text-gray-400 hover:text-white">{{ t('auth.register.title') }}</RouterLink></li>
              <li><RouterLink to="/jobs" class="text-sm text-gray-400 hover:text-white">{{ t('nav.browseJobs') }}</RouterLink></li>
            </ul>
          </div>
        </div>
        <div class="mt-10 border-t border-gray-800 pt-6 text-center text-sm text-gray-500">
          &copy; {{ new Date().getFullYear() }} HR PreScan. {{ t('landing.footer.copyright') }}
        </div>
      </div>
    </footer>
  </div>
</template>
