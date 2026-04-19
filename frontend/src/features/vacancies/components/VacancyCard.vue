<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import VacancyStatusBadge from './VacancyStatusBadge.vue'
import CompanyLogo from '@/shared/components/CompanyLogo.vue'
import type { Vacancy, VacancyStatus } from '../types/vacancy.types'

defineProps<{
  vacancy: Vacancy
}>()

const emit = defineEmits<{
  click: [id: string]
  delete: [event: Event, id: string, title: string]
  statusChange: [event: Event, id: string, status: VacancyStatus]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function onStatusClick(event: Event, id: string, status: VacancyStatus): void {
  event.stopPropagation()
  emit('statusChange', event, id, status)
}
</script>

<template>
  <div
    class="cursor-pointer rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 px-4 py-3 transition-all hover:border-gray-200 dark:hover:border-gray-700 hover:shadow-sm md:px-5 md:py-4"
    @click="emit('click', vacancy.id)"
  >
    <div class="flex items-start justify-between gap-3">
      <CompanyLogo
        v-if="vacancy.companyName"
        :logo="vacancy.companyLogo"
        :name="vacancy.companyName"
        size="sm"
        rounded="md"
      />
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <h3 class="text-sm font-semibold text-gray-900">{{ vacancy.title }}</h3>
          <VacancyStatusBadge :status="vacancy.status" />
        </div>
        <p v-if="vacancy.companyName" class="mt-0.5 text-xs text-gray-500">
          {{ vacancy.companyName }}
        </p>
        <div class="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
          <span v-if="vacancy.location"
            ><i class="pi pi-map-marker mr-1"></i>{{ vacancy.location }}</span
          >
          <span v-if="vacancy.isRemote" class="text-blue-600">{{
            t('vacancies.overview.remote')
          }}</span>
          <span><i class="pi pi-calendar mr-1"></i>{{ formatDate(vacancy.createdAt) }}</span>
        </div>
      </div>
      <div class="flex items-center gap-2" @click.stop>
        <Button
          v-if="vacancy.status === 'draft'"
          :label="t('vacancies.actions.publish')"
          icon="pi pi-send"
          size="small"
          @click="onStatusClick($event, vacancy.id, 'published')"
        />
        <Button
          v-if="vacancy.status === 'paused'"
          :label="t('vacancies.actions.resume')"
          icon="pi pi-play"
          severity="success"
          size="small"
          @click="onStatusClick($event, vacancy.id, 'published')"
        />
        <Button
          v-if="vacancy.status === 'published'"
          :label="t('vacancies.actions.pause')"
          icon="pi pi-pause"
          severity="warn"
          size="small"
          outlined
          @click="onStatusClick($event, vacancy.id, 'paused')"
        />
        <Button
          v-if="vacancy.status === 'draft' || vacancy.status === 'archived'"
          icon="pi pi-trash"
          severity="danger"
          text
          rounded
          size="small"
          @click="emit('delete', $event, vacancy.id, vacancy.title)"
        />
        <i
          class="pi pi-chevron-right mt-1 hidden text-sm text-gray-300 dark:text-gray-600 sm:block"
        ></i>
      </div>
    </div>

    <div class="mt-3 flex flex-wrap gap-2">
      <div
        class="flex items-center gap-1.5 rounded-lg bg-blue-50 dark:bg-blue-950 px-2 py-1 sm:px-2.5 sm:py-1.5"
      >
        <i class="pi pi-users text-xs text-blue-500"></i>
        <span class="text-xs font-semibold text-blue-700 dark:text-blue-300 sm:text-sm">{{
          vacancy.candidatesTotal ?? 0
        }}</span>
        <span class="text-[10px] text-blue-400 sm:text-xs">{{ t('vacancies.applied') }}</span>
      </div>
      <div
        class="flex items-center gap-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950 px-2 py-1 sm:px-2.5 sm:py-1.5"
      >
        <i class="pi pi-check text-xs text-emerald-500"></i>
        <span class="text-xs font-semibold text-emerald-700 sm:text-sm">{{
          vacancy.candidatesInterviewed ?? 0
        }}</span>
        <span class="text-[10px] text-emerald-400 sm:text-xs">{{
          t('vacancies.interviewed')
        }}</span>
      </div>
      <div class="flex items-center gap-1.5 rounded-lg bg-violet-50 px-2 py-1 sm:px-2.5 sm:py-1.5">
        <i class="pi pi-star text-xs text-violet-500"></i>
        <span class="text-xs font-semibold text-violet-700 sm:text-sm">{{
          vacancy.candidatesShortlisted ?? 0
        }}</span>
        <span class="text-[10px] text-violet-400 sm:text-xs">{{ t('vacancies.shortlisted') }}</span>
      </div>
      <div
        v-if="vacancy.status === 'archived' && (vacancy.candidatesHired ?? 0) > 0"
        class="flex items-center gap-1.5 rounded-lg bg-amber-50 px-2 py-1 sm:px-2.5 sm:py-1.5"
      >
        <i class="pi pi-verified text-xs text-amber-500"></i>
        <span class="text-xs font-semibold text-amber-700 sm:text-sm">{{
          vacancy.candidatesHired
        }}</span>
        <span class="text-[10px] text-amber-400 sm:text-xs">{{ t('vacancies.hired') }}</span>
      </div>
    </div>
  </div>
</template>
