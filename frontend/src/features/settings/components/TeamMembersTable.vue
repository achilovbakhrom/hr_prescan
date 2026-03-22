<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import type { TeamMember } from '../types/settings.types'

const { t } = useI18n()

defineProps<{
  members: TeamMember[]
}>()

const emit = defineEmits<{
  toggleActive: [userId: string]
}>()

function getRoleSeverity(role: string): 'info' | 'warn' | undefined {
  if (role === 'admin') return 'warn'
  if (role === 'hr') return 'info'
  return undefined
}
</script>

<template>
  <DataTable :value="members" striped-rows>
    <Column :header="t('admin.users.name')">
      <template #body="{ data }">
        {{ (data as TeamMember).firstName }}
        {{ (data as TeamMember).lastName }}
      </template>
    </Column>
    <Column field="email" :header="t('admin.users.email')" />
    <Column :header="t('settings.team.role')">
      <template #body="{ data }">
        <Tag
          :value="(data as TeamMember).role.toUpperCase()"
          :severity="getRoleSeverity((data as TeamMember).role)"
        />
      </template>
    </Column>
    <Column :header="t('common.status')">
      <template #body="{ data }">
        <Tag
          :value="(data as TeamMember).isActive ? 'Active' : 'Inactive'"
          :severity="(data as TeamMember).isActive ? 'success' : 'danger'"
        />
      </template>
    </Column>
    <Column :header="t('common.actions')">
      <template #body="{ data }">
        <ToggleSwitch
          :model-value="(data as TeamMember).isActive"
          @update:model-value="emit('toggleActive', (data as TeamMember).id)"
        />
      </template>
    </Column>
  </DataTable>
</template>
