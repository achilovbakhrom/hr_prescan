<script setup lang="ts">
/**
 * AdminCompaniesPage — denser admin table for company management.
 * Glass toolbar + solid DataTable rows per spec §9.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAdminStore } from '../stores/admin.store'
import type { AdminCompany } from '../types/admin.types'
import AdminPageHeader from '../components/AdminPageHeader.vue'
import AdminFiltersBar from '../components/AdminFiltersBar.vue'

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
  <div class="mx-auto w-full max-w-7xl">
    <AdminPageHeader :eyebrow="t('admin.title')" :title="t('admin.companies.title')" />

    <AdminFiltersBar>
      <InputText
        v-model="search"
        :placeholder="t('admin.companies.searchPlaceholder')"
        class="w-56"
        @keyup.enter="handleSearch"
      />
      <Button icon="pi pi-search" severity="secondary" size="small" @click="handleSearch" />
    </AdminFiltersBar>

    <DataTable
      :value="adminStore.companies"
      :loading="adminStore.loading"
      striped-rows
      paginator
      :rows="15"
      :total-records="adminStore.companiesCount"
      size="small"
      class="admin-table text-sm"
    >
      <Column field="name" :header="t('admin.companies.name')" sortable />
      <Column field="industry" :header="t('settings.company.industry')" sortable />
      <Column field="size" :header="t('settings.company.size')" sortable />
      <Column field="country" :header="t('settings.company.country')" />
      <Column field="planTier" :header="t('admin.companies.plan')" sortable>
        <template #body="{ data }">
          <span
            class="font-mono text-xs uppercase tracking-wide text-[color:var(--color-text-secondary)]"
            >{{ (data as AdminCompany).planTier }}</span
          >
        </template>
      </Column>
      <Column field="usersCount" :header="t('admin.companies.users')" sortable>
        <template #body="{ data }">
          <span class="font-mono tabular-nums">{{ (data as AdminCompany).usersCount }}</span>
        </template>
      </Column>
      <Column field="vacanciesCount" :header="t('admin.companies.vacancies')" sortable>
        <template #body="{ data }">
          <span class="font-mono tabular-nums">{{ (data as AdminCompany).vacanciesCount }}</span>
        </template>
      </Column>
      <Column :header="t('admin.companies.status')">
        <template #body="{ data }">
          <span
            class="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
            :class="
              (data as AdminCompany).isActive
                ? 'bg-[color:color-mix(in_srgb,var(--color-success)_15%,transparent)] text-[color:var(--color-success)]'
                : 'bg-[color:color-mix(in_srgb,var(--color-danger)_15%,transparent)] text-[color:var(--color-danger)]'
            "
          >
            {{ (data as AdminCompany).isActive ? t('common.active') : t('admin.blocked') }}
          </span>
        </template>
      </Column>
      <Column field="createdAt" :header="t('common.createdAt')">
        <template #body="{ data }">
          <span class="font-mono text-xs text-[color:var(--color-text-muted)]">{{
            formatDate((data as AdminCompany).createdAt)
          }}</span>
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
            :loading="adminStore.isMutating((data as AdminCompany).id)"
            :disabled="adminStore.isMutating((data as AdminCompany).id)"
            @click="handleToggleStatus(data as AdminCompany)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
