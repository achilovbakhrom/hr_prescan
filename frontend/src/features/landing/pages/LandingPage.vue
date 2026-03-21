<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { EMPLOYMENT_LABELS, formatSalaryRange, formatDate } from '@/features/vacancies/composables/useVacancyLabels'
import type { Vacancy } from '@/features/vacancies/types/vacancy.types'

const router = useRouter()
const authStore = useAuthStore()
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

const features: Feature[] = [
  {
    icon: 'pi pi-microphone',
    title: 'AI-Powered Interviews',
    description: 'Automated video interviews conducted by an AI voice agent, available 24/7 for candidates worldwide.',
    color: 'blue',
  },
  {
    icon: 'pi pi-chart-bar',
    title: 'Smart Scoring',
    description: 'Objective candidate evaluation with AI-generated scores, transcripts, and detailed performance insights.',
    color: 'emerald',
  },
  {
    icon: 'pi pi-shield',
    title: 'Anti-Cheating Protection',
    description: 'Real-time proctoring with face detection and environment monitoring ensures interview integrity.',
    color: 'amber',
  },
  {
    icon: 'pi pi-briefcase',
    title: 'Easy Management',
    description: 'Manage vacancies, track candidates, schedule interviews, and collaborate with your team in one platform.',
    color: 'violet',
  },
]

const steps: Step[] = [
  { number: '01', title: 'Post a Vacancy', description: 'Create a job listing with custom criteria. Share the link anywhere — LinkedIn, job boards, email.' },
  { number: '02', title: 'Candidates Apply & Interview', description: 'Candidates submit applications, upload CVs, and take AI video interviews at their convenience.' },
  { number: '03', title: 'Review AI Results', description: 'Receive scored transcripts, video recordings, and AI insights to make faster, data-driven hiring decisions.' },
]
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
          <a href="#features" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">Features</a>
          <a href="#how-it-works" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">How It Works</a>
          <a href="#jobs" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">Open Positions</a>
          <a href="#pricing" class="text-sm font-medium text-gray-500 transition-colors hover:text-gray-900">Pricing</a>
        </div>
        <div class="flex items-center gap-3">
          <template v-if="authStore.isAuthenticated">
            <Button label="Dashboard" icon="pi pi-th-large" text severity="secondary" size="small" @click="router.push({ name: ROUTE_NAMES.DASHBOARD })" />
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700">
              {{ authStore.user?.firstName?.charAt(0) }}{{ authStore.user?.lastName?.charAt(0) }}
            </div>
          </template>
          <template v-else>
            <Button label="Sign In" text severity="secondary" class="hidden sm:flex" @click="goToLogin" />
            <Button label="Get Started" size="small" @click="goToRegister" />
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
          <i class="pi pi-bolt text-xs"></i> Powered by Advanced AI
        </div>
        <h1 class="mb-6 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
          Hire Smarter with<br>
          <span class="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">AI Pre-Screening</span>
        </h1>
        <p class="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-gray-600">
          Screen hundreds of candidates automatically with AI video interviews.
          Save time, reduce bias, and hire the best talent faster.
        </p>
        <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button label="Start Free Trial" icon="pi pi-arrow-right" icon-pos="right" size="large" @click="goToRegister" />
          <Button label="Browse Open Positions" icon="pi pi-search" severity="secondary" outlined size="large" @click="goToJobs" />
        </div>
        <p class="mt-4 text-sm text-gray-400">No credit card required &middot; 14-day free trial</p>
      </div>
    </section>

    <!-- Stats Bar -->
    <section class="border-y border-gray-100 bg-gray-50/50">
      <div class="mx-auto grid max-w-5xl grid-cols-3 divide-x divide-gray-200 py-10">
        <div class="text-center">
          <div class="text-3xl font-extrabold text-gray-900">10x</div>
          <div class="mt-1 text-sm text-gray-500">Faster Screening</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-extrabold text-gray-900">90%</div>
          <div class="mt-1 text-sm text-gray-500">Time Saved</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-extrabold text-gray-900">24/7</div>
          <div class="mt-1 text-sm text-gray-500">Available</div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="px-6 py-20">
      <div class="mx-auto max-w-7xl">
        <div class="mb-14 text-center">
          <h2 class="mb-3 text-3xl font-bold text-gray-900">Everything you need to hire smarter</h2>
          <p class="mx-auto max-w-xl text-gray-500">Our AI platform handles the entire pre-screening process so your HR team can focus on finding the right people.</p>
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
          <h2 class="mb-3 text-3xl font-bold text-gray-900">How It Works</h2>
          <p class="mx-auto max-w-xl text-gray-500">Get up and running in minutes. Our streamlined process makes AI-powered hiring effortless.</p>
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
            <h2 class="mb-2 text-3xl font-bold text-gray-900">Open Positions</h2>
            <p class="text-gray-500">Browse the latest job openings from companies using HR PreScan</p>
          </div>
          <Button label="View All Jobs" icon="pi pi-arrow-right" icon-pos="right" text severity="secondary" @click="goToJobs" />
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
                <Tag v-if="job.isRemote" value="Remote" severity="info" class="text-xs" />
              </div>
            </div>
            <div class="ml-4 flex flex-col items-end gap-1">
              <span v-if="formatSalaryRange(job) !== 'Not specified'" class="text-sm font-semibold text-emerald-600">
                {{ formatSalaryRange(job) }}
              </span>
              <span class="text-xs text-gray-400">{{ formatDate(job.createdAt) }}</span>
            </div>
          </div>
        </div>

        <div v-else class="rounded-2xl border border-dashed border-gray-200 py-16 text-center">
          <i class="pi pi-briefcase mb-3 text-4xl text-gray-300"></i>
          <p class="text-gray-500">No open positions at the moment</p>
          <p class="mt-1 text-sm text-gray-400">Check back soon for new opportunities</p>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section id="pricing" class="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-20">
      <div class="mx-auto max-w-3xl text-center">
        <h2 class="mb-4 text-3xl font-bold text-white">Ready to transform your hiring?</h2>
        <p class="mx-auto mb-8 max-w-lg text-lg text-blue-100">
          Join companies already using HR PreScan to find top talent faster.
        </p>
        <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button label="Start Free Trial" icon="pi pi-arrow-right" icon-pos="right" size="large" severity="contrast" @click="goToRegister" />
          <Button label="View Pricing" text size="large" class="text-white hover:text-blue-100" @click="goToPricing" />
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
            <p class="text-sm text-gray-400">AI-powered candidate pre-screening for modern teams.</p>
          </div>
          <div>
            <h4 class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Product</h4>
            <ul class="space-y-2">
              <li><a href="#features" class="text-sm text-gray-400 hover:text-white">Features</a></li>
              <li><a href="#how-it-works" class="text-sm text-gray-400 hover:text-white">How It Works</a></li>
              <li><RouterLink to="/pricing" class="text-sm text-gray-400 hover:text-white">Pricing</RouterLink></li>
            </ul>
          </div>
          <div>
            <h4 class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Company</h4>
            <ul class="space-y-2">
              <li><RouterLink to="/privacy" class="text-sm text-gray-400 hover:text-white">Privacy Policy</RouterLink></li>
              <li><RouterLink to="/terms" class="text-sm text-gray-400 hover:text-white">Terms of Service</RouterLink></li>
            </ul>
          </div>
          <div>
            <h4 class="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">Get Started</h4>
            <ul class="space-y-2">
              <li><RouterLink to="/login" class="text-sm text-gray-400 hover:text-white">Sign In</RouterLink></li>
              <li><RouterLink to="/register" class="text-sm text-gray-400 hover:text-white">Create Account</RouterLink></li>
              <li><RouterLink to="/jobs" class="text-sm text-gray-400 hover:text-white">Browse Jobs</RouterLink></li>
            </ul>
          </div>
        </div>
        <div class="mt-10 border-t border-gray-800 pt-6 text-center text-sm text-gray-500">
          &copy; {{ new Date().getFullYear() }} HR PreScan. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>
