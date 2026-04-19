<script setup lang="ts">
/**
 * AdminPlansPage — subscription plan management (denser treatment).
 */
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAdminStore } from '../stores/admin.store'
import AdminPageHeader from '../components/AdminPageHeader.vue'

const { t } = useI18n()
const adminStore = useAdminStore()

onMounted(() => adminStore.fetchPlans())
</script>

<template>
  <div class="mx-auto w-full max-w-7xl">
    <AdminPageHeader :eyebrow="t('admin.title')" :title="t('nav.plans')" />

    <DataTable
      :value="adminStore.plans"
      :loading="adminStore.loading"
      striped-rows
      size="small"
      class="admin-table text-sm"
    >
      <Column field="name" header="Plan Name">
        <template #body="{ data }">
          <span class="font-medium text-[color:var(--color-text-primary)]">{{ data.name }}</span>
        </template>
      </Column>
      <Column field="tier" header="Tier">
        <template #body="{ data }">
          <span
            class="rounded-full bg-[color:var(--color-accent-soft)] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-[color:var(--color-accent)]"
            >{{ data.tier }}</span
          >
        </template>
      </Column>
      <Column header="Monthly Price">
        <template #body="{ data }">
          <span class="font-mono tabular-nums text-[color:var(--color-text-secondary)]"
            >${{ data.priceMonthly }}</span
          >
        </template>
      </Column>
      <Column header="Yearly Price">
        <template #body="{ data }">
          <span class="font-mono tabular-nums text-[color:var(--color-text-secondary)]"
            >${{ data.priceYearly }}</span
          >
        </template>
      </Column>
      <Column field="maxVacancies" header="Max Vacancies">
        <template #body="{ data }">
          <span class="font-mono tabular-nums">{{ data.maxVacancies }}</span>
        </template>
      </Column>
      <Column field="maxInterviewsPerMonth" header="Max Interviews/Mo">
        <template #body="{ data }">
          <span class="font-mono tabular-nums">{{ data.maxInterviewsPerMonth }}</span>
        </template>
      </Column>
      <Column field="maxHrUsers" header="Max HR Users">
        <template #body="{ data }">
          <span class="font-mono tabular-nums">{{ data.maxHrUsers }}</span>
        </template>
      </Column>
      <Column header="Storage">
        <template #body="{ data }">
          <span class="font-mono tabular-nums text-[color:var(--color-text-secondary)]"
            >{{ data.maxStorageGb }} GB</span
          >
        </template>
      </Column>
    </DataTable>
  </div>
</template>
