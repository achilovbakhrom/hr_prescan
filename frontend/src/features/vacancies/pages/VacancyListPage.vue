<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import { useVacancyStore } from '../stores/vacancy.store'
import VacancyStatusBadge from '../components/VacancyStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const vacancyStore = useVacancyStore()

const statusFilter = ref<string | null>(null)
const statusOptions = [
  { label: 'All', value: null },
  { label: 'Draft', value: 'draft' },
  { label: 'Published', value: 'published' },
  { label: 'Paused', value: 'paused' },
  { label: 'Closed', value: 'closed' },
]

onMounted(() => {
  vacancyStore.fetchVacancies()
})

function onStatusChange(): void {
  const params = statusFilter.value ? { status: statusFilter.value } : undefined
  vacancyStore.fetchVacancies(params)
}

function navigateToCreate(): void {
  router.push({ name: ROUTE_NAMES.VACANCY_CREATE })
}

function navigateToDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">Vacancies</h1>
      <Button
        label="Create Vacancy"
        icon="pi pi-plus"
        @click="navigateToCreate"
      />
    </div>

    <div class="flex items-center gap-4">
      <Dropdown
        v-model="statusFilter"
        :options="statusOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by status"
        class="w-48"
        @change="onStatusChange"
      />
    </div>

    <DataTable
      :value="vacancyStore.vacancies"
      :loading="vacancyStore.loading"
      striped-rows
      row-hover
      class="cursor-pointer"
      @row-click="(e) => navigateToDetail(e.data.id)"
    >
      <Column field="title" header="Title" sortable />
      <Column field="status" header="Status" style="width: 130px" sortable>
        <template #body="{ data }">
          <VacancyStatusBadge :status="data.status" />
        </template>
      </Column>
      <Column header="Candidates" style="width: 120px">
        <template #body>
          <span class="text-gray-500">0</span>
        </template>
      </Column>
      <Column field="createdAt" header="Created" style="width: 130px" sortable>
        <template #body="{ data }">
          {{ formatDate(data.createdAt) }}
        </template>
      </Column>
      <Column header="Actions" style="width: 100px">
        <template #body="{ data }">
          <Button
            icon="pi pi-eye"
            severity="secondary"
            text
            size="small"
            @click.stop="navigateToDetail(data.id)"
          />
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          No vacancies found. Create your first vacancy to get started.
        </div>
      </template>
    </DataTable>
  </div>
</template>
