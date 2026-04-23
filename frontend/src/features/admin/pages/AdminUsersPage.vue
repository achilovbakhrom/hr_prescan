<script setup lang="ts">
/**
 * AdminUsersPage — denser admin table for user management.
 * Glass toolbar + solid DataTable rows per spec §9.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from '@/shared/components/AppSelect.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { useAdminStore } from '../stores/admin.store'
import type { AdminUser } from '../types/admin.types'
import AdminPageHeader from '../components/AdminPageHeader.vue'
import AdminFiltersBar from '../components/AdminFiltersBar.vue'

const { t } = useI18n()
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

function roleBadgeClass(role: string): string {
  switch (role) {
    case 'admin':
      return 'bg-[color:color-mix(in_srgb,var(--color-warning)_18%,transparent)] text-[color:var(--color-warning)]'
    case 'hr':
      return 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
    case 'candidate':
      return 'bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]'
    default:
      return 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
  }
}

onMounted(() => adminStore.fetchUsers())
</script>

<template>
  <div class="mx-auto w-full max-w-7xl">
    <AdminPageHeader :eyebrow="t('admin.title')" :title="t('admin.users.title')" />

    <AdminFiltersBar>
      <InputText
        v-model="search"
        placeholder="Search users..."
        class="w-56"
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
      <Button icon="pi pi-search" severity="secondary" size="small" @click="handleSearch" />
    </AdminFiltersBar>

    <DataTable
      :value="adminStore.users"
      :loading="adminStore.loading"
      striped-rows
      paginator
      :rows="15"
      :total-records="adminStore.usersCount"
      size="small"
      class="admin-table text-sm"
    >
      <Column field="email" :header="t('admin.users.email')" sortable>
        <template #body="{ data }">
          <span class="font-mono text-xs text-[color:var(--color-text-secondary)]">{{
            (data as AdminUser).email
          }}</span>
        </template>
      </Column>
      <Column :header="t('admin.users.name')" sortable>
        <template #body="{ data }">
          {{ (data as AdminUser).firstName }} {{ (data as AdminUser).lastName }}
        </template>
      </Column>
      <Column field="role" :header="t('admin.users.role')" sortable>
        <template #body="{ data }">
          <span
            class="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
            :class="roleBadgeClass((data as AdminUser).role)"
            >{{ (data as AdminUser).role }}</span
          >
        </template>
      </Column>
      <Column field="companyName" :header="t('admin.users.company')">
        <template #body="{ data }">
          <span class="text-[color:var(--color-text-secondary)]">{{
            (data as AdminUser).companyName || '—'
          }}</span>
        </template>
      </Column>
      <Column :header="t('admin.users.status')">
        <template #body="{ data }">
          <span
            class="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
            :class="
              (data as AdminUser).isActive
                ? 'bg-[color:color-mix(in_srgb,var(--color-success)_15%,transparent)] text-[color:var(--color-success)]'
                : 'bg-[color:color-mix(in_srgb,var(--color-danger)_15%,transparent)] text-[color:var(--color-danger)]'
            "
          >
            {{ (data as AdminUser).isActive ? 'Active' : 'Blocked' }}
          </span>
        </template>
      </Column>
      <Column field="createdAt" header="Created">
        <template #body="{ data }">
          <span class="font-mono text-xs text-[color:var(--color-text-muted)]">{{
            formatDate((data as AdminUser).createdAt)
          }}</span>
        </template>
      </Column>
      <Column :header="t('common.actions')">
        <template #body="{ data }">
          <Button
            :label="
              (data as AdminUser).isActive
                ? t('admin.companies.block')
                : t('settings.team.activate')
            "
            :severity="(data as AdminUser).isActive ? 'danger' : 'success'"
            size="small"
            outlined
            :loading="adminStore.isMutating((data as AdminUser).id)"
            :disabled="adminStore.isMutating((data as AdminUser).id)"
            @click="handleToggleStatus(data as AdminUser)"
          />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
