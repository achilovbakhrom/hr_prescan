<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface PipelineStep {
  icon: string
  title: string
  description: string
  color: string
  bg: string
}

const pipelineSteps = computed<PipelineStep[]>(() => [
  {
    icon: 'pi pi-send',
    title: t('landing.pipeline.step1'),
    description: t('landing.pipeline.step1Desc'),
    color: 'text-blue-600',
    bg: 'bg-blue-50',
  },
  {
    icon: 'pi pi-comments',
    title: t('landing.pipeline.step2'),
    description: t('landing.pipeline.step2Desc'),
    color: 'text-indigo-600',
    bg: 'bg-indigo-50',
  },
  {
    icon: 'pi pi-video',
    title: t('landing.pipeline.step3'),
    description: t('landing.pipeline.step3Desc'),
    color: 'text-violet-600',
    bg: 'bg-violet-50',
  },
  {
    icon: 'pi pi-chart-bar',
    title: t('landing.pipeline.step4'),
    description: t('landing.pipeline.step4Desc'),
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
  },
  {
    icon: 'pi pi-check-circle',
    title: t('landing.pipeline.step5'),
    description: t('landing.pipeline.step5Desc'),
    color: 'text-green-600',
    bg: 'bg-green-50',
  },
])
</script>

<template>
  <section id="how-it-works" class="bg-gray-50/80 dark:bg-gray-900/40 px-6 py-24">
    <div class="mx-auto max-w-6xl">
      <div class="scroll-animate mb-16 text-center">
        <h2 class="mb-3 text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          {{ t('landing.pipeline.title') }}
        </h2>
        <p class="mx-auto max-w-xl text-gray-500">
          {{ t('landing.pipeline.subtitle') }}
        </p>
      </div>

      <!-- Desktop: horizontal flow -->
      <div class="scroll-animate hidden lg:block">
        <div class="flex items-start">
          <template v-for="(step, idx) in pipelineSteps" :key="step.title">
            <div class="flex flex-1 flex-col items-center text-center">
              <div
                class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl transition-transform duration-300 hover:scale-110"
                :class="[step.bg, step.color]"
              >
                <i :class="step.icon" class="text-2xl"></i>
              </div>
              <h3 class="mb-1.5 text-sm font-semibold text-gray-900 dark:text-white">{{ step.title }}</h3>
              <p class="max-w-[160px] text-xs leading-relaxed text-gray-500 dark:text-gray-300">
                {{ step.description }}
              </p>
            </div>
            <!-- Connector arrow -->
            <div v-if="idx < pipelineSteps.length - 1" class="mt-6 flex shrink-0 items-center px-1">
              <div class="h-px w-8 bg-gray-300"></div>
              <i class="pi pi-angle-right text-xs text-gray-400"></i>
            </div>
          </template>
        </div>
      </div>

      <!-- Mobile: vertical flow -->
      <div class="scroll-animate lg:hidden">
        <div class="relative ml-6 border-l-2 border-gray-200 dark:border-gray-700 pl-8">
          <div v-for="step in pipelineSteps" :key="step.title" class="relative pb-10 last:pb-0">
            <!-- Dot on the timeline -->
            <div
              class="absolute -left-[41px] flex h-10 w-10 items-center justify-center rounded-xl"
              :class="[step.bg, step.color]"
            >
              <i :class="step.icon" class="text-lg"></i>
            </div>
            <div class="pt-0.5">
              <h3 class="mb-1 text-base font-semibold text-gray-900 dark:text-white">{{ step.title }}</h3>
              <p class="text-sm leading-relaxed text-gray-500 dark:text-gray-300">{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
