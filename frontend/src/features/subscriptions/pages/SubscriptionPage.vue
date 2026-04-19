<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import UsageMeter from '../components/UsageMeter.vue'
import PlanCard from '../components/PlanCard.vue'
import { useSubscriptionStore } from '../stores/subscription.store'
import type { BillingPeriod } from '../types/subscription.types'

const { t } = useI18n()
const subscriptionStore = useSubscriptionStore()
const showCancelConfirm = ref(false)
const upgradePeriod = ref<BillingPeriod>('monthly')

async function handleCancel(): Promise<void> {
  await subscriptionStore.cancelSubscription()
  showCancelConfirm.value = false
}

async function handleUpgrade(planId: string): Promise<void> {
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
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">{{ t('subscriptions.title') }}</h1>

    <div v-if="subscriptionStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else>
      <!-- Current Plan -->
      <div
        v-if="subscriptionStore.currentSubscription"
        class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6"
      >
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-lg font-semibold">{{ t('subscriptions.currentPlan') }}</h2>
            <p class="mt-1 text-2xl font-bold text-blue-600">
              {{ subscriptionStore.currentSubscription.plan.name }}
            </p>
            <p class="mt-1 text-sm text-gray-500">
              {{
                t('subscriptions.billed', {
                  period: subscriptionStore.currentSubscription.billingPeriod,
                })
              }}
            </p>
          </div>
          <span
            class="rounded-full px-3 py-1 text-xs font-semibold"
            :class="
              subscriptionStore.currentSubscription.isActive
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            "
          >
            {{
              subscriptionStore.currentSubscription.isActive
                ? t('subscriptions.statusActive')
                : t('subscriptions.statusCancelled')
            }}
          </span>
        </div>

        <div class="mt-4 text-sm text-gray-600">
          <p>
            {{ t('subscriptions.currentPeriod') }}
            {{
              new Date(
                subscriptionStore.currentSubscription.currentPeriodStart,
              ).toLocaleDateString()
            }}
            —
            {{
              new Date(subscriptionStore.currentSubscription.currentPeriodEnd).toLocaleDateString()
            }}
          </p>
        </div>

        <div v-if="subscriptionStore.currentSubscription.isActive" class="mt-4">
          <Button
            v-if="!showCancelConfirm"
            :label="t('subscriptions.cancelSubscription')"
            severity="danger"
            outlined
            size="small"
            @click="showCancelConfirm = true"
          />
          <div v-else class="flex items-center gap-2">
            <span class="text-sm text-red-600">{{ t('subscriptions.areYouSure') }}</span>
            <Button
              :label="t('subscriptions.yesCancel')"
              severity="danger"
              size="small"
              @click="handleCancel"
            />
            <Button
              :label="t('subscriptions.keepPlan')"
              outlined
              size="small"
              @click="showCancelConfirm = false"
            />
          </div>
        </div>
      </div>

      <!-- Usage -->
      <div v-if="subscriptionStore.usage" class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
        <h2 class="mb-4 text-lg font-semibold">{{ t('subscriptions.usage') }}</h2>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <UsageMeter
            :label="t('subscriptions.vacanciesUsed')"
            :used="subscriptionStore.usage?.vacancies?.used ?? 0"
            :limit="subscriptionStore.usage?.vacancies?.limit ?? 0"
          />
          <UsageMeter
            :label="t('subscriptions.interviewsUsed')"
            :used="subscriptionStore.usage?.interviews?.used ?? 0"
            :limit="subscriptionStore.usage?.interviews?.limit ?? 0"
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
      </div>

      <!-- Upgrade -->
      <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
        <h2 class="mb-4 text-lg font-semibold">{{ t('subscriptions.availablePlans') }}</h2>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <PlanCard
            v-for="plan in subscriptionStore.plans"
            :key="plan.id"
            :plan="plan"
            :billing-period="upgradePeriod"
            :is-current-plan="subscriptionStore.currentSubscription?.plan.id === plan.id"
            @select="handleUpgrade"
          />
        </div>
      </div>

      <!-- Billing History Placeholder -->
      <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
        <h2 class="mb-4 text-lg font-semibold">{{ t('subscriptions.billingHistory') }}</h2>
        <p class="text-sm text-gray-500">
          {{ t('subscriptions.billingHistoryComingSoon') }}
        </p>
      </div>
    </template>
  </div>
</template>
