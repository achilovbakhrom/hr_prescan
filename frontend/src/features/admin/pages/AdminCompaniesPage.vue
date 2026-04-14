<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAdminStore } from '../stores/admin.store'
import type { AdminCompany } from '../types/admin.types'

const { t } = useI18n()
const adminStore = useAdminStore()
const search = ref('')

function handleSearch(): void {
  adminStore.fetchCompanies({ search: search.value || undefined })
}

async function handleToggleStatus(company: AdminCompany): Promise<void> {
  await adminStore.toggleCompanyStatus(company.id, !company.isActive)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => adminStore.fetchCompanies())
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t('admin.companies.title') }}</h1>
    </div>

    <div class="flex gap-2">
      <InputText
        v-model="search"
        placeholder="Search companies..."
        class="w-64"
        @keyup.enter="handleSearch"
      />
      <Button icon="pi pi-search" outlined @click="handleSearch" />
    </div>

    <DataTable
      :value="adminStore.companies"
      :loading="adminStore.loading"
      striped-rows
      paginator
      :rows="10"
      :total-records="adminStore.companiesCount"
    >
      <Column field="name" :header="t('admin.companies.name')" sortable />
      <Column field="industry" header="Industry" sortable />
      <Column field="size" header="Size" sortable />
      <Column field="country" header="Country" />
      <Column field="planTier" :header="t('admin.companies.plan')" sortable />
      <Column field="usersCount" :header="t('admin.companies.users')" sortable />
      <Column field="vacanciesCount" :header="t('admin.companies.vacancies')" sortable />
      <Column :header="t('admin.companies.status')">
        <template #body="{ data }">
          <span
            class="rounded-full px-2 py-1 text-xs font-semibold"
            :class="
              (data as AdminCompany).isActive
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            "
          >
            {{ (data as AdminCompany).isActive ? 'Active' : 'Blocked' }}
          </span>
        </template>
      </Column>
      <Column field="createdAt" header="Created">
        <template #body="{ data }">
          {{ formatDate((data as AdminCompany).createdAt) }}
        </template>
      </Column>
      <Column :header="t('admin.companies.actions')">
        <template #body="{ data }">
          <Button
            :label="
              (data as AdminCompany).isActive
                ? t('admin.companies.block')
                : t('settings.team.activate')
            "
            :severity="(data as AdminCompany).isActive ? 'danger' : 'success'"
            size="small"
            outlined
            @click="handleToggleStatus(data as AdminCompany)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
