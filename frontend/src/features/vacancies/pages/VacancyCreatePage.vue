<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyForm from '../components/VacancyForm.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CreateVacancyRequest } from '../types/vacancy.types'

const { t } = useI18n()
const router = useRouter()
const vacancyStore = useVacancyStore()

async function handleSave(data: CreateVacancyRequest): Promise<void> {
  try {
    const vacancy = await vacancyStore.createVacancy(data)
    router.push({
      name: ROUTE_NAMES.VACANCY_DETAIL,
      params: { id: vacancy.id },
    })
  } catch {
    // Error is handled by the store
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-gray-500 hover:text-gray-700"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-2xl font-bold">{{ t('vacancies.createTitle') }}</h1>
    </div>

    <p v-if="vacancyStore.error" class="text-sm text-red-600">
      {{ vacancyStore.error }}
    </p>

    <VacancyForm :loading="vacancyStore.loading" @save="handleSave" />
  </div>
</template>
