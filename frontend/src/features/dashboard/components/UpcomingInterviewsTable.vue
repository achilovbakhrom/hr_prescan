<script setup lang="ts">
/** Upcoming interviews — glass card list with avatar + time chip (Figma dashboard rail). */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { UpcomingInterview } from '../types/dashboard.types'

defineProps<{ interviews: UpcomingInterview[] }>()

const { t } = useI18n()
const router = useRouter()

function initials(name: string): string {
  return name
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
function timeLabel(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}
function open(i: UpcomingInterview): void {
  router.push({ name: ROUTE_NAMES.INTERVIEW_DETAIL, params: { id: i.id } })
}
</script>

<template>
  <GlassCard class="overflow-hidden p-0">
    <div class="px-5 py-4">
      <h3 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ t('dashboard.upcomingInterviews') }}
      </h3>
    </div>

    <button
      v-for="i in interviews"
      :key="i.id"
      type="button"
      class="flex w-full items-center gap-3 border-t border-[color:var(--color-border-soft)] px-5 py-3 text-left transition-colors hover:bg-[color:var(--color-surface-raised)]"
      @click="open(i)"
    >
      <span
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-xs font-semibold text-[color:var(--color-accent)]"
      >
        {{ initials(i.candidateName) }}
      </span>
      <span class="flex min-w-0 flex-1 flex-col">
        <span class="truncate text-sm font-medium text-[color:var(--color-text-primary)]">
          {{ i.candidateName }}
        </span>
        <span class="truncate text-xs text-[color:var(--color-text-muted)]">
          {{ i.vacancyTitle }}
        </span>
      </span>
      <span
        class="shrink-0 rounded-lg bg-[color:var(--color-accent-soft)] px-2.5 py-1 font-mono text-xs font-medium text-[color:var(--color-accent)]"
      >
        {{ timeLabel(i.createdAt) }}
      </span>
    </button>

    <div
      v-if="interviews.length === 0"
      class="border-t border-[color:var(--color-border-soft)] px-5 py-8 text-center text-sm text-[color:var(--color-text-muted)]"
    >
      {{ t('dashboard.noUpcomingInterviews') }}
    </div>
  </GlassCard>
</template>
