<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAdminStore } from '../stores/admin.store'
import type { AdminUser } from '../types/admin.types'

const adminStore = useAdminStore()
const search = ref('')
const roleFilter = ref<string | undefined>(undefined)

const roleOptions = [
  { label: 'All Roles', value: undefined },
  { label: 'Admin', value: 'admin' },
  { label: 'HR', value: 'hr' },
  { label: 'Candidate', value: 'candidate' },
]

function handleSearch(): void {
  adminStore.fetchUsers({
    search: search.value || undefined,
    role: roleFilter.value,
  })
}

async function handleToggleStatus(user: AdminUser): Promise<void> {
  await adminStore.toggleUserStatus(user.id, !user.isActive)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => adminStore.fetchUsers())
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-2xl font-bold">Users</h1>

    <div class="flex gap-2">
      <InputText
        v-model="search"
        placeholder="Search users..."
        class="w-64"
        @keyup.enter="handleSearch"
      />
      <Select
        v-model="roleFilter"
        :options="roleOptions"
        option-label="label"
        option-value="value"
        placeholder="Filter by role"
        class="w-40"
        @change="handleSearch"
      />
      <Button
        icon="pi pi-search"
        outlined
        @click="handleSearch"
      />
    </div>

    <DataTable
      :value="adminStore.users"
      :loading="adminStore.loading"
      striped-rows
      paginator
      :rows="10"
      :total-records="adminStore.usersCount"
    >
      <Column field="email" header="Email" sortable />
      <Column header="Name" sortable>
        <template #body="{ data }">
          {{ (data as AdminUser).firstName }} {{ (data as AdminUser).lastName }}
        </template>
      </Column>
      <Column field="role" header="Role" sortable />
      <Column field="companyName" header="Company" />
      <Column header="Status">
        <template #body="{ data }">
          <span
            class="rounded-full px-2 py-1 text-xs font-semibold"
            :class="
              (data as AdminUser).isActive
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            "
          >
            {{ (data as AdminUser).isActive ? 'Active' : 'Blocked' }}
          </span>
        </template>
      </Column>
      <Column field="createdAt" header="Created">
        <template #body="{ data }">
          {{ formatDate((data as AdminUser).createdAt) }}
        </template>
      </Column>
      <Column header="Actions">
        <template #body="{ data }">
          <Button
            :label="(data as AdminUser).isActive ? 'Block' : 'Activate'"
            :severity="(data as AdminUser).isActive ? 'danger' : 'success'"
            size="small"
            outlined
            @click="handleToggleStatus(data as AdminUser)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
