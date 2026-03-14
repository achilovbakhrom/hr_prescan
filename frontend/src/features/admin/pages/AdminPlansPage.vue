<script setup lang="ts">
import { onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAdminStore } from '../stores/admin.store'

const adminStore = useAdminStore()

onMounted(() => adminStore.fetchPlans())
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-2xl font-bold">Subscription Plans</h1>

    <DataTable
      :value="adminStore.plans"
      :loading="adminStore.loading"
      striped-rows
    >
      <Column field="name" header="Plan Name" />
      <Column field="tier" header="Tier" />
      <Column header="Monthly Price">
        <template #body="{ data }">
          ${{ data.priceMonthly }}
        </template>
      </Column>
      <Column header="Yearly Price">
        <template #body="{ data }">
          ${{ data.priceYearly }}
        </template>
      </Column>
      <Column field="maxVacancies" header="Max Vacancies" />
      <Column field="maxInterviewsPerMonth" header="Max Interviews/Mo" />
      <Column field="maxHrUsers" header="Max HR Users" />
      <Column header="Storage">
        <template #body="{ data }">
          {{ data.maxStorageGb }} GB
        </template>
      </Column>
    </DataTable>
  </div>
</template>
