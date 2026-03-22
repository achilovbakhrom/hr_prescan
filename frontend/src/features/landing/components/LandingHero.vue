<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()
</script>

<template>
  <section class="relative overflow-hidden px-6 py-24 sm:py-32 lg:py-40">
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/40 to-indigo-50/60"></div>
    <!-- Animated floating shapes -->
    <div class="absolute -top-32 right-1/4 h-[500px] w-[500px] rounded-full bg-blue-200/20 blur-3xl animate-float"></div>
    <div class="absolute -bottom-32 left-1/4 h-[400px] w-[400px] rounded-full bg-indigo-200/20 blur-3xl animate-float-delayed"></div>
    <div class="absolute right-10 top-1/3 h-48 w-48 rounded-full bg-violet-200/15 blur-2xl animate-float-delayed"></div>

    <div class="relative mx-auto max-w-5xl text-center">
      <!-- Badge -->
      <div class="scroll-animate mb-8 inline-flex items-center gap-2 rounded-full border border-blue-200/60 bg-blue-50/80 px-4 py-1.5 text-sm font-medium text-blue-700 backdrop-blur-sm">
        <i class="pi pi-sparkles text-xs"></i> {{ t('landing.badge.poweredBy') }}
      </div>

      <!-- Headline -->
      <h1 class="scroll-animate mb-6 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl xl:text-7xl">
        {{ t('landing.hero.title') }}
      </h1>

      <!-- Subtitle -->
      <p class="scroll-animate mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-gray-500 sm:text-xl">
        {{ t('landing.hero.subtitle') }}
      </p>

      <!-- CTAs -->
      <div class="scroll-animate flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
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

      <!-- Trust signals -->
      <p class="scroll-animate mt-5 text-sm text-gray-400">
        {{ t('landing.promo.noCreditCard') }} &middot; {{ t('landing.promo.freeTrial') }}
      </p>

      <!-- Hero illustration: stylized dashboard mockup -->
      <div class="scroll-animate scroll-animate-delay-2 mx-auto mt-16 max-w-3xl">
        <div class="relative rounded-2xl border border-gray-200/60 bg-white/80 p-1.5 shadow-2xl shadow-blue-900/5 backdrop-blur-sm">
          <!-- Browser chrome bar -->
          <div class="flex items-center gap-1.5 rounded-t-xl bg-gray-100 px-4 py-2.5">
            <div class="h-2.5 w-2.5 rounded-full bg-red-300"></div>
            <div class="h-2.5 w-2.5 rounded-full bg-amber-300"></div>
            <div class="h-2.5 w-2.5 rounded-full bg-green-300"></div>
            <div class="ml-3 h-5 w-48 rounded-md bg-gray-200"></div>
          </div>
          <!-- Dashboard content mockup -->
          <div class="space-y-3 rounded-b-xl bg-gradient-to-b from-slate-50 to-white p-5">
            <!-- Top stat cards -->
            <div class="grid grid-cols-4 gap-2.5">
              <div class="rounded-lg bg-white p-3 shadow-sm ring-1 ring-gray-100">
                <div class="mb-1.5 h-2 w-10 rounded bg-gray-200"></div>
                <div class="h-4 w-8 rounded bg-blue-500"></div>
              </div>
              <div class="rounded-lg bg-white p-3 shadow-sm ring-1 ring-gray-100">
                <div class="mb-1.5 h-2 w-12 rounded bg-gray-200"></div>
                <div class="h-4 w-10 rounded bg-emerald-500"></div>
              </div>
              <div class="rounded-lg bg-white p-3 shadow-sm ring-1 ring-gray-100">
                <div class="mb-1.5 h-2 w-8 rounded bg-gray-200"></div>
                <div class="h-4 w-6 rounded bg-amber-500"></div>
              </div>
              <div class="rounded-lg bg-white p-3 shadow-sm ring-1 ring-gray-100">
                <div class="mb-1.5 h-2 w-14 rounded bg-gray-200"></div>
                <div class="h-4 w-12 rounded bg-violet-500"></div>
              </div>
            </div>
            <!-- Chat/table mockup rows -->
            <div class="space-y-2">
              <div class="flex items-center gap-3 rounded-lg bg-white p-3 ring-1 ring-gray-100">
                <div class="h-8 w-8 shrink-0 rounded-full bg-blue-100"></div>
                <div class="flex-1 space-y-1">
                  <div class="h-2.5 w-32 rounded bg-gray-200"></div>
                  <div class="h-2 w-48 rounded bg-gray-100"></div>
                </div>
                <div class="h-6 w-14 rounded-full bg-emerald-100"></div>
              </div>
              <div class="flex items-center gap-3 rounded-lg bg-white p-3 ring-1 ring-gray-100">
                <div class="h-8 w-8 shrink-0 rounded-full bg-indigo-100"></div>
                <div class="flex-1 space-y-1">
                  <div class="h-2.5 w-28 rounded bg-gray-200"></div>
                  <div class="h-2 w-40 rounded bg-gray-100"></div>
                </div>
                <div class="h-6 w-14 rounded-full bg-blue-100"></div>
              </div>
              <div class="flex items-center gap-3 rounded-lg bg-white p-3 ring-1 ring-gray-100">
                <div class="h-8 w-8 shrink-0 rounded-full bg-amber-100"></div>
                <div class="flex-1 space-y-1">
                  <div class="h-2.5 w-36 rounded bg-gray-200"></div>
                  <div class="h-2 w-44 rounded bg-gray-100"></div>
                </div>
                <div class="h-6 w-14 rounded-full bg-amber-100"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
