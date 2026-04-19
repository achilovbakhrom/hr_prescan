<script setup lang="ts">
/**
 * PricingPage — public pricing with 3 plan cards. Center plan highlighted
 * (violet glow). Monthly/yearly toggle at top. Geist Mono for price numbers.
 * Spec: docs/design/spec.md §9 — pricing area, PublicLayout.
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PlanCard from '../components/PlanCard.vue'
import PricingPeriodToggle from '../components/PricingPeriodToggle.vue'
import { useSubscriptionStore } from '../stores/subscription.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { BillingPeriod } from '../types/subscription.types'

const { t } = useI18n()
const router = useRouter()
const subscriptionStore = useSubscriptionStore()
const billingPeriod = ref<BillingPeriod>('monthly')

function handleSelectPlan(): void {
  router.push({ name: ROUTE_NAMES.REGISTER })
}

onMounted(() => subscriptionStore.fetchPlans())
</script>

<template>
  <div class="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-20 lg:py-24">
    <!-- Hero header -->
    <div class="pricing-hero text-center">
      <span
        class="bg-glass-1 border-glass shadow-glass inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium text-[color:var(--color-accent-ai)]"
      >
        <i class="pi pi-tag text-[10px]"></i>
        {{ t('subscriptions.simpleTransparent') || 'Simple, transparent pricing' }}
      </span>
      <h1 class="text-display mt-5 mx-auto max-w-3xl text-[color:var(--color-text-primary)]">
        {{ t('subscriptions.choosePlan') }}
      </h1>
      <p
        class="mx-auto mt-5 max-w-2xl text-base text-[color:var(--color-text-secondary)] sm:text-lg"
      >
        {{
          t('subscriptions.choosePlanSub') ||
          'Scale your hiring process with the right plan for your team. No hidden fees. Cancel anytime.'
        }}
      </p>
    </div>

    <!-- Toggle -->
    <div class="pricing-toggle mt-10 flex justify-center">
      <PricingPeriodToggle v-model="billingPeriod" />
    </div>

    <!-- Loading -->
    <div v-if="subscriptionStore.loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <!-- Plan grid -->
    <div
      v-else-if="subscriptionStore.plans.length"
      class="pricing-grid mt-14 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
      :class="subscriptionStore.plans.length === 4 ? 'lg:grid-cols-4' : ''"
    >
      <PlanCard
        v-for="plan in subscriptionStore.plans"
        :key="plan.id"
        :plan="plan"
        :billing-period="billingPeriod"
        @select="handleSelectPlan"
      />
    </div>

    <!-- Empty -->
    <div v-else class="mt-14 text-center text-sm text-[color:var(--color-text-muted)]">
      {{ t('subscriptions.noPlans') || 'No plans available right now.' }}
    </div>

    <!-- Footer reassurance -->
    <div class="pricing-footer mt-16 text-center">
      <p class="text-sm text-[color:var(--color-text-muted)]">
        <i class="pi pi-shield mr-1.5 text-[color:var(--color-success)]"></i>
        {{ t('landing.promo.noCreditCard') }} ·
        {{ t('landing.promo.freeTrial') }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.pricing-hero,
.pricing-toggle,
.pricing-grid,
.pricing-footer {
  opacity: 0;
  animation: hero-enter 620ms var(--ease-ios) both;
}
.pricing-hero {
  animation-delay: 0ms;
}
.pricing-toggle {
  animation-delay: 120ms;
}
.pricing-grid {
  animation-delay: 200ms;
}
.pricing-footer {
  animation-delay: 320ms;
}
@keyframes hero-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@media (prefers-reduced-motion: reduce) {
  .pricing-hero,
  .pricing-toggle,
  .pricing-grid,
  .pricing-footer {
    animation: hero-enter-rm 200ms linear both;
    animation-delay: 0ms;
  }
  @keyframes hero-enter-rm {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
}
</style>
