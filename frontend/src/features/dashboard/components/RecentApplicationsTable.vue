<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { RecentApplication } from '../types/dashboard.types'

defineProps<{
  applications: RecentApplication[]
}>()

const { t } = useI18n()

const router = useRouter()

function viewDetail(app: RecentApplication): void {
  router.push({
    name: ROUTE_NAMES.CANDIDATE_DETAIL,
    params: { id: app.id },
  })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white">
    <div class="border-b border-gray-200 dark:border-gray-700 px-5 py-3">
      <h3 class="text-sm font-semibold text-gray-700">{{ t('dashboard.recentApplications') }}</h3>
    </div>
    <DataTable
      :value="applications"
      striped-rows
      row-hover
      class="cursor-pointer"
      @row-click="(e) => viewDetail(e.data)"
    >
      <Column field="candidateName" :header="t('dashboard.table.candidate')" />
      <Column field="vacancyTitle" :header="t('dashboard.table.vacancy')" />
      <Column :header="t('dashboard.table.score')">
        <template #body="{ data }">
          {{
            (data as RecentApplication).matchScore !== null
              ? `${(data as RecentApplication).matchScore}%`
              : t('interviews.status.pending')
          }}
        </template>
      </Column>
      <Column field="status" :header="t('common.status')" />
      <Column :header="t('dashboard.table.date')">
        <template #body="{ data }">
          {{ formatDate((data as RecentApplication).createdAt) }}
        </template>
      </Column>
      <template #empty>
        <div class="py-4 text-center text-sm text-gray-500">
          {{ t('dashboard.noRecentApplications') }}
        </div>
      </template>
    </DataTable>
  </div>
</template>
