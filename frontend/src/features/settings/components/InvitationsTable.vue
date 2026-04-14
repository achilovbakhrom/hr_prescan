<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import type { Invitation } from '../types/settings.types'

defineProps<{
  invitations: Invitation[]
}>()

const { t } = useI18n()

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

function getStatusSeverity(invitation: Invitation): 'success' | 'warn' | 'danger' {
  if (invitation.isAccepted) return 'success'
  const now = new Date()
  const expires = new Date(invitation.expiresAt)
  if (expires < now) return 'danger'
  return 'warn'
}

function getStatusLabel(invitation: Invitation): string {
  if (invitation.isAccepted) return 'Accepted'
  const now = new Date()
  const expires = new Date(invitation.expiresAt)
  if (expires < now) return 'Expired'
  return 'Pending'
}
</script>

<template>
  <DataTable :value="invitations" striped-rows>
    <Column field="email" :header="t('admin.users.email')" />
    <Column :header="t('common.status')">
      <template #body="{ data }">
        <Tag
          :value="getStatusLabel(data as Invitation)"
          :severity="getStatusSeverity(data as Invitation)"
        />
      </template>
    </Column>
    <Column header="Sent">
      <template #body="{ data }">
        {{ formatDate((data as Invitation).createdAt) }}
      </template>
    </Column>
    <Column header="Expires">
      <template #body="{ data }">
        {{ formatDate((data as Invitation).expiresAt) }}
      </template>
    </Column>
  </DataTable>
</template>
