<script setup lang="ts">
/**
 * ApplicationTimeline — vertical timeline of application events.
 * Preserved statuses: applied → prescanned → interviewed → shortlisted (or rejected).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Application, ApplicationStatus } from '../types/candidate.types'

const props = defineProps<{
  application: Application
}>()

const { t } = useI18n()

const steps: ApplicationStatus[] = ['applied', 'prescanned', 'interviewed', 'shortlisted']

const currentIndex = computed(() => {
  const idx = steps.indexOf(props.application.status)
  return idx
})

const isRejected = computed(() => props.application.status === 'rejected')

interface TimelineItem {
  key: ApplicationStatus
  icon: string
  labelKey: string
  state: 'done' | 'current' | 'pending'
}

const items = computed<TimelineItem[]>(() =>
  steps.map((key, i) => {
    let state: 'done' | 'current' | 'pending' = 'pending'
    if (currentIndex.value >= 0) {
      if (i < currentIndex.value) state = 'done'
      else if (i === currentIndex.value) state = 'current'
    }
    return {
      key,
      icon: iconFor(key),
      labelKey: `candidates.status.${key}`,
      state,
    }
  }),
)

function iconFor(status: ApplicationStatus): string {
  switch (status) {
    case 'applied':
      return 'pi pi-send'
    case 'prescanned':
      return 'pi pi-sparkles'
    case 'interviewed':
      return 'pi pi-microphone'
    case 'shortlisted':
      return 'pi pi-star'
    default:
      return 'pi pi-circle'
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="space-y-3">
    <h2 class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]">
      {{ t('candidates.myApplication.progress') }}
    </h2>

    <div
      v-if="isRejected"
      class="flex items-center gap-3 rounded-md border border-[color:var(--color-danger)] bg-[color:color-mix(in_srgb,var(--color-danger)_10%,transparent)] px-4 py-3"
    >
      <i class="pi pi-times-circle text-lg text-[color:var(--color-danger)]"></i>
      <span class="text-sm font-medium text-[color:var(--color-danger)]">
        {{ t('candidates.status.rejected') }}
      </span>
    </div>

    <ol v-else class="relative flex flex-col gap-0">
      <li
        v-for="(item, i) in items"
        :key="item.key"
        class="relative flex items-start gap-4 pb-5 last:pb-0"
      >
        <!-- connecting line -->
        <span
          v-if="i < items.length - 1"
          class="absolute left-[15px] top-8 bottom-0 w-px"
          :class="
            item.state === 'done'
              ? 'bg-[color:var(--color-accent-ai)]'
              : 'bg-[color:var(--color-border-soft)]'
          "
        ></span>

        <!-- node -->
        <span
          class="relative z-10 flex h-8 w-8 flex-none items-center justify-center rounded-full border text-xs"
          :class="
            item.state === 'done'
              ? 'border-[color:var(--color-accent-ai)] bg-[color:var(--color-accent-ai)] text-white'
              : item.state === 'current'
                ? 'border-[color:var(--color-accent-ai)] bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)] timeline-node--current'
                : 'border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)]'
          "
        >
          <i :class="item.icon"></i>
        </span>

        <!-- content chip -->
        <div
          class="flex-1 rounded-md border px-3 py-2"
          :class="
            item.state === 'current'
              ? 'border-[color:var(--color-accent-ai)] bg-glass-1 border-glass'
              : item.state === 'done'
                ? 'border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)]'
                : 'border-dashed border-[color:var(--color-border-soft)] bg-transparent'
          "
        >
          <div class="flex items-center justify-between gap-2">
            <span
              class="text-sm font-medium"
              :class="
                item.state === 'pending'
                  ? 'text-[color:var(--color-text-muted)]'
                  : 'text-[color:var(--color-text-primary)]'
              "
            >
              {{ t(item.labelKey) }}
            </span>
            <span
              v-if="item.state === 'current' && application.updatedAt"
              class="font-mono text-[11px] text-[color:var(--color-text-muted)]"
            >
              {{ formatDate(application.updatedAt) }}
            </span>
          </div>
        </div>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.timeline-node--current {
  animation: pulse-ring 1800ms var(--ease-ios) infinite;
}
@keyframes pulse-ring {
  0%,
  100% {
    box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-accent-ai) 50%, transparent);
  }
  50% {
    box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-accent-ai) 0%, transparent);
  }
}
@media (prefers-reduced-motion: reduce) {
  .timeline-node--current {
    animation: none;
  }
}
</style>
