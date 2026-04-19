<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import InviteHRDialog from '../components/InviteHRDialog.vue'
import InvitationsTable from '../components/InvitationsTable.vue'
import TeamMembersTable from '../components/TeamMembersTable.vue'
import { useSettingsStore } from '../stores/settings.store'
import type { HRPermission } from '@/shared/types/auth.types'

const { t } = useI18n()
const settingsStore = useSettingsStore()

const showInviteDialog = ref(false)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([settingsStore.fetchTeam(), settingsStore.fetchInvitations()])
})

async function handleInvite(payload: {
  email: string
  permissions: HRPermission[]
  companyIds: string[]
}): Promise<void> {
  successMessage.value = null
  errorMessage.value = null
  try {
    await settingsStore.inviteHR(payload)
    showInviteDialog.value = false
    successMessage.value = `Invitation sent to ${payload.email}.`
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Failed to send invitation. Please try again.'
  }
}

async function handleUpdatePermissions(userId: string, permissions: HRPermission[]): Promise<void> {
  errorMessage.value = null
  try {
    await settingsStore.updateMemberPermissions(userId, permissions)
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Failed to update permissions. Please try again.'
  }
}

async function handleCancelInvitation(invitationId: string): Promise<void> {
  errorMessage.value = null
  try {
    await settingsStore.cancelInvitation(invitationId)
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to cancel invitation.'
  }
}

async function handleToggleActive(userId: string): Promise<void> {
  errorMessage.value = null
  try {
    await settingsStore.toggleMemberActive(userId)
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Failed to update member status. Please try again.'
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl p-6">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">{{ t('settings.team.title') }}</h1>
      <Button
        :label="t('settings.team.invite')"
        icon="pi pi-plus"
        @click="showInviteDialog = true"
      />
    </div>

    <Message v-if="successMessage" severity="success" class="mb-4">
      {{ successMessage }}
    </Message>

    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <div
      v-if="settingsStore.loading && !settingsStore.team.length"
      class="py-12 text-center text-gray-500"
    >
      Loading team data...
    </div>

    <template v-else>
      <div v-if="settingsStore.invitations.length" class="mb-8 rounded-lg bg-white p-6 shadow-sm">
        <h2 class="mb-4 text-lg font-semibold text-gray-900">
          {{ t('settings.team.invitations') }}
        </h2>
        <InvitationsTable
          :invitations="settingsStore.invitations"
          @cancel="handleCancelInvitation"
        />
      </div>

      <div class="rounded-lg bg-white p-6 shadow-sm">
        <h2 class="mb-4 text-lg font-semibold text-gray-900">{{ t('settings.team.members') }}</h2>
        <TeamMembersTable
          :members="settingsStore.team"
          @toggle-active="handleToggleActive"
          @update-permissions="handleUpdatePermissions"
        />
      </div>
    </template>

    <InviteHRDialog
      :visible="showInviteDialog"
      :loading="settingsStore.loading"
      @hide="showInviteDialog = false"
      @invite="handleInvite"
    />
  </div>
</template>
