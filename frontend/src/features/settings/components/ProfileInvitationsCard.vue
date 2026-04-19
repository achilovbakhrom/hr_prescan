<script setup lang="ts">
/**
 * ProfileInvitationsCard — pending company invitations, list of rows.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import type { PendingInvitation } from '@/shared/types/auth.types'

defineProps<{
  invitations: PendingInvitation[]
  acceptingToken: string | null
}>()

const emit = defineEmits<{
  accept: [inv: PendingInvitation]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<template>
  <GlassCard accent="ai">
    <div class="mb-4 flex items-center gap-2">
      <span
        class="flex h-8 w-8 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]"
      >
        <i class="pi pi-envelope"></i>
      </span>
      <h2 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ t('settings.profile.pendingInvitations', { count: invitations.length }) }}
      </h2>
    </div>
    <div class="space-y-3">
      <div
        v-for="inv in invitations"
        :key="inv.id"
        class="flex flex-col gap-3 rounded-md border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="min-w-0">
          <p class="font-semibold text-[color:var(--color-text-primary)]">
            {{ inv.accountOwnerName }}
          </p>
          <p
            v-if="inv.companies?.length"
            class="mt-0.5 text-sm text-[color:var(--color-text-secondary)]"
          >
            {{ inv.companies.map((c) => c.name).join(', ') }}
          </p>
          <p
            class="mt-1 flex flex-wrap gap-x-2 gap-y-0.5 text-xs text-[color:var(--color-text-muted)]"
          >
            <span>{{ t('settings.profile.invitedBy', { name: inv.invitedByName }) }}</span>
            <span class="font-mono">{{ formatDate(inv.createdAt) }}</span>
            <span>·</span>
            <span>{{ t('settings.profile.expires', { date: formatDate(inv.expiresAt) }) }}</span>
          </p>
        </div>
        <Button
          :label="t('settings.profile.accept')"
          icon="pi pi-check"
          size="small"
          :loading="acceptingToken === inv.token"
          @click="emit('accept', inv)"
        />
      </div>
    </div>
    <p class="mt-3 text-xs text-[color:var(--color-text-muted)]">
      {{ t('settings.profile.acceptInvitationHint') }}
    </p>
  </GlassCard>
</template>
