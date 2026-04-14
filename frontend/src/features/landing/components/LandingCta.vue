<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()
</script>

<template>
  <section id="pricing" class="relative overflow-hidden px-6 py-24">
    <div class="absolute inset-0 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700"></div>
    <!-- Decorative shapes -->
    <div class="absolute -left-20 -top-20 h-80 w-80 rounded-full bg-white/5 blur-2xl"></div>
    <div class="absolute -bottom-20 -right-20 h-80 w-80 rounded-full bg-white/5 blur-2xl"></div>

    <div class="relative mx-auto max-w-3xl text-center">
      <h2 class="scroll-animate mb-4 text-3xl font-bold text-white sm:text-4xl">
        {{ t('landing.cta.title') }}
      </h2>
      <p class="scroll-animate mx-auto mb-10 max-w-lg text-lg text-blue-100">
        {{ t('landing.cta.subtitle') }}
      </p>
      <div
        class="scroll-animate flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4"
      >
        <Button
          :label="t('landing.cta.startFree')"
          icon="pi pi-arrow-right"
          icon-pos="right"
          size="large"
          severity="contrast"
          class="w-full sm:w-auto"
          @click="router.push({ name: ROUTE_NAMES.COMPANY_REGISTER })"
        />
        <Button
          :label="t('landing.cta.viewPricing')"
          text
          size="large"
          class="w-full !text-white hover:!text-blue-100 sm:w-auto"
          @click="router.push({ name: ROUTE_NAMES.PRICING })"
        />
      </div>
    </div>
  </section>
</template>
