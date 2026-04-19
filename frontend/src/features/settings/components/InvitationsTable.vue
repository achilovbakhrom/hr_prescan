<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import type { Invitation } from '../types/settings.types'

defineProps<{
  invitations: Invitation[]
}>()

const emit = defineEmits<{
  cancel: [invitationId: string]
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
    <Column :header="t('settings.team.companies')">
      <template #body="{ data }">
        <span class="text-sm text-gray-700">
          {{ ((data as Invitation).companies || []).map((c) => c.name).join(', ') || '—' }}
        </span>
      </template>
    </Column>
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
    <Column :header="t('common.actions')">
      <template #body="{ data }">
        <Button
          v-if="!(data as Invitation).isAccepted"
          icon="pi pi-times"
          severity="danger"
          text
          size="small"
          :label="t('common.cancel')"
          @click="emit('cancel', (data as Invitation).id)"
        />
      </template>
    </Column>
  </DataTable>
</template>
