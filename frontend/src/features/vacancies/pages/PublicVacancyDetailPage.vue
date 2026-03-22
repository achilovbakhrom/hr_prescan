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

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const vacancy = ref<Vacancy | null>(null)
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

    <div class="mx-auto max-w-3xl px-4 py-8">
    <div v-if="loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>
    <div v-else-if="error" class="py-12 text-center text-red-600">
      <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
      <p>{{ error }}</p>
    </div>
    <template v-else-if="vacancy">
      <div class="mb-6">
        <h1 class="text-3xl font-bold">{{ vacancy.title }}</h1>
        <div class="mt-2 flex flex-wrap items-center gap-3 text-gray-500">
          <span v-if="vacancy.location"><i class="pi pi-map-marker mr-1"></i>{{ vacancy.location }}</span>
          <Tag v-if="vacancy.isRemote" :value="t('vacancies.overview.remote')" severity="info" />
          <span><i class="pi pi-briefcase mr-1"></i>{{ EMPLOYMENT_LABELS[vacancy.employmentType] }}</span>
          <span><i class="pi pi-star mr-1"></i>{{ EXPERIENCE_LABELS[vacancy.experienceLevel] }}</span>
          <span><i class="pi pi-calendar mr-1"></i>{{ t('jobBoard.postedOn') }} {{ formatDate(vacancy.createdAt) }}</span>
        </div>
      </div>
      <p v-if="formatSalaryRange(vacancy) !== 'Not specified'" class="mb-6 text-xl font-semibold text-green-700">
        {{ formatSalaryRange(vacancy) }}
      </p>
      <div class="mb-8">
        <Button
          :label="t('jobBoard.apply')"
          icon="pi pi-send"
          size="large"
          class="w-full sm:w-auto"
          @click="router.push(`/jobs/${route.params.id || route.params.token}/apply`)"
        />
      </div>
      <div v-if="vacancy.skills.length > 0" class="mb-6">
        <h2 class="mb-2 text-lg font-semibold">{{ t('vacancies.overview.skills') }}</h2>
        <div class="flex flex-wrap gap-2">
          <Tag v-for="skill in vacancy.skills" :key="skill" :value="skill" severity="secondary" />
        </div>
      </div>
      <div class="mb-6">
        <h2 class="mb-2 text-lg font-semibold">{{ t('vacancies.form.description') }}</h2>
        <p class="whitespace-pre-line text-gray-700">{{ vacancy.description }}</p>
      </div>
      <div v-if="vacancy.requirements" class="mb-6">
        <h2 class="mb-2 text-lg font-semibold">{{ t('vacancies.form.requirements') }}</h2>
        <p class="whitespace-pre-line text-gray-700">{{ vacancy.requirements }}</p>
      </div>
      <div v-if="vacancy.responsibilities" class="mb-6">
        <h2 class="mb-2 text-lg font-semibold">{{ t('vacancies.form.responsibilities') }}</h2>
        <p class="whitespace-pre-line text-gray-700">{{ vacancy.responsibilities }}</p>
      </div>
      <div v-if="vacancy.deadline" class="text-sm text-gray-500">
        <i class="pi pi-clock mr-1"></i>{{ t('vacancies.form.deadline') }}: {{ formatDate(vacancy.deadline) }}
      </div>
    </template>
    </div>
  </div>
</template>
