<script setup lang="ts">
/**
 * VacancyListGrid — card grid replacing the legacy DataTable.
 * Each card is an interactive GlassSurface; status badge, title, company,
 * stats (applied, posted), and the contextual primary action stack inside.
 * Same emits contract as before (`open`, `delete`, `status-change`).
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import VacancyStatusBadge from './VacancyStatusBadge.vue'
import type { Vacancy, VacancyStatus } from '../types/vacancy.types'

defineProps<{
  vacancies: Vacancy[]
  loading: boolean
}>()

const emit = defineEmits<{
  open: [id: string]
  delete: [event: Event, id: string, title: string]
  statusChange: [event: Event, id: string, status: VacancyStatus]
}>()

const { t } = useI18n()

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<template>
  <!-- Loading skeletons -->
  <div
    v-if="loading"
    class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3"
    aria-busy="true"
  >
    <div
      v-for="n in 6"
      :key="n"
      class="vacancy-card-skeleton h-44 rounded-xl bg-[color:var(--color-surface-raised)]"
    ></div>
  </div>

  <!-- Empty state -->
  <div
    v-else-if="vacancies.length === 0"
    class="flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-[color:var(--color-border-soft)] py-16 text-center"
  >
    <i class="pi pi-briefcase text-3xl text-[color:var(--color-text-muted)]"></i>
    <p class="text-sm text-[color:var(--color-text-muted)]">{{ t('vacancies.noVacancies') }}</p>
  </div>

  <!-- Card grid -->
  <div v-else class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
    <GlassSurface
      v-for="v in vacancies"
      :key="v.id"
      level="1"
      interactive
      :as="'article'"
      class="group flex flex-col gap-3 !rounded-xl p-4"
      role="button"
      tabindex="0"
      @click="emit('open', v.id)"
      @keydown.enter.prevent="emit('open', v.id)"
      @keydown.space.prevent="emit('open', v.id)"
    >
      <!-- Top row: status + delete affordance -->
      <div class="flex items-start justify-between gap-2">
        <VacancyStatusBadge :status="v.status" />
        <button
          v-if="v.status === 'draft' || v.status === 'archived'"
          type="button"
          class="rounded-md p-1.5 text-[color:var(--color-text-muted)] opacity-0 transition-all hover:bg-[color:var(--color-danger)]/10 hover:text-[color:var(--color-danger)] group-hover:opacity-100 focus-visible:opacity-100"
          :aria-label="t('common.delete')"
          @click.stop="emit('delete', $event, v.id, v.title)"
        >
          <i class="pi pi-trash text-sm"></i>
        </button>
      </div>

      <!-- Title + company -->
      <div class="min-h-[3rem]">
        <h3
          class="line-clamp-2 text-base font-semibold leading-snug text-[color:var(--color-text-primary)]"
        >
          {{ v.title }}
        </h3>
        <p
          v-if="v.companyName"
          class="mt-0.5 truncate text-xs text-[color:var(--color-text-muted)]"
        >
          {{ v.companyName }}
        </p>
      </div>

      <!-- Stats row -->
      <div
        class="flex items-center gap-4 border-t border-[color:var(--color-border-soft)] pt-3 text-xs text-[color:var(--color-text-muted)]"
      >
        <span class="inline-flex items-center gap-1.5">
          <i class="pi pi-users text-[0.75rem]"></i>
          <span class="font-medium text-[color:var(--color-text-primary)]">
            {{ v.candidatesTotal ?? 0 }}
          </span>
          <span>{{ t('vacancies.applied').toLowerCase() }}</span>
        </span>
        <span class="inline-flex items-center gap-1.5">
          <i class="pi pi-calendar text-[0.75rem]"></i>
          {{ formatDate(v.createdAt) }}
        </span>
      </div>

      <!-- Contextual primary action -->
      <div class="flex items-center justify-end" @click.stop>
        <Button
          v-if="v.status === 'draft'"
          :label="t('vacancies.actions.publish')"
          icon="pi pi-send"
          size="small"
          @click="emit('statusChange', $event, v.id, 'published')"
        />
        <Button
          v-else-if="v.status === 'paused'"
          :label="t('vacancies.actions.resume')"
          icon="pi pi-play"
          severity="success"
          size="small"
          @click="emit('statusChange', $event, v.id, 'published')"
        />
        <Button
          v-else-if="v.status === 'published'"
          :label="t('vacancies.actions.pause')"
          icon="pi pi-pause"
          severity="warn"
          size="small"
          outlined
          @click="emit('statusChange', $event, v.id, 'paused')"
        />
      </div>
    </GlassSurface>
  </div>
</template>

<style scoped>
.vacancy-card-skeleton {
  position: relative;
  overflow: hidden;
}
.vacancy-card-skeleton::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    color-mix(in oklab, var(--color-surface-overlay, #fff) 28%, transparent),
    transparent
  );
  transform: translateX(-100%);
  animation: vacancy-skel 1.2s ease-in-out infinite;
}
@keyframes vacancy-skel {
  to {
    transform: translateX(100%);
  }
}
</style>
