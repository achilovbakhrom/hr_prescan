<script setup lang="ts">
/**
 * SubscriptionPage — authenticated subscription management.
 * Current plan summary + usage metrics + upgrade grid + billing history.
 * Spec: docs/design/spec.md §9.
 */
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import UsageMeter from '../components/UsageMeter.vue'
import PlanCard from '../components/PlanCard.vue'
import CurrentPlanCard from '../components/CurrentPlanCard.vue'
import BillingHistoryCard from '../components/BillingHistoryCard.vue'
import { useSubscriptionStore } from '../stores/subscription.store'
import { BILLING_ENABLED, FREE_ACCESS_ACTIVE_USER_TARGET } from '@/shared/constants/billing'
import type { BillingPeriod } from '../types/subscription.types'

const { t } = useI18n()
const subscriptionStore = useSubscriptionStore()
const upgradePeriod = ref<BillingPeriod>('monthly')
const billingEnabled = computed(() => subscriptionStore.usage?.billingEnabled ?? BILLING_ENABLED)
const activeUserTarget = computed(
  () => subscriptionStore.usage?.freeAccessActiveUserTarget ?? FREE_ACCESS_ACTIVE_USER_TARGET,
)

async function handleCancel(): Promise<void> {
  if (!billingEnabled.value) return
  await subscriptionStore.cancelSubscription()
}

async function handleUpgrade(planId: string): Promise<void> {
  if (!billingEnabled.value) return
  await subscriptionStore.subscribe(planId, upgradePeriod.value)
  await subscriptionStore.fetchCurrentSubscription()
}

onMounted(async () => {
  await Promise.all([
    subscriptionStore.fetchCurrentSubscription(),
    subscriptionStore.fetchUsage(),
    subscriptionStore.fetchPlans(),
  ])
})
</script>

<template>
  <div class="w-full space-y-6">
    <header class="flex flex-col gap-1">
      <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
        {{ t('subscriptions.title') }}
      </h1>
      <p class="text-sm text-[color:var(--color-text-muted)]">
        {{ t('subscriptions.manageYourPlan') || 'Manage your plan, usage and billing.' }}
      </p>
    </header>

    <div v-if="subscriptionStore.loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else>
      <!-- Current Plan -->
      <CurrentPlanCard
        v-if="subscriptionStore.currentSubscription"
        :subscription="subscriptionStore.currentSubscription"
        :billing-enabled="billingEnabled"
        @cancel="handleCancel"
      />

      <GlassCard v-if="!billingEnabled" accent="ai" :title="t('subscriptions.earlyAccessTitle')">
        <div class="flex flex-col gap-2 text-sm text-[color:var(--color-text-secondary)]">
          <p>{{ t('subscriptions.earlyAccessBody', { count: activeUserTarget }) }}</p>
          <p>{{ t('subscriptions.earlyAccessNoAction') }}</p>
        </div>
      </GlassCard>

      <!-- Usage -->
      <GlassCard v-if="subscriptionStore.usage" :title="t('subscriptions.usage')">
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <UsageMeter
            :label="t('subscriptions.vacanciesUsed')"
            :used="subscriptionStore.usage?.vacancies?.used ?? 0"
            :limit="subscriptionStore.usage?.vacancies?.limit ?? 0"
          />
          <UsageMeter
            :label="t('subscriptions.interviewsUsed')"
            :used="subscriptionStore.usage?.interviewsThisMonth?.used ?? 0"
            :limit="subscriptionStore.usage?.interviewsThisMonth?.limit ?? 0"
          />
          <UsageMeter
            :label="t('subscriptions.hrUsersUsed')"
            :used="subscriptionStore.usage?.hrUsers?.used ?? 0"
            :limit="subscriptionStore.usage?.hrUsers?.limit ?? 0"
          />
          <UsageMeter
            :label="t('subscriptions.storageUsed')"
            :used="subscriptionStore.usage?.storage?.usedGb ?? 0"
            :limit="subscriptionStore.usage?.storage?.limitGb ?? 0"
            unit="GB"
          />
        </div>
      </GlassCard>

      <!-- Upgrade plans -->
      <section v-if="billingEnabled" class="space-y-5">
        <header class="flex flex-col gap-1">
          <h2 class="text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('subscriptions.availablePlans') }}
          </h2>
          <p class="text-sm text-[color:var(--color-text-muted)]">
            {{ t('subscriptions.upgradeAnytime') || 'Upgrade or downgrade your plan at any time.' }}
          </p>
        </header>
        <div
          class="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3"
          :class="subscriptionStore.plans.length === 4 ? 'lg:grid-cols-4' : ''"
        >
          <PlanCard
            v-for="plan in subscriptionStore.plans"
            :key="plan.id"
            :plan="plan"
            :billing-period="upgradePeriod"
            :is-current-plan="subscriptionStore.currentSubscription?.plan.id === plan.id"
            @select="handleUpgrade"
          />
        </div>
      </section>

      <!-- Billing History -->
      <BillingHistoryCard v-if="billingEnabled" />
    </template>
  </div>
</template>
