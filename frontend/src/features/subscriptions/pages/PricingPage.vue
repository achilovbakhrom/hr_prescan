<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import PlanCard from '../components/PlanCard.vue'
import { useSubscriptionStore } from '../stores/subscription.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { BillingPeriod } from '../types/subscription.types'

const { t } = useI18n()
const router = useRouter()
const subscriptionStore = useSubscriptionStore()
const billingPeriod = ref<BillingPeriod>('monthly')

function togglePeriod(period: BillingPeriod): void {
  billingPeriod.value = period
}

function handleSelectPlan(): void {
  router.push({ name: ROUTE_NAMES.REGISTER })
}

onMounted(() => subscriptionStore.fetchPlans())
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-16">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900">
        {{ t('subscriptions.choosePlan') }}
      </h1>
      <p class="mt-4 text-lg text-gray-600">
        Scale your hiring process with the right plan for your team
      </p>
    </div>

    <div class="mt-8 flex items-center justify-center gap-2">
      <Button
        :label="t('subscriptions.monthly')"
        :outlined="billingPeriod !== 'monthly'"
        size="small"
        @click="togglePeriod('monthly')"
      />
      <Button
        :label="t('subscriptions.yearly')"
        :outlined="billingPeriod !== 'yearly'"
        size="small"
        @click="togglePeriod('yearly')"
      />
      <span v-if="billingPeriod === 'yearly'" class="ml-2 text-sm font-medium text-green-600">
        {{ t('subscriptions.saveUpTo') }}
      </span>
    </div>

    <div v-if="subscriptionStore.loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div v-else class="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      <PlanCard
        v-for="plan in subscriptionStore.plans"
        :key="plan.id"
        :plan="plan"
        :billing-period="billingPeriod"
        @select="handleSelectPlan"
      />
    </div>
  </div>
</template>
