<script setup lang="ts">
/** Recent candidates — glass card with avatar rows, score and status pill (Figma dashboard). */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { RecentApplication } from '../types/dashboard.types'

defineProps<{ applications: RecentApplication[] }>()

const { t } = useI18n()
const router = useRouter()

const STATUS: Record<string, string> = {
  applied: '#8a8fa6',
  prescanned: '#5b9bf0',
  interviewed: '#a78bfa',
  shortlisted: '#2dd4bf',
  hired: '#34d399',
  rejected: '#f87171',
}

function initials(name: string): string {
  return name
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
function statusColor(s: string): string {
  return STATUS[s] ?? '#8a8fa6'
}
function scoreColor(v: number | null): string {
  if (v == null) return 'var(--color-text-muted)'
  if (v >= 80) return '#34d399'
  if (v >= 60) return 'var(--color-accent)'
  if (v >= 40) return '#fbbf24'
  return '#f87171'
}
/** Backend scores are 0–100; the design shows them on a /10 scale. */
function scoreOutOf10(v: number | null): string {
  return v == null ? '—' : (v / 10).toFixed(1)
}
function open(app: RecentApplication): void {
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id: app.id } })
}
</script>

<template>
  <GlassCard class="overflow-hidden p-0">
    <div class="flex items-center justify-between px-5 py-4">
      <h3 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ t('dashboard.recentApplications') }}
      </h3>
      <button
        type="button"
        class="text-sm font-medium text-[color:var(--color-accent)] hover:underline"
        @click="router.push({ name: ROUTE_NAMES.CANDIDATE_LIST })"
      >
        {{ t('common.viewAll') }}
      </button>
    </div>

    <div
      class="grid grid-cols-[1fr_auto_auto] gap-4 border-y border-[color:var(--color-border-soft)] px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-[color:var(--color-text-muted)] sm:grid-cols-[1.6fr_1fr_auto_auto]"
    >
      <span>{{ t('dashboard.table.candidate') }}</span>
      <span class="hidden sm:block">{{ t('dashboard.table.vacancy') }}</span>
      <span class="text-right">{{ t('dashboard.table.score') }}</span>
      <span class="text-right">{{ t('common.status') }}</span>
    </div>

    <button
      v-for="app in applications"
      :key="app.id"
      type="button"
      class="grid w-full grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-[color:var(--color-border-soft)] px-5 py-3 text-left transition-colors last:border-b-0 hover:bg-[color:var(--color-surface-raised)] sm:grid-cols-[1.6fr_1fr_auto_auto]"
      @click="open(app)"
    >
      <span class="flex min-w-0 items-center gap-3">
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-xs font-semibold text-[color:var(--color-accent)]"
        >
          {{ initials(app.candidateName) }}
        </span>
        <span class="truncate text-sm font-medium text-[color:var(--color-text-primary)]">
          {{ app.candidateName }}
        </span>
      </span>
      <span class="hidden truncate text-sm text-[color:var(--color-text-secondary)] sm:block">
        {{ app.vacancyTitle }}
      </span>
      <span class="text-right text-sm font-semibold" :style="{ color: scoreColor(app.matchScore) }">
        {{ scoreOutOf10(app.matchScore) }}
      </span>
      <span class="flex justify-end">
        <span
          class="rounded-full px-2.5 py-0.5 text-xs font-medium"
          :style="{
            color: statusColor(app.status),
            background: `color-mix(in srgb, ${statusColor(app.status)} 16%, transparent)`,
          }"
        >
          {{ t(`candidates.status.${app.status}`) }}
        </span>
      </span>
    </button>

    <div
      v-if="applications.length === 0"
      class="px-5 py-10 text-center text-sm text-[color:var(--color-text-muted)]"
    >
      {{ t('dashboard.noRecentApplications') }}
    </div>
  </GlassCard>
</template>
