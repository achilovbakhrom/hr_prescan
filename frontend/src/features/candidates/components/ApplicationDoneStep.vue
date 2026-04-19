<script setup lang="ts">
/**
 * ApplicationDoneStep — celebrate confirmation shown after the candidate
 * finishes the AI prescan. Extracted to keep ApplicationFormPage small.
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'

const { t } = useI18n()
</script>

<template>
  <GlassCard accent="celebrate" class="py-10 text-center">
    <div
      class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
    >
      <i class="pi pi-check-circle text-3xl text-[color:var(--color-accent-celebrate)]"></i>
    </div>
    <h2 class="mb-2 text-xl font-semibold text-[color:var(--color-text-primary)]">
      {{ t('candidates.application.prescanComplete') }}
    </h2>
    <p class="mb-6 text-sm text-[color:var(--color-text-secondary)]">
      {{ t('candidates.application.prescanCompleteHint') }}
    </p>
    <RouterLink to="/jobs">
      <Button :label="t('candidates.application.browseVacancies')" icon="pi pi-briefcase" />
    </RouterLink>
  </GlassCard>
</template>
