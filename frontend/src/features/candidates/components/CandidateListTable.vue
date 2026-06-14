<script setup lang="ts">
/**
 * CandidateListTable — Figma candidate list: avatar + name/email, applied-for,
 * a circular AI-score ring (Strong/Good/Weak), and a colored status pill.
 */
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import type { Application } from '../types/candidate.types'

defineProps<{
  candidates: Application[]
  loading: boolean
  searchQuery: string
  showVacancyColumn?: boolean
}>()

const emit = defineEmits<{ viewDetail: [candidate: Application] }>()

const { t } = useI18n()

const STATUS: Record<string, string> = {
  applied: '#8a8fa6',
  prescanned: '#5b9bf0',
  interviewed: '#a78bfa',
  shortlisted: '#2dd4bf',
  hired: '#34d399',
  rejected: '#f87171',
  expired: '#9a98ad',
  archived: '#9a98ad',
}
const R = 17
const CIRC = 2 * Math.PI * R

function initials(name: string | undefined): string {
  if (!name) return '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join('')
}
function aiScore(c: Application): number | null {
  return c.interviewScore ?? c.prescanningScore ?? null
}
function tier(s: number): { label: string; color: string } {
  if (s >= 8) return { label: t('candidates.scoreTier.strong'), color: '#34d399' }
  if (s >= 6.5) return { label: t('candidates.scoreTier.good'), color: 'var(--color-accent)' }
  return { label: t('candidates.scoreTier.weak'), color: '#9a98ad' }
}
function statusColor(s: string): string {
  return STATUS[s] ?? '#9a98ad'
}
</script>

<template>
  <DataTable
    :value="candidates"
    :loading="loading"
    row-hover
    paginator
    :rows="12"
    :rows-per-page-options="[12, 25, 50]"
    class="cursor-pointer"
    data-key="id"
    @row-click="(e) => emit('viewDetail', e.data)"
  >
    <Column :header="t('dashboard.table.candidate')" sortable sort-field="candidateName">
      <template #body="{ data }">
        <div class="flex items-center gap-3">
          <div
            class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-xs font-semibold text-[color:var(--color-accent)]"
          >
            {{ initials((data as Application).candidateName) }}
          </div>
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold text-[color:var(--color-text-primary)]">
              {{ (data as Application).candidateName }}
            </p>
            <p class="truncate text-xs text-[color:var(--color-text-muted)]">
              {{ (data as Application).candidateEmail }}
            </p>
          </div>
        </div>
      </template>
    </Column>

    <Column
      v-if="showVacancyColumn"
      field="vacancyTitle"
      :header="t('candidates.appliedFor')"
      sortable
    >
      <template #body="{ data }">
        <span class="text-sm text-[color:var(--color-text-secondary)]">{{
          (data as Application).vacancyTitle
        }}</span>
      </template>
    </Column>

    <Column :header="t('candidates.aiScore')" sortable sort-field="prescanningScore">
      <template #body="{ data }">
        <div v-if="aiScore(data as Application) !== null" class="flex items-center gap-3">
          <svg width="44" height="44" viewBox="0 0 44 44" class="shrink-0">
            <circle
              cx="22"
              cy="22"
              :r="R"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
              class="text-[color:var(--color-border-soft)]"
            />
            <circle
              cx="22"
              cy="22"
              :r="R"
              fill="none"
              :stroke="tier(aiScore(data as Application)!).color"
              stroke-width="3"
              stroke-linecap="round"
              :stroke-dasharray="CIRC"
              :stroke-dashoffset="CIRC * (1 - aiScore(data as Application)! / 10)"
              transform="rotate(-90 22 22)"
            />
            <text
              x="22"
              y="22"
              text-anchor="middle"
              dominant-baseline="central"
              class="fill-[color:var(--color-text-primary)] text-[11px] font-bold"
            >
              {{ aiScore(data as Application)!.toFixed(1) }}
            </text>
          </svg>
          <div class="leading-tight">
            <p
              class="text-sm font-semibold"
              :style="{ color: tier(aiScore(data as Application)!).color }"
            >
              {{ tier(aiScore(data as Application)!).label }}
            </p>
            <p class="text-xs text-[color:var(--color-text-muted)]">/ 10</p>
          </div>
        </div>
        <span v-else class="text-xs text-[color:var(--color-text-muted)]">{{
          t('interviews.status.pending')
        }}</span>
      </template>
    </Column>

    <Column :header="t('common.status')">
      <template #body="{ data }">
        <span
          class="rounded-full px-2.5 py-1 text-xs font-medium"
          :style="{
            color: statusColor((data as Application).status),
            background: `color-mix(in srgb, ${statusColor((data as Application).status)} 16%, transparent)`,
          }"
        >
          {{ t(`candidates.status.${(data as Application).status}`) }}
        </span>
      </template>
    </Column>

    <Column header-style="width: 3rem">
      <template #body>
        <i class="pi pi-arrow-right text-xs text-[color:var(--color-text-muted)]"></i>
      </template>
    </Column>

    <template #empty>
      <div class="py-10 text-center text-[color:var(--color-text-muted)]">
        <i class="pi pi-users mb-2 text-3xl"></i>
        <p v-if="searchQuery" class="text-sm">
          {{ t('candidates.noMatchingCandidates', { query: searchQuery }) }}
        </p>
        <p v-else class="text-sm">{{ t('candidates.noCandidates') }}</p>
      </div>
    </template>
  </DataTable>
</template>
