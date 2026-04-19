<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Feature {
  icon: string
  title: string
  description: string
  gradient: string
}

const features = computed<Feature[]>(() => [
  {
    icon: 'pi pi-comments',
    title: t('landing.features.aiPrescanning'),
    description: t('landing.features.aiPrescanningDesc'),
    gradient: 'from-blue-500 to-blue-600',
  },
  {
    icon: 'pi pi-video',
    title: t('landing.features.aiInterviews'),
    description: t('landing.features.aiInterviewsDesc'),
    gradient: 'from-indigo-500 to-indigo-600',
  },
  {
    icon: 'pi pi-chart-bar',
    title: t('landing.features.smartScoring'),
    description: t('landing.features.smartScoringDesc'),
    gradient: 'from-emerald-500 to-emerald-600',
  },
  {
    icon: 'pi pi-shield',
    title: t('landing.features.antiCheating'),
    description: t('landing.features.antiCheatingDesc'),
    gradient: 'from-amber-500 to-amber-600',
  },
])
</script>

<template>
  <section id="features" class="px-6 py-24">
    <div class="mx-auto max-w-7xl">
      <div class="scroll-animate mb-16 text-center">
        <h2 class="mb-3 text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          {{ t('landing.features.title') }}
        </h2>
        <p class="mx-auto max-w-xl text-gray-500">
          {{ t('landing.features.subtitle') }}
        </p>
      </div>
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="(feature, idx) in features"
          :key="feature.title"
          class="scroll-animate group glass-card rounded-2xl p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-blue-500/10"
          :class="`scroll-animate-delay-${idx + 1}`"
        >
          <div
            class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br text-white transition-shadow duration-300 group-hover:shadow-lg"
            :class="feature.gradient"
          >
            <i :class="feature.icon" class="text-xl"></i>
          </div>
          <h3 class="mb-2 text-lg font-semibold text-gray-900">{{ feature.title }}</h3>
          <p class="text-sm leading-relaxed text-gray-500">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
