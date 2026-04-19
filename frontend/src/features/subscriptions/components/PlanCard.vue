<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { SubscriptionPlan, BillingPeriod } from '../types/subscription.types'

const props = defineProps<{
  plan: SubscriptionPlan
  billingPeriod: BillingPeriod
  isCurrentPlan?: boolean
}>()

const emit = defineEmits<{
  select: [planTier: string]
}>()

const { t } = useI18n()

const price = computed(() => {
  return props.billingPeriod === 'monthly' ? props.plan.priceMonthly : props.plan.priceYearly
})

const periodLabel = computed(() => {
  return props.billingPeriod === 'monthly' ? '/mo' : '/yr'
})

const features = computed(() => [
  `${props.plan.maxVacancies} vacancies`,
  `${props.plan.maxInterviewsPerMonth} interviews/month`,
  `${props.plan.maxHrUsers} HR users`,
  `${props.plan.maxStorageGb} GB storage`,
])

const isHighlighted = computed(() => props.plan.tier === 'professional')
</script>

<template>
  <div
    class="flex flex-col rounded-xl border-2 p-6 transition-shadow hover:shadow-lg"
    :class="isHighlighted ? 'border-blue-500 shadow-md' : 'border-gray-200'"
  >
    <div v-if="isHighlighted" class="mb-2 text-center">
      <span class="rounded-full bg-blue-100 dark:bg-blue-950 px-3 py-1 text-xs font-semibold text-blue-700">
        Most Popular
      </span>
    </div>

    <h3 class="text-lg font-bold text-gray-900">{{ plan.name }}</h3>
    <p class="mt-1 text-sm text-gray-500">{{ plan.description }}</p>

    <div class="mt-4">
      <span class="text-3xl font-bold text-gray-900"> ${{ price }} </span>
      <span class="text-gray-500">{{ periodLabel }}</span>
    </div>

    <ul class="mt-6 flex-1 space-y-3">
      <li
        v-for="feature in features"
        :key="feature"
        class="flex items-center gap-2 text-sm text-gray-600"
      >
        <i class="pi pi-check text-green-500"></i>
        {{ feature }}
      </li>
    </ul>

    <Button
      :label="isCurrentPlan ? t('subscriptions.currentPlan') : t('landing.hero.getStarted')"
      :disabled="isCurrentPlan"
      :outlined="!isHighlighted && !isCurrentPlan"
      class="mt-6 w-full"
      @click="emit('select', plan.tier)"
    />
  </div>
</template>
