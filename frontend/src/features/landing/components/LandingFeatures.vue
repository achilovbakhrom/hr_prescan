<script setup lang="ts">
/**
 * LandingFeatures — 4 GlassCards arranged 1/2/4 columns.
 * Uses the existing scroll-animate observer on each card with staggered
 * transition-delay (spec §8: cardStagger @ 60ms/item, max 10).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LandingFeatureCard from './LandingFeatureCard.vue'

const { t } = useI18n()

interface Feature {
  icon: string
  title: string
  description: string
  accent: 'ai' | 'celebrate' | 'accent'
}

const features = computed<Feature[]>(() => [
  {
    icon: 'pi pi-sparkles',
    title: t('landing.features.aiPrescanning'),
    description: t('landing.features.aiPrescanningDesc'),
    accent: 'ai',
  },
  {
    icon: 'pi pi-video',
    title: t('landing.features.aiInterviews'),
    description: t('landing.features.aiInterviewsDesc'),
    accent: 'accent',
  },
  {
    icon: 'pi pi-chart-bar',
    title: t('landing.features.smartScoring'),
    description: t('landing.features.smartScoringDesc'),
    accent: 'celebrate',
  },
  {
    icon: 'pi pi-shield',
    title: t('landing.features.antiCheating'),
    description: t('landing.features.antiCheatingDesc'),
    accent: 'ai',
  },
])
</script>

<template>
  <section id="features" class="px-4 py-24 sm:px-6 md:py-32">
    <div class="mx-auto max-w-7xl">
      <div class="scroll-animate mb-14 text-center sm:mb-20">
        <h2
          class="mb-4 text-4xl font-semibold tracking-tight text-[color:var(--color-text-primary)] md:text-5xl"
        >
          {{ t('landing.features.title') }}
        </h2>
        <p
          class="mx-auto max-w-2xl text-base leading-relaxed text-[color:var(--color-text-secondary)] md:text-lg"
        >
          {{ t('landing.features.subtitle') }}
        </p>
      </div>

      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="(feature, idx) in features"
          :key="feature.title"
          class="scroll-animate"
          :class="`scroll-animate-delay-${(idx % 4) + 1}`"
        >
          <LandingFeatureCard
            :icon="feature.icon"
            :title="feature.title"
            :description="feature.description"
            :accent="feature.accent"
          />
        </div>
      </div>
    </div>
  </section>
</template>
