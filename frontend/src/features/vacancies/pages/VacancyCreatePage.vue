<script setup lang="ts">
/**
 * VacancyCreatePage — vacancy creation form presented inside a GlassCard.
 */
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import GlassCard from '@/shared/components/GlassCard.vue'
import VacancyForm from '../components/VacancyForm.vue'
import { useVacancyStore } from '../stores/vacancy.store'
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
    /* errors shown via fieldErrors / error passed to VacancyForm */
  }
}
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-4">
    <div class="flex items-center gap-3">
      <button
        class="text-[color:var(--color-text-muted)] transition-colors hover:text-[color:var(--color-text-primary)]"
        @click="router.back()"
      >
        <i class="pi pi-arrow-left text-lg"></i>
      </button>
      <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
        {{ t('vacancies.createTitle') }}
      </h1>
    </div>

    <GlassCard>
      <VacancyForm
        :loading="vacancyStore.loading"
        :field-errors="vacancyStore.fieldErrors"
        :error-message="vacancyStore.error"
        @save="handleSave"
      />
    </GlassCard>
  </div>
</template>
