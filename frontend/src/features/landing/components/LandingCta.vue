<script setup lang="ts">
/**
 * LandingCta — centered GlassCard with AI accent.
 * Bold headline + short supporting line + primary CTA.
 */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()
</script>

<template>
  <section id="pricing" class="px-4 py-24 sm:px-6 md:py-32">
    <div class="scroll-animate mx-auto max-w-3xl">
      <GlassCard accent="ai" class="cta-card">
        <div class="text-center sm:px-6 sm:py-6">
          <h2
            class="mb-4 text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl md:text-5xl"
          >
            {{ t('landing.cta.title') }}
          </h2>
          <p
            class="mx-auto mb-10 max-w-lg text-base leading-relaxed text-[color:var(--color-text-secondary)] md:text-lg"
          >
            {{ t('landing.cta.subtitle') }}
          </p>
          <div class="flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
            <Button
              :label="t('landing.cta.startFree')"
              icon="pi pi-arrow-right"
              icon-pos="right"
              size="large"
              class="w-full sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.REGISTER })"
            />
            <Button
              :label="t('landing.cta.viewPricing')"
              severity="secondary"
              outlined
              size="large"
              class="w-full sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.PRICING })"
            />
          </div>
        </div>
      </GlassCard>
    </div>
  </section>
</template>

<style scoped>
.cta-card {
  position: relative;
}
/* Add a subtle ambient glow behind the card using the accent-ai tint. */
.cta-card::after {
  content: '';
  position: absolute;
  inset: -30px;
  z-index: -1;
  pointer-events: none;
  background: radial-gradient(ellipse at center, var(--color-accent-ai-soft), transparent 65%);
  opacity: 0.6;
  filter: blur(24px);
}
</style>
