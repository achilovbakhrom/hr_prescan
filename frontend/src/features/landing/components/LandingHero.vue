<script setup lang="ts">
/**
 * LandingHero — Figma marketing hero: badge, headline, subhead, two CTAs,
 * a "no credit card" line, social-proof avatars, and a live-interview
 * preview card on the right.
 */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LandingHeroMockup from './LandingHeroMockup.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()

const avatars = [
  '/landing/avatar-11.jpg',
  '/landing/avatar-12.jpg',
  '/landing/avatar-13.jpg',
  '/landing/avatar-5.jpg',
  '/landing/avatar-32.jpg',
]
</script>

<template>
  <section class="relative px-4 pt-16 pb-20 sm:px-6 sm:pt-20 lg:pt-28">
    <div class="relative mx-auto max-w-7xl">
      <div class="grid items-center gap-12 lg:grid-cols-12">
        <!-- Left: copy -->
        <div class="text-center lg:col-span-7 lg:text-left">
          <span
            class="hero-stagger hero-stagger-1 inline-flex items-center gap-2 rounded-full border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] px-4 py-1.5 text-xs font-medium text-[color:var(--color-accent)]"
          >
            <i class="pi pi-sparkles text-[10px]"></i>
            {{ t('landing.badge.poweredBy') }}
          </span>

          <h1
            class="hero-stagger hero-stagger-2 mt-6 text-4xl font-bold leading-[1.05] tracking-tight text-[color:var(--color-text-primary)] sm:text-5xl lg:text-6xl"
          >
            {{ t('landing.hero.title') }}
          </h1>

          <p
            class="hero-stagger hero-stagger-3 mx-auto mt-5 max-w-xl text-base leading-relaxed text-[color:var(--color-text-secondary)] sm:text-lg lg:mx-0"
          >
            {{ t('landing.hero.subtitle') }}
          </p>

          <div
            class="hero-stagger hero-stagger-4 mt-8 flex flex-col items-center gap-3 sm:flex-row lg:justify-start"
          >
            <button
              type="button"
              class="inline-flex w-full cursor-pointer items-center justify-center gap-2 rounded-full bg-[linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)] px-6 py-3 text-sm font-semibold text-white shadow-[0_10px_30px_rgba(124,58,237,0.35)] transition-transform hover:-translate-y-0.5 sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.REGISTER })"
            >
              {{ t('landing.cta.startFree') }}
              <i class="pi pi-arrow-right text-xs"></i>
            </button>
            <a
              href="#how-it-works"
              class="inline-flex w-full items-center justify-center gap-2 rounded-full border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] px-6 py-3 text-sm font-semibold text-[color:var(--color-text-primary)] transition-colors hover:bg-[color:var(--color-surface-sunken)] sm:w-auto"
            >
              {{ t('landing.hero.seeFlow') }}
            </a>
          </div>

          <p class="hero-stagger hero-stagger-4 mt-4 text-sm text-[color:var(--color-text-muted)]">
            {{ t('landing.promo.noCreditCard') }} · {{ t('landing.promo.freeTrial') }}
          </p>

          <!-- Social proof -->
          <div
            class="hero-stagger hero-stagger-4 mt-9 flex items-center justify-center gap-3 lg:justify-start"
          >
            <div class="flex -space-x-2.5">
              <img
                v-for="(src, i) in avatars"
                :key="i"
                :src="src"
                alt=""
                class="h-9 w-9 rounded-full border-2 border-[color:var(--color-surface-base)] object-cover"
                loading="lazy"
              />
            </div>
            <span class="text-sm text-[color:var(--color-text-secondary)]">
              {{ t('landing.hero.trustedBy') }}
            </span>
          </div>
        </div>

        <!-- Right: preview card -->
        <div class="hero-mockup lg:col-span-5">
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
    animation: none;
    opacity: 1;
  }
}
</style>
