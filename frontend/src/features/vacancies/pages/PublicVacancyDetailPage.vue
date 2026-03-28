<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { vacancyService } from '../services/vacancy.service'
import { EMPLOYMENT_LABELS, EXPERIENCE_LABELS, formatSalaryRange, formatDate } from '../composables/useVacancyLabels'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Vacancy } from '../types/vacancy.types'
import type { EmployerCompany } from '@/features/employers/types/employer.types'

interface VacancyWithEmployer extends Vacancy {
  employer?: EmployerCompany
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const vacancy = ref<VacancyWithEmployer | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const isShareRoute = computed(() => route.name === 'job-share')

onMounted(async () => {
  loading.value = true
  try {
    if (isShareRoute.value) {
      vacancy.value = await vacancyService.getByShareToken(route.params.token as string)
    } else {
      vacancy.value = await vacancyService.getPublicDetail(route.params.id as string)
    }
  } catch { error.value = 'Failed to load vacancy details' } finally { loading.value = false }
})
</script>

<template>
  <div>
    <div class="mx-auto max-w-3xl px-4 py-6 sm:py-8">
      <!-- Back button -->
      <button
        class="mb-4 flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-900"
        @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
      >
        <i class="pi pi-arrow-left text-xs"></i>
        {{ t('common.back') }}
      </button>

      <div v-if="loading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
      </div>
      <div v-else-if="error" class="py-12 text-center text-red-600">
        <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
        <p>{{ error }}</p>
      </div>
      <template v-else-if="vacancy">
        <div class="mb-5 sm:mb-6">
          <h1 class="text-2xl font-bold sm:text-3xl">{{ vacancy.title }}</h1>
          <p v-if="vacancy.employer?.name || (vacancy as any).companyName" class="mt-1 text-sm text-gray-500 sm:text-base">
            <i class="pi pi-building mr-1"></i>{{ vacancy.employer?.name || (vacancy as any).companyName }}
          </p>
          <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-gray-500 sm:gap-3 sm:text-sm">
            <span v-if="vacancy.location"><i class="pi pi-map-marker mr-1"></i>{{ vacancy.location }}</span>
            <Tag v-if="vacancy.isRemote" :value="t('vacancies.overview.remote')" severity="info" class="!text-[10px] sm:!text-xs" />
            <span><i class="pi pi-briefcase mr-1"></i>{{ EMPLOYMENT_LABELS[vacancy.employmentType] }}</span>
            <span><i class="pi pi-star mr-1"></i>{{ EXPERIENCE_LABELS[vacancy.experienceLevel] }}</span>
            <span class="hidden sm:inline"><i class="pi pi-calendar mr-1"></i>{{ t('jobBoard.postedOn') }} {{ formatDate(vacancy.createdAt) }}</span>
          </div>
          <p class="mt-1 text-xs text-gray-400 sm:hidden">
            <i class="pi pi-calendar mr-1"></i>{{ t('jobBoard.postedOn') }} {{ formatDate(vacancy.createdAt) }}
          </p>
        </div>

        <p v-if="formatSalaryRange(vacancy, t) !== t('vacancies.overview.salaryNotSpecified')" class="mb-5 text-lg font-semibold text-green-700 sm:mb-6 sm:text-xl">
          {{ formatSalaryRange(vacancy, t) }}
        </p>

        <div class="mb-6 sm:mb-8">
          <Button
            :label="t('jobBoard.apply')"
            icon="pi pi-send"
            size="large"
            class="w-full sm:w-auto"
            @click="router.push(`/jobs/${vacancy!.id}/apply`)"
          />
        </div>

        <div v-if="vacancy.skills.length > 0" class="mb-5 sm:mb-6">
          <h2 class="mb-2 text-base font-semibold sm:text-lg">{{ t('vacancies.overview.skills') }}</h2>
          <div class="flex flex-wrap gap-1.5 sm:gap-2">
            <Tag v-for="skill in vacancy.skills" :key="skill" :value="skill" severity="secondary" />
          </div>
        </div>

        <!-- Employer profile card -->
        <div v-if="vacancy.employer" class="mb-5 rounded-xl border border-gray-200 bg-gray-50 p-4 sm:mb-6 sm:p-5">
          <div class="flex items-center gap-3 sm:gap-4">
            <div
              v-if="vacancy.employer.logo"
              class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-white sm:h-14 sm:w-14"
            >
              <img :src="vacancy.employer.logo" :alt="vacancy.employer.name" class="h-full w-full object-contain" />
            </div>
            <div v-else class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600 sm:h-14 sm:w-14">
              <i class="pi pi-building text-lg sm:text-2xl"></i>
            </div>
            <div class="min-w-0">
              <h3 class="text-base font-semibold text-gray-900 sm:text-lg">{{ vacancy.employer.name }}</h3>
              <p v-if="vacancy.employer.industry" class="text-xs text-gray-500 sm:text-sm">{{ vacancy.employer.industry }}</p>
              <a
                v-if="vacancy.employer.website"
                :href="vacancy.employer.website"
                target="_blank"
                rel="noopener noreferrer"
                class="text-xs text-blue-600 hover:underline sm:text-sm"
              >
                {{ vacancy.employer.website }}
              </a>
            </div>
          </div>
          <p v-if="vacancy.employer.description" class="mt-3 whitespace-pre-line text-xs text-gray-600 sm:text-sm">
            {{ vacancy.employer.description }}
          </p>
        </div>

        <div class="mb-5 sm:mb-6">
          <h2 class="mb-2 text-base font-semibold sm:text-lg">{{ t('vacancies.form.description') }}</h2>
          <div class="prose prose-sm max-w-none text-gray-700" v-html="vacancy.description"></div>
        </div>
        <div v-if="vacancy.requirements" class="mb-5 sm:mb-6">
          <h2 class="mb-2 text-base font-semibold sm:text-lg">{{ t('vacancies.form.requirements') }}</h2>
          <p class="whitespace-pre-line text-sm text-gray-700">{{ vacancy.requirements }}</p>
        </div>
        <div v-if="vacancy.responsibilities" class="mb-5 sm:mb-6">
          <h2 class="mb-2 text-base font-semibold sm:text-lg">{{ t('vacancies.form.responsibilities') }}</h2>
          <p class="whitespace-pre-line text-sm text-gray-700">{{ vacancy.responsibilities }}</p>
        </div>
        <div v-if="vacancy.deadline" class="text-xs text-gray-500 sm:text-sm">
          <i class="pi pi-clock mr-1"></i>{{ t('vacancies.form.deadline') }}: {{ formatDate(vacancy.deadline) }}
        </div>
      </template>
    </div>
  </div>
</template>
