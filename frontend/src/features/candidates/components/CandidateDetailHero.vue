<script setup lang="ts">
/**
 * CandidateDetailHero — Figma candidate detail hero: avatar, name + status
 * pill, applied-for + meta, an action-bar slot, and a large overall-score ring.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import type { Application } from '../types/candidate.types'

const props = defineProps<{
  candidate: Application
  overallScore: number | null
}>()

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
const R = 52
const CIRC = 2 * Math.PI * R

const initials = computed(() =>
  (props.candidate.candidateName || '?')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join(''),
)
const statusColor = computed(() => STATUS[props.candidate.status] ?? '#9a98ad')
const scoreOutOf10 = computed(() =>
  props.overallScore == null ? null : Math.round((props.overallScore / 10) * 10) / 10,
)
const tier = computed(() => {
  const s = props.overallScore
  if (s == null) return { label: '—', color: 'var(--color-text-muted)' }
  if (s >= 80) return { label: t('candidates.scoreTier.strong'), color: '#34d399' }
  if (s >= 65) return { label: t('candidates.scoreTier.good'), color: 'var(--color-accent)' }
  return { label: t('candidates.scoreTier.weak'), color: '#f87171' }
})
const appliedDate = computed(() => new Date(props.candidate.createdAt).toLocaleDateString())
</script>

<template>
  <GlassCard>
    <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
      <!-- Left: avatar + info + actions -->
      <div class="flex min-w-0 flex-1 items-start gap-5">
        <div
          class="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-2xl font-bold text-[color:var(--color-accent)] sm:h-24 sm:w-24"
        >
          {{ initials }}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-3">
            <h1 class="truncate text-2xl font-bold text-[color:var(--color-text-primary)]">
              {{ candidate.candidateName }}
            </h1>
            <span
              class="rounded-full px-2.5 py-1 text-xs font-medium"
              :style="{
                color: statusColor,
                background: `color-mix(in srgb, ${statusColor} 16%, transparent)`,
              }"
            >
              {{ t(`candidates.status.${candidate.status}`) }}
            </span>
          </div>
          <p class="mt-1.5 text-sm text-[color:var(--color-text-secondary)]">
            {{ t('candidates.appliedFor') }} · {{ candidate.vacancyTitle }}
          </p>
          <div
            class="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm text-[color:var(--color-text-muted)]"
          >
            <span class="inline-flex items-center gap-1.5">
              <i class="pi pi-envelope text-xs"></i>{{ candidate.candidateEmail }}
            </span>
            <span class="inline-flex items-center gap-1.5">
              <i class="pi pi-calendar text-xs"></i>{{ appliedDate }}
            </span>
          </div>
          <div class="mt-4">
            <slot name="actions" />
          </div>
        </div>
      </div>

      <!-- Right: overall score ring -->
      <div class="flex shrink-0 flex-col items-center gap-1">
        <div class="relative h-[120px] w-[120px]">
          <svg width="120" height="120" viewBox="0 0 120 120">
            <circle
              cx="60"
              cy="60"
              :r="R"
              fill="none"
              stroke="currentColor"
              stroke-width="6"
              class="text-[color:var(--color-border-soft)]"
            />
            <circle
              v-if="scoreOutOf10 !== null"
              cx="60"
              cy="60"
              :r="R"
              fill="none"
              :stroke="tier.color"
              stroke-width="6"
              stroke-linecap="round"
              :stroke-dasharray="CIRC"
              :stroke-dashoffset="CIRC * (1 - (overallScore ?? 0) / 100)"
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="font-mono text-3xl font-bold text-[color:var(--color-text-primary)]">
              {{ scoreOutOf10 === null ? '—' : scoreOutOf10.toFixed(1) }}
            </span>
            <span class="text-xs text-[color:var(--color-text-muted)]">/ 10</span>
          </div>
        </div>
        <p class="text-sm font-semibold" :style="{ color: tier.color }">{{ tier.label }}</p>
      </div>
    </div>
  </GlassCard>
</template>
