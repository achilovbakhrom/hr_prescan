<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import type { TeamMember } from '../types/settings.types'

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
    <Column header="Name">
      <template #body="{ data }">
        {{ (data as TeamMember).firstName }}
        {{ (data as TeamMember).lastName }}
      </template>
    </Column>
    <Column field="email" header="Email" />
    <Column header="Role">
      <template #body="{ data }">
        <Tag
          :value="(data as TeamMember).role.toUpperCase()"
          :severity="getRoleSeverity((data as TeamMember).role)"
        />
      </template>
    </Column>
    <Column header="Status">
      <template #body="{ data }">
        <Tag
          :value="(data as TeamMember).isActive ? 'Active' : 'Inactive'"
          :severity="(data as TeamMember).isActive ? 'success' : 'danger'"
        />
      </template>
    </Column>
    <Column header="Actions">
      <template #body="{ data }">
        <ToggleSwitch
          :model-value="(data as TeamMember).isActive"
          @update:model-value="emit('toggleActive', (data as TeamMember).id)"
        />
      </template>
    </Column>
  </DataTable>
</template>
