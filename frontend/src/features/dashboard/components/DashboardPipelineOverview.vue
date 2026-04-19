<script setup lang="ts">
/**
 * DashboardPipelineOverview — center column card showing vacancies + applicants.
 * Constellation-style node rows: each row is a vacancy with a status pill and
 * a small applicant-count cluster. Solid data rows inside the glass card.
 *
 * Spec: docs/design/spec.md §9 (dashboard).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Vacancy } from '@/features/vacancies/types/vacancy.types'

interface Props {
  vacancies: Vacancy[]
}

const props = defineProps<Props>()
const { t } = useI18n()
const router = useRouter()

interface Row {
  id: string
  title: string
  status: Vacancy['status']
  applicantCount: number
}

const rows = computed<Row[]>(() =>
  [...props.vacancies]
    .sort((a, b) => {
      const order = { published: 0, draft: 1, paused: 2, archived: 3 } as const
      return (order[a.status] ?? 9) - (order[b.status] ?? 9)
    })
    .slice(0, 6)
    .map((v) => ({
      id: v.id,
      title: v.title,
      status: v.status,
      applicantCount: v.candidatesTotal ?? 0,
    })),
)

function statusBadgeClass(status: Vacancy['status']): string {
  switch (status) {
    case 'published':
      return 'bg-[color:color-mix(in_srgb,var(--color-success)_15%,transparent)] text-[color:var(--color-success)]'
    case 'draft':
      return 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
    case 'paused':
      return 'bg-[color:color-mix(in_srgb,var(--color-warning)_18%,transparent)] text-[color:var(--color-warning)]'
    case 'archived':
      return 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)] line-through opacity-70'
    default:
      return 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
  }
}

function goTo(id: string): void {
  router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })
}

// Width percentage for the applicant-count progress bar.
// Normalized against the largest row so the bar always shows relative scale.
const maxCount = computed(() => Math.max(1, ...rows.value.map((r) => r.applicantCount)))
function barWidth(count: number): string {
  return `${Math.max(4, Math.round((count / maxCount.value) * 100))}%`
}
</script>

<template>
  <GlassCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h2
          class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('dashboard.pipelineOverview') }}
        </h2>
        <button
          type="button"
          class="font-mono text-[11px] text-[color:var(--color-accent)] hover:underline"
          @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
        >
          {{ t('common.viewAll') }}
        </button>
      </div>
    </template>

    <div v-if="rows.length" class="flex flex-col gap-2">
      <div
        v-for="row in rows"
        :key="row.id"
        class="group flex cursor-pointer items-center gap-4 rounded-[--radius-sm] bg-[color:var(--color-surface-raised)] px-4 py-3 transition-colors hover:bg-[color:var(--color-surface-sunken)]"
        @click="goTo(row.id)"
      >
        <!-- Node dot -->
        <span
          class="h-2.5 w-2.5 shrink-0 rounded-full"
          :class="{
            'bg-[color:var(--color-success)]': row.status === 'published',
            'bg-[color:var(--color-text-muted)]':
              row.status === 'draft' || row.status === 'archived',
            'bg-[color:var(--color-warning)]': row.status === 'paused',
          }"
        />

        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <p
              class="truncate text-sm font-medium text-[color:var(--color-text-primary)]"
              :title="row.title"
            >
              {{ row.title }}
            </p>
            <span
              class="shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
              :class="statusBadgeClass(row.status)"
            >
              {{ t(`vacancies.status.${row.status}`) }}
            </span>
          </div>

          <!-- Applicant count bar + label -->
          <div class="mt-1.5 flex items-center gap-2">
            <div
              class="relative h-1.5 flex-1 overflow-hidden rounded-full bg-[color:var(--color-border-soft)]"
            >
              <div
                class="absolute left-0 top-0 h-full rounded-full bg-[color:var(--color-accent-ai)]"
                :style="{ width: barWidth(row.applicantCount) }"
              ></div>
            </div>
            <span
              class="shrink-0 font-mono text-xs tabular-nums text-[color:var(--color-text-secondary)]"
            >
              {{ row.applicantCount }}
              <span class="text-[color:var(--color-text-muted)]">{{
                t('dashboard.applicants')
              }}</span>
            </span>
          </div>
        </div>

        <i
          class="pi pi-chevron-right text-xs text-[color:var(--color-text-muted)] transition-transform group-hover:translate-x-0.5"
        ></i>
      </div>
    </div>

    <div
      v-else
      class="flex flex-col items-center py-10 text-center text-[color:var(--color-text-muted)]"
    >
      <i class="pi pi-briefcase mb-2 text-2xl"></i>
      <p class="text-sm">{{ t('common.noData') }}</p>
    </div>
  </GlassCard>
</template>
