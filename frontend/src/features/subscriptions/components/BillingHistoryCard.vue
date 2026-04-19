<script setup lang="ts">
/**
 * BillingHistoryCard — placeholder glass card for billing history.
 * Shows an empty state until billing data is wired.
 */
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'

const { t } = useI18n()
</script>

<template>
  <GlassCard :title="t('subscriptions.billingHistory')">
    <div
      class="flex flex-col items-center gap-3 rounded-md border border-dashed border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-sunken)] px-6 py-10 text-center"
    >
      <i class="pi pi-receipt text-3xl text-[color:var(--color-text-muted)]"></i>
      <p class="text-sm text-[color:var(--color-text-muted)]">
        {{ t('subscriptions.billingHistoryComingSoon') }}
      </p>
    </div>
  </GlassCard>
</template>
