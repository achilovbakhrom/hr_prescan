<script setup lang="ts">
/**
 * PricingPeriodToggle — glass segmented toggle between monthly / yearly.
 * Pill-style segmented control with accent-highlighted active tab.
 */
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import type { BillingPeriod } from '../types/subscription.types'

defineProps<{
  modelValue: BillingPeriod
}>()

const emit = defineEmits<{
  'update:modelValue': [value: BillingPeriod]
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-col items-center gap-3">
    <GlassSurface level="1" class="inline-flex items-center gap-1 rounded-full p-1">
      <button
        type="button"
        :class="[
          'period-toggle',
          modelValue === 'monthly' ? 'period-toggle--active' : 'period-toggle--inactive',
        ]"
        @click="emit('update:modelValue', 'monthly')"
      >
        {{ t('subscriptions.monthly') }}
      </button>
      <button
        type="button"
        :class="[
          'period-toggle',
          modelValue === 'yearly' ? 'period-toggle--active' : 'period-toggle--inactive',
        ]"
        @click="emit('update:modelValue', 'yearly')"
      >
        {{ t('subscriptions.yearly') }}
        <span
          class="ml-1.5 rounded-full bg-[color:var(--color-accent-celebrate-soft)] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[color:var(--color-accent-celebrate)]"
        >
          -20%
        </span>
      </button>
    </GlassSurface>
    <p v-if="modelValue === 'yearly'" class="text-xs text-[color:var(--color-accent-celebrate)]">
      {{ t('subscriptions.saveUpTo') }}
    </p>
  </div>
</template>

<style scoped>
.period-toggle {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 9999px;
  transition:
    background-color 240ms var(--ease-ios),
    color 240ms var(--ease-ios);
  cursor: pointer;
  white-space: nowrap;
}
.period-toggle--active {
  background: var(--color-accent);
  color: var(--color-text-on-accent);
  box-shadow: var(--shadow-card);
}
.period-toggle--inactive {
  background: transparent;
  color: var(--color-text-secondary);
}
.period-toggle--inactive:hover {
  color: var(--color-text-primary);
}
.period-toggle:focus-visible {
  outline: 2px solid var(--color-border-ring);
  outline-offset: 2px;
}
</style>
