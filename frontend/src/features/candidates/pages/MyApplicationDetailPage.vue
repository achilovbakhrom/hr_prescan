<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useCandidateStore } from '../stores/candidate.store'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const applicationId = computed(() => route.params.id as string)
const application = computed(() => candidateStore.currentApplication)

onMounted(() => candidateStore.fetchMyApplicationDetail(applicationId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

const statusSteps = ['applied', 'prescanned', 'interviewed', 'shortlisted'] as const

function stepIndex(status: string): number {
  const idx = statusSteps.indexOf(status as (typeof statusSteps)[number])
  return idx === -1 ? -1 : idx
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button
        class="text-gray-500 dark:text-gray-400 hover:text-gray-700"
        @click="router.push({ name: ROUTE_NAMES.MY_APPLICATIONS })"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">{{ t('candidates.overview') }}</h1>
    </div>

    <div v-if="candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <template v-if="application">
      <!-- Status Timeline -->
      <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <h2 class="mb-3 text-sm font-semibold text-gray-600">
          {{ t('candidates.myApplication.progress') }}
        </h2>
        <div
          v-if="application.status !== 'rejected'"
          class="flex items-center gap-1 overflow-x-auto"
        >
          <div v-for="(step, idx) in statusSteps" :key="step" class="flex items-center">
            <div
              class="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold"
              :class="
                idx <= stepIndex(application.status)
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-500'
              "
            >
              {{ idx + 1 }}
            </div>
            <div
              v-if="idx < statusSteps.length - 1"
              class="mx-1 h-0.5 w-6"
              :class="idx < stepIndex(application.status) ? 'bg-blue-500' : 'bg-gray-200'"
            ></div>
          </div>
        </div>
        <div class="mt-2">
          <ApplicationStatusBadge :status="application.status" />
        </div>
      </div>

      <!-- Vacancy Info -->
      <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <h2 class="mb-2 text-sm font-semibold text-gray-600">{{ t('nav.vacancies') }}</h2>
        <p class="text-lg font-medium">{{ application.vacancyTitle }}</p>
        <p class="text-sm text-gray-500">
          {{ t('candidates.myApplication.appliedOn') }} {{ formatDate(application.createdAt) }}
        </p>
      </div>

      <!-- Match Score -->
      <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <h2 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.matchScore') }}</h2>
        <p v-if="application.matchScore !== null" class="text-3xl font-bold text-blue-600">
          {{ application.matchScore }}%
        </p>
        <p v-else class="text-gray-400">
          {{ t('candidates.myApplication.cvBeingAnalyzed') }}
        </p>
      </div>

      <!-- CV Download -->
      <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
        <h2 class="mb-2 text-sm font-semibold text-gray-600">
          {{ t('candidates.cv') }}
        </h2>
        <Button
          v-if="application.cvFile"
          :label="application.cvOriginalFilename || t('candidates.myApplication.downloadCv')"
          icon="pi pi-download"
          size="small"
          outlined
          :href="application.cvFile"
          as="a"
          target="_blank"
        />
        <p v-else class="text-sm text-gray-400">{{ t('candidates.myApplication.noCvUploaded') }}</p>
      </div>
    </template>
  </div>
</template>
