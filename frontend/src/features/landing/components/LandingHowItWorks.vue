<script setup lang="ts">
/**
 * LandingHowItWorks — Figma "Three steps. Zero manual screening." section:
 * eyebrow + heading + three numbered step cards.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const steps = computed(() => [
  { n: '1', title: t('landing.howItWorks.step1'), desc: t('landing.howItWorks.step1Desc') },
  { n: '2', title: t('landing.howItWorks.step2'), desc: t('landing.howItWorks.step2Desc') },
  { n: '3', title: t('landing.howItWorks.step4'), desc: t('landing.howItWorks.step4Desc') },
])
</script>

<template>
  <section id="how-it-works" class="px-4 py-20 sm:px-6 md:py-28">
    <div class="mx-auto max-w-6xl">
      <div class="scroll-animate text-center">
        <p
          class="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--color-accent)]"
        >
          {{ t('landing.howItWorks.title') }}
        </p>
        <h2
          class="mx-auto mt-3 max-w-2xl text-3xl font-bold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
        >
          {{ t('landing.howItWorks.heading') }}
        </h2>
        <p class="mx-auto mt-4 max-w-xl text-base text-[color:var(--color-text-secondary)]">
          {{ t('landing.howItWorks.subtitle') }}
        </p>
      </div>

      <div class="mt-14 grid gap-5 md:grid-cols-3">
        <div
          v-for="(step, idx) in steps"
          :key="step.n"
          class="scroll-animate rounded-2xl border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] p-7 shadow-[var(--shadow-glass-1)]"
          :class="`scroll-animate-delay-${idx + 1}`"
        >
          <span
            class="flex h-12 w-12 items-center justify-center rounded-xl bg-[color:var(--color-accent-soft)] text-lg font-bold text-[color:var(--color-accent)]"
          >
            {{ step.n }}
          </span>
          <h3 class="mt-6 text-lg font-semibold text-[color:var(--color-text-primary)]">
            {{ step.title }}
          </h3>
          <p class="mt-2 text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
            {{ step.desc }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
