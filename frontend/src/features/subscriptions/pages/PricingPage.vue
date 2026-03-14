<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import PlanCard from '../components/PlanCard.vue'
import { useSubscriptionStore } from '../stores/subscription.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { BillingPeriod } from '../types/subscription.types'

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
        Choose Your Plan
      </h1>
      <p class="mt-4 text-lg text-gray-600">
        Scale your hiring process with the right plan for your team
      </p>
    </div>

    <div class="mt-8 flex items-center justify-center gap-2">
      <Button
        label="Monthly"
        :outlined="billingPeriod !== 'monthly'"
        size="small"
        @click="togglePeriod('monthly')"
      />
      <Button
        label="Yearly"
        :outlined="billingPeriod !== 'yearly'"
        size="small"
        @click="togglePeriod('yearly')"
      />
      <span
        v-if="billingPeriod === 'yearly'"
        class="ml-2 text-sm font-medium text-green-600"
      >
        Save up to 20%
      </span>
    </div>

    <div v-if="subscriptionStore.loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div
      v-else
      class="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4"
    >
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
