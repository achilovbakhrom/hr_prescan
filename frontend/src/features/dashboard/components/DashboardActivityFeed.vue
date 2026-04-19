<script setup lang="ts">
/**
 * DashboardActivityFeed — rail card showing recent activity.
 * Glass rows with icon + action line + timestamp (Geist Mono).
 *
 * Spec: docs/design/spec.md §9 (dashboard rail).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import GlassCard from '@/shared/components/GlassCard.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Interview } from '@/features/interviews/types/interview.types'

interface Props {
  interviews: Interview[]
}

const props = defineProps<Props>()
const { t } = useI18n()
const router = useRouter()

interface FeedItem {
  id: string
  iconClass: string
  iconBg: string
  title: string
  subtitle: string
  timestamp: string
  onClick: () => void
}

function formatTime(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffH = Math.floor(diffMs / 3600000)
  const diffD = Math.floor(diffMs / 86400000)
  if (diffMin < 1) return 'now'
  if (diffMin < 60) return `${diffMin}m`
  if (diffH < 24) return `${diffH}h`
  if (diffD < 7) return `${diffD}d`
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

const items = computed<FeedItem[]>(() =>
  props.interviews.slice(0, 6).map((iv) => {
    const isCompleted = iv.status === 'completed'
    return {
      id: iv.id,
      iconClass: isCompleted ? 'pi pi-check-circle' : 'pi pi-calendar',
      iconBg: isCompleted
        ? 'bg-[color:color-mix(in_srgb,var(--color-success)_15%,transparent)] text-[color:var(--color-success)]'
        : 'bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)]',
      title: iv.candidateName ?? t('dashboard.table.candidate'),
      subtitle: iv.vacancyTitle ?? '',
      timestamp: formatTime(new Date(iv.createdAt)),
      onClick: () => router.push({ name: ROUTE_NAMES.INTERVIEW_DETAIL, params: { id: iv.id } }),
    }
  }),
)
</script>

<template>
  <GlassCard class="flex h-full flex-col">
    <template #header>
      <div class="flex items-center justify-between">
        <h3
          class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('dashboard.recentActivity') }}
        </h3>
        <button
          type="button"
          class="font-mono text-[11px] text-[color:var(--color-accent)] hover:underline"
          @click="router.push({ name: ROUTE_NAMES.INTERVIEW_LIST })"
        >
          {{ t('common.viewAll') }}
        </button>
      </div>
    </template>

    <ul v-if="items.length" class="flex flex-col gap-1">
      <li
        v-for="item in items"
        :key="item.id"
        class="group flex cursor-pointer items-center gap-3 rounded-md px-2 py-2 transition-colors hover:bg-[color:var(--color-surface-sunken)]"
        @click="item.onClick"
      >
        <div
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
          :class="item.iconBg"
        >
          <i :class="item.iconClass" class="text-sm"></i>
        </div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-[color:var(--color-text-primary)]">
            {{ item.title }}
          </p>
          <p class="truncate text-xs text-[color:var(--color-text-muted)]">
            {{ item.subtitle }}
          </p>
        </div>
        <span class="shrink-0 font-mono text-[11px] text-[color:var(--color-text-muted)]">
          {{ item.timestamp }}
        </span>
      </li>
    </ul>

    <div
      v-else
      class="flex flex-col items-center justify-center py-8 text-center text-[color:var(--color-text-muted)]"
    >
      <i class="pi pi-inbox mb-2 text-2xl"></i>
      <p class="text-xs">{{ t('dashboard.noUpcomingInterviews') }}</p>
    </div>
  </GlassCard>
</template>
