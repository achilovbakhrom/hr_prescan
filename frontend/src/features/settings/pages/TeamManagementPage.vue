<script setup lang="ts">
/**
 * TeamManagementPage — team roster + pending invitations.
 * Glass toolbar + GlassCard chrome around solid data tables.
 * Spec: docs/design/spec.md §9.
 */
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import GlassCard from '@/shared/components/GlassCard.vue'
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

const pendingInvitationsCount = computed(
  () => settingsStore.invitations.filter((i) => !i.isAccepted).length,
)
const activeMembersCount = computed(() => settingsStore.team.filter((m) => m.isActive).length)

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
  <div class="mx-auto max-w-6xl space-y-6">
    <!-- Header / glass toolbar -->
    <GlassCard class="!p-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
            {{ t('settings.team.title') }}
          </h1>
          <p
            class="mt-0.5 flex flex-wrap gap-x-3 gap-y-1 text-xs text-[color:var(--color-text-muted)]"
          >
            <span class="inline-flex items-center gap-1">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[color:var(--color-success)]"
                aria-hidden="true"
              ></span>
              <span class="font-mono">{{ activeMembersCount }}</span>
              {{ t('settings.team.activeMembers') || 'active members' }}
            </span>
            <span class="inline-flex items-center gap-1">
              <span
                class="h-1.5 w-1.5 rounded-full bg-[color:var(--color-warning)]"
                aria-hidden="true"
              ></span>
              <span class="font-mono">{{ pendingInvitationsCount }}</span>
              {{ t('settings.team.pendingInvitations') || 'pending invitations' }}
            </span>
          </p>
        </div>
        <Button
          :label="t('settings.team.invite')"
          icon="pi pi-plus"
          @click="showInviteDialog = true"
        />
      </div>
    </GlassCard>

    <Message v-if="successMessage" severity="success">
      {{ successMessage }}
    </Message>

    <Message v-if="errorMessage" severity="error">
      {{ errorMessage }}
    </Message>

    <div v-if="settingsStore.loading && !settingsStore.team.length" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else>
      <GlassCard v-if="settingsStore.invitations.length" :title="t('settings.team.invitations')">
        <InvitationsTable
          :invitations="settingsStore.invitations"
          @cancel="handleCancelInvitation"
        />
      </GlassCard>

      <GlassCard :title="t('settings.team.members')">
        <TeamMembersTable
          :members="settingsStore.team"
          @toggle-active="handleToggleActive"
          @update-permissions="handleUpdatePermissions"
        />
      </GlassCard>
    </template>

    <InviteHRDialog
      :visible="showInviteDialog"
      :loading="settingsStore.loading"
      @hide="showInviteDialog = false"
      @invite="handleInvite"
    />
  </div>
</template>
