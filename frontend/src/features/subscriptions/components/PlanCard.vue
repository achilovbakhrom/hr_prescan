<script setup lang="ts">
/**
 * PlanCard — single subscription plan card.
 * Visual: GlassCard composition. The recommended tier gets `accent="ai"`
 * styling (violet glow + "Most popular" badge). Price uses Geist Mono.
 * Spec: docs/design/spec.md §9 (Pricing area).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
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

const price = computed(() =>
  props.billingPeriod === 'monthly' ? props.plan.priceMonthly : props.plan.priceYearly,
)

const periodLabel = computed(() => (props.billingPeriod === 'monthly' ? '/mo' : '/yr'))

const features = computed(() => [
  `${props.plan.maxVacancies} vacancies`,
  `${props.plan.maxInterviewsPerMonth} interviews/month`,
  `${props.plan.maxHrUsers} HR users`,
  `${props.plan.maxStorageGb} GB storage`,
])

const isHighlighted = computed(() => props.plan.tier === 'professional')
const accent = computed<'default' | 'ai'>(() => (isHighlighted.value ? 'ai' : 'default'))
</script>

<template>
  <div class="relative flex">
    <GlassCard
      :accent="accent"
      class="plan-card flex w-full flex-col"
      :class="isHighlighted ? 'plan-card--highlighted' : ''"
    >
      <div v-if="isHighlighted" class="plan-card__badge">
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-[color:var(--color-accent-ai)] bg-[color:var(--color-accent-ai-soft)] px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-ai)]"
        >
          <i class="pi pi-star-fill text-[9px]"></i>
          Most popular
        </span>
      </div>

      <div class="flex flex-col gap-1">
        <h3 class="text-lg font-semibold text-[color:var(--color-text-primary)]">
          {{ plan.name }}
        </h3>
        <p class="text-sm text-[color:var(--color-text-muted)]">
          {{ plan.description }}
        </p>
      </div>

      <div class="mt-5 flex items-end gap-1.5">
        <span
          class="font-mono text-5xl font-semibold leading-none tracking-tight text-[color:var(--color-text-primary)]"
        >
          ${{ price }}
        </span>
        <span class="pb-1.5 font-mono text-sm text-[color:var(--color-text-muted)]">
          {{ periodLabel }}
        </span>
      </div>

      <ul class="mt-6 flex-1 space-y-3">
        <li
          v-for="feature in features"
          :key="feature"
          class="flex items-center gap-2.5 text-sm text-[color:var(--color-text-secondary)]"
        >
          <span
            class="flex h-5 w-5 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)]"
            :class="isHighlighted ? '!bg-[color:var(--color-accent-ai-soft)]' : ''"
          >
            <i
              class="pi pi-check text-[10px] font-bold"
              :class="
                isHighlighted
                  ? 'text-[color:var(--color-accent-ai)]'
                  : 'text-[color:var(--color-accent)]'
              "
            ></i>
          </span>
          {{ feature }}
        </li>
      </ul>

      <Button
        :label="isCurrentPlan ? t('subscriptions.currentPlan') : t('landing.hero.getStarted')"
        :disabled="isCurrentPlan"
        :outlined="!isHighlighted && !isCurrentPlan"
        :severity="isHighlighted ? undefined : 'secondary'"
        class="mt-6 w-full"
        size="large"
        @click="emit('select', plan.tier)"
      />
    </GlassCard>
  </div>
</template>

<style scoped>
.plan-card {
  transition:
    transform 320ms var(--ease-ios),
    box-shadow 320ms var(--ease-ios);
}
.plan-card:hover {
  transform: translateY(-2px);
}
.plan-card--highlighted {
  box-shadow:
    var(--shadow-glass-float),
    0 0 0 1px var(--color-accent-ai),
    0 20px 45px -15px color-mix(in srgb, var(--color-accent-ai) 35%, transparent);
}
.plan-card--highlighted:hover {
  transform: translateY(-4px);
}
.plan-card__badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
}
@media (prefers-reduced-motion: reduce) {
  .plan-card,
  .plan-card:hover {
    transform: none;
  }
}
</style>
