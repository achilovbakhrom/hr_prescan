<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { vacancyService } from '../services/vacancy.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { EMPLOYMENT_LABELS, formatSalaryRange, formatDate } from '../composables/useVacancyLabels'
import type { Vacancy } from '../types/vacancy.types'

const router = useRouter()
const jobs = ref<Vacancy[]>([])
const loading = ref(false)
const search = ref('')
const location = ref('')
const isRemote = ref(false)

onMounted(() => fetchJobs())

async function fetchJobs(): Promise<void> {
  loading.value = true
  try {
    jobs.value = await vacancyService.getPublicList({
      search: search.value || undefined,
      location: location.value || undefined,
      isRemote: isRemote.value || undefined,
    })
  } catch { /* silent */ } finally { loading.value = false }
}

function navigateToDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.JOB_DETAIL, params: { id } })
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-8">
    <h1 class="mb-2 text-3xl font-bold">Job Board</h1>
    <p class="mb-6 text-gray-600">Find your next opportunity</p>

    <div class="mb-6 flex flex-wrap items-end gap-4">
      <div class="flex-1">
        <label class="mb-1 block text-sm font-medium">Search</label>
        <InputText v-model="search" class="w-full" placeholder="Search jobs..." @keyup.enter="fetchJobs" />
      </div>
      <div class="w-48">
        <label class="mb-1 block text-sm font-medium">Location</label>
        <InputText v-model="location" class="w-full" placeholder="Any location" @keyup.enter="fetchJobs" />
      </div>
      <div class="flex items-center gap-2 pb-1">
        <ToggleSwitch v-model="isRemote" />
        <label class="text-sm font-medium">Remote only</label>
      </div>
      <Button label="Search" icon="pi pi-search" :loading="loading" @click="fetchJobs" />
    </div>

    <div v-if="loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div v-else-if="jobs.length > 0" class="space-y-4">
      <div
        v-for="job in jobs" :key="job.id"
        class="cursor-pointer rounded-lg border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md"
        @click="navigateToDetail(job.id)"
      >
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-lg font-semibold text-blue-700">{{ job.title }}</h2>
            <div class="mt-1 flex flex-wrap items-center gap-2 text-sm text-gray-500">
              <span v-if="job.location"><i class="pi pi-map-marker mr-1"></i>{{ job.location }}</span>
              <Tag v-if="job.isRemote" value="Remote" severity="info" />
              <span><i class="pi pi-briefcase mr-1"></i>{{ EMPLOYMENT_LABELS[job.employmentType] }}</span>
            </div>
          </div>
          <span class="text-sm text-gray-400">{{ formatDate(job.createdAt) }}</span>
        </div>
        <p v-if="formatSalaryRange(job) !== 'Not specified'" class="mt-2 font-medium text-green-700">
          {{ formatSalaryRange(job) }}
        </p>
        <p class="mt-2 line-clamp-2 text-sm text-gray-600">{{ job.description }}</p>
        <div v-if="job.skills.length > 0" class="mt-3 flex flex-wrap gap-1">
          <Tag v-for="skill in job.skills.slice(0, 5)" :key="skill" :value="skill" severity="secondary" />
          <Tag v-if="job.skills.length > 5" :value="`+${job.skills.length - 5}`" severity="secondary" />
        </div>
      </div>
    </div>

    <div v-else class="py-12 text-center text-gray-500">
      <i class="pi pi-briefcase mb-3 text-4xl"></i>
      <p class="text-lg font-medium">No jobs found</p>
      <p class="text-sm">Try adjusting your search criteria</p>
    </div>
  </div>
</template>
