<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useCandidateStore } from '../stores/candidate.store'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Application } from '../types/candidate.types'

const { t } = useI18n()

const router = useRouter()
const candidateStore = useCandidateStore()

onMounted(() => candidateStore.fetchMyApplications())

function viewDetail(app: Application): void {
  router.push({ name: ROUTE_NAMES.MY_APPLICATION_DETAIL, params: { id: app.id } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-2xl font-bold">{{ t('nav.myApplications') }}</h1>

    <p v-if="candidateStore.error" class="text-sm text-red-600">
      {{ candidateStore.error }}
    </p>

    <DataTable
      :value="candidateStore.myApplications"
      :loading="candidateStore.loading"
      striped-rows
      row-hover
      class="cursor-pointer"
      @row-click="(e) => viewDetail(e.data)"
    >
      <Column field="vacancyTitle" :header="t('nav.vacancies')" sortable />
      <Column :header="t('vacancies.form.companyInfo')">
        <template #body="{ data }">
          <span v-if="(data as Application).companyName" class="text-sm text-gray-600">
            <i class="pi pi-building mr-1 text-xs"></i>{{ (data as Application).companyName }}
          </span>
          <span v-else class="text-sm text-gray-400">-</span>
        </template>
      </Column>
      <Column :header="t('common.status')">
        <template #body="{ data }">
          <ApplicationStatusBadge :status="(data as Application).status" />
        </template>
      </Column>
      <Column :header="t('candidates.matchScore')" sortable sort-field="matchScore">
        <template #body="{ data }">
          {{
            (data as Application).matchScore !== null
              ? `${(data as Application).matchScore}%`
              : t('interviews.status.pending')
          }}
        </template>
      </Column>
      <Column :header="t('common.createdAt')" sortable sort-field="createdAt">
        <template #body="{ data }">
          {{ formatDate((data as Application).createdAt) }}
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          <i class="pi pi-inbox mb-2 text-3xl"></i>
          <p>No applications yet</p>
          <RouterLink to="/jobs" class="mt-2 inline-block text-blue-600 dark:text-blue-400 hover:underline">
            Browse available jobs
          </RouterLink>
        </div>
      </template>
    </DataTable>
  </div>
</template>
