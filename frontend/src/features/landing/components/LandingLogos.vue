<script setup lang="ts">
/** LandingLogos — Figma "trusted by teams at" logo strip. */
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const logos = ['Nimbus', 'Vertex', 'Quanta', 'Lumen', 'Orbit']
</script>

<template>
  <section class="px-4 py-10 sm:px-6">
    <div class="mx-auto max-w-5xl text-center">
      <p
        class="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
      >
        {{ t('landing.trust.label') }}
      </p>
      <div
        class="mt-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-4 text-[color:var(--color-text-secondary)]"
      >
        <span v-for="logo in logos" :key="logo" class="text-lg font-semibold opacity-60">
          {{ logo }}
        </span>
      </div>
    </div>
  </section>
</template>
