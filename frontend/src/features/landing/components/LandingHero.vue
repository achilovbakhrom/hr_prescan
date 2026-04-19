<script setup lang="ts">
/**
 * LandingHero — display headline + subhead + 2 CTAs + a tilted product
 * preview card. Staggered fade-up on mount using CSS keyframes.
 */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import LandingHeroMockup from './LandingHeroMockup.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()
</script>

<template>
  <section class="relative px-4 pt-20 pb-24 sm:px-6 sm:pt-24 sm:pb-28 lg:pt-32 lg:pb-36">
    <div class="relative mx-auto max-w-7xl">
      <div class="grid items-center gap-10 lg:grid-cols-12 lg:gap-12">
        <!-- Left: copy -->
        <div class="text-center lg:col-span-7 lg:text-left">
          <div class="hero-stagger hero-stagger-1 mb-5 inline-flex">
            <span
              class="bg-glass-1 border-glass shadow-glass inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium text-[color:var(--color-accent-ai)]"
            >
              <i class="pi pi-sparkles text-[10px]"></i>
              {{ t('landing.badge.poweredBy') }}
            </span>
          </div>

          <h1
            class="text-display hero-stagger hero-stagger-2 mb-5 text-[color:var(--color-text-primary)]"
          >
            {{ t('landing.hero.title') }}
          </h1>

          <p
            class="hero-stagger hero-stagger-3 mx-auto mb-8 max-w-xl text-base leading-relaxed text-[color:var(--color-text-secondary)] sm:text-lg lg:mx-0"
          >
            {{ t('landing.hero.subtitle') }}
          </p>

          <div
            class="hero-stagger hero-stagger-4 flex flex-col items-center gap-3 sm:flex-row lg:justify-start"
          >
            <Button
              :label="t('landing.hero.cta')"
              icon="pi pi-arrow-right"
              icon-pos="right"
              size="large"
              class="w-full sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.REGISTER })"
            />
            <Button
              :label="t('landing.hero.browseJobs')"
              icon="pi pi-search"
              severity="secondary"
              outlined
              size="large"
              class="w-full sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
            />
          </div>

          <p class="hero-stagger hero-stagger-4 mt-4 text-sm text-[color:var(--color-text-muted)]">
            {{ t('landing.promo.noCreditCard') }} · {{ t('landing.promo.freeTrial') }}
          </p>
        </div>

        <!-- Right: product preview (desktop only) -->
        <div class="hero-mockup hidden lg:col-span-5 lg:block">
          <LandingHeroMockup />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-stagger {
  opacity: 0;
  animation: hero-enter 620ms var(--ease-ios) both;
}
.hero-stagger-1 {
  animation-delay: 0ms;
}
.hero-stagger-2 {
  animation-delay: 80ms;
}
.hero-stagger-3 {
  animation-delay: 160ms;
}
.hero-stagger-4 {
  animation-delay: 240ms;
}
.hero-mockup {
  opacity: 0;
  animation: hero-enter 720ms var(--ease-ios) both;
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
  .hero-stagger,
  .hero-mockup {
    animation: hero-enter-rm 200ms linear both;
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
