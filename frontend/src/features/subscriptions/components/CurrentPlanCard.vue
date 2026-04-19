<script setup lang="ts">
/**
 * CurrentPlanCard — summary of the active subscription: plan name,
 * billing period, date range, status pill, and cancel flow.
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import type { CompanySubscription } from '../types/subscription.types'

defineProps<{
  subscription: CompanySubscription
}>()

const emit = defineEmits<{
  cancel: []
}>()

const { t } = useI18n()
const showCancelConfirm = ref(false)

function confirmCancel(): void {
  emit('cancel')
  showCancelConfirm.value = false
}

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
    <div class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
      <div class="flex flex-col gap-1">
        <span
          class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('subscriptions.currentPlan') }}
        </span>
        <p
          class="font-mono text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]"
        >
          {{ subscription.plan.name }}
        </p>
        <p class="text-sm text-[color:var(--color-text-secondary)]">
          {{ t('subscriptions.billed', { period: subscription.billingPeriod }) }}
        </p>
      </div>
      <span
        class="inline-flex h-7 items-center rounded-full border px-3 text-xs font-semibold uppercase tracking-wide"
        :class="
          subscription.isActive
            ? 'border-[color:var(--color-success)] bg-[color:color-mix(in_srgb,var(--color-success)_12%,transparent)] text-[color:var(--color-success)]'
            : 'border-[color:var(--color-danger)] bg-[color:color-mix(in_srgb,var(--color-danger)_12%,transparent)] text-[color:var(--color-danger)]'
        "
      >
        {{
          subscription.isActive
            ? t('subscriptions.statusActive')
            : t('subscriptions.statusCancelled')
        }}
      </span>
    </div>

    <div
      class="mt-6 flex items-center gap-2 rounded-md border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-sunken)] px-4 py-3 text-sm"
    >
      <i class="pi pi-calendar text-[color:var(--color-text-muted)]"></i>
      <span class="text-[color:var(--color-text-secondary)]">
        {{ t('subscriptions.currentPeriod') }}
      </span>
      <span class="font-mono text-[color:var(--color-text-primary)]">
        {{ formatDate(subscription.currentPeriodStart) }} —
        {{ formatDate(subscription.currentPeriodEnd) }}
      </span>
    </div>

    <div v-if="subscription.isActive" class="mt-5 flex flex-wrap items-center gap-2">
      <Button
        v-if="!showCancelConfirm"
        :label="t('subscriptions.cancelSubscription')"
        severity="danger"
        outlined
        size="small"
        icon="pi pi-times"
        @click="showCancelConfirm = true"
      />
      <template v-else>
        <span class="text-sm text-[color:var(--color-danger)]">
          {{ t('subscriptions.areYouSure') }}
        </span>
        <Button
          :label="t('subscriptions.yesCancel')"
          severity="danger"
          size="small"
          @click="confirmCancel"
        />
        <Button
          :label="t('subscriptions.keepPlan')"
          severity="secondary"
          outlined
          size="small"
          @click="showCancelConfirm = false"
        />
      </template>
    </div>
  </GlassCard>
</template>
