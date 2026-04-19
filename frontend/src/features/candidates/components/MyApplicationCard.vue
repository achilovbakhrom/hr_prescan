<script setup lang="ts">
/**
 * MyApplicationCard — candidate's view of one application.
 * GlassCard with status pill, vacancy meta, match score, and CTA.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import ApplicationStatusBadge from './ApplicationStatusBadge.vue'
import type { Application } from '../types/candidate.types'

const props = defineProps<{
  application: Application
}>()

const emit = defineEmits<{
  open: [id: string]
}>()

const { t } = useI18n()

const initials = computed(() => {
  const chars = (props.application.companyName || props.application.vacancyTitle || 'V')
    .split(/\s+/)
    .map((s) => s[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
  return chars || 'V'
})

const formattedDate = computed(() =>
  new Date(props.application.createdAt).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }),
)

const ctaLabel = computed(() => {
  if (props.application.status === 'applied')
    return t('candidates.myApplication.startPrescan') || 'Start prescan'
  if (props.application.status === 'prescanned')
    return t('candidates.myApplication.continue') || 'View progress'
  if (props.application.status === 'interviewed' || props.application.status === 'shortlisted')
    return t('candidates.myApplication.viewInterview') || 'View interview'
  return t('common.view') || 'View'
})
</script>

<template>
  <GlassSurface
    level="1"
    interactive
    as="button"
    class="my-app-card relative flex w-full flex-col gap-4 rounded-lg p-5 text-left"
    @click="emit('open', application.id)"
  >
    <div class="flex items-start gap-3">
      <div
        class="flex h-11 w-11 flex-none items-center justify-center rounded-md bg-[color:var(--color-accent-soft)] font-mono text-sm font-semibold text-[color:var(--color-accent)]"
      >
        {{ initials }}
      </div>
      <div class="min-w-0 flex-1">
        <h3 class="truncate text-base font-semibold text-[color:var(--color-text-primary)]">
          {{ application.vacancyTitle }}
        </h3>
        <p
          v-if="application.companyName"
          class="mt-0.5 flex items-center gap-1.5 truncate text-sm text-[color:var(--color-text-secondary)]"
        >
          <i class="pi pi-building text-xs"></i>
          {{ application.companyName }}
        </p>
      </div>
      <ApplicationStatusBadge :status="application.status" />
    </div>

    <div
      class="flex items-center justify-between gap-3 rounded-md border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-sunken)] px-3 py-2.5"
    >
      <div class="flex flex-col">
        <span class="text-[11px] uppercase tracking-wider text-[color:var(--color-text-muted)]">
          {{ t('candidates.matchScore') }}
        </span>
        <span
          v-if="application.matchScore !== null"
          class="font-mono text-lg font-semibold text-[color:var(--color-accent-ai)]"
        >
          {{ application.matchScore }}%
        </span>
        <span v-else class="text-xs text-[color:var(--color-text-muted)]">
          {{ t('candidates.myApplication.cvBeingAnalyzed') }}
        </span>
      </div>
      <div class="flex flex-col items-end">
        <span class="text-[11px] uppercase tracking-wider text-[color:var(--color-text-muted)]">
          {{ t('common.createdAt') }}
        </span>
        <span class="font-mono text-xs text-[color:var(--color-text-secondary)]">
          {{ formattedDate }}
        </span>
      </div>
    </div>

    <div class="flex items-center justify-end">
      <Button
        :label="ctaLabel"
        icon="pi pi-arrow-right"
        icon-pos="right"
        size="small"
        severity="secondary"
        outlined
      />
    </div>
  </GlassSurface>
</template>

<style scoped>
.my-app-card {
  transition:
    transform 240ms var(--ease-ios),
    box-shadow 240ms var(--ease-ios);
}
@media (prefers-reduced-motion: reduce) {
  .my-app-card {
    transition: none;
  }
}
</style>
