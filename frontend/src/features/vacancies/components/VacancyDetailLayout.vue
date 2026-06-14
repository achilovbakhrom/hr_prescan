<script setup lang="ts">
/**
 * VacancyDetailLayout — Figma vacancy detail: a horizontal stat-cards row
 * (Applicants / Interviewed / Shortlisted / Hired) + a horizontal tab bar,
 * with the active section rendered below via the default slot.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import type { VacancyDetail } from '../types/vacancy.types'

interface TabItem {
  key: string
  label: string
  count?: number | null
}

const props = defineProps<{
  vacancy: VacancyDetail
  active: string
}>()

const emit = defineEmits<{ navigate: [key: string] }>()

const { t } = useI18n()

const stats = computed(() => [
  { label: t('vacancies.applied'), value: props.vacancy.candidatesTotal ?? 0, dot: '#a78bfa' },
  {
    label: t('candidates.status.interviewed'),
    value: props.vacancy.candidatesInterviewed ?? 0,
    dot: '#f472b6',
  },
  {
    label: t('candidates.status.shortlisted'),
    value: props.vacancy.candidatesShortlisted ?? 0,
    dot: '#2dd4bf',
  },
  {
    label: t('candidates.status.hired'),
    value: props.vacancy.candidatesHired ?? 0,
    dot: '#34d399',
  },
])

const tabs = computed<TabItem[]>(() => {
  const list: TabItem[] = [
    { key: 'details', label: t('vacancies.section.details') },
    { key: 'prescanning', label: t('vacancies.form.prescanning') },
  ]
  if (props.vacancy.interviewEnabled) {
    list.push({ key: 'interview', label: t('vacancies.form.interview') })
  }
  list.push({
    key: 'candidates',
    label: t('candidates.title'),
    count: props.vacancy.candidatesTotal ?? 0,
  })
  list.push({ key: 'settings', label: t('nav.settings') })
  return list
})
</script>

<template>
  <div class="space-y-5">
    <!-- Stat cards row -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <GlassCard v-for="s in stats" :key="s.label" class="!p-4">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full" :style="{ background: s.dot }"></span>
          <span class="text-xs text-[color:var(--color-text-muted)]">{{ s.label }}</span>
        </div>
        <p
          class="mt-2 font-mono text-2xl font-semibold tracking-tight text-[color:var(--color-text-primary)]"
        >
          {{ s.value }}
        </p>
      </GlassCard>
    </div>

    <!-- Horizontal tabs -->
    <div class="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="flex shrink-0 items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-colors"
        :class="
          active === tab.key
            ? 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
            : 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]'
        "
        @click="emit('navigate', tab.key)"
      >
        <span>{{ tab.label }}</span>
        <span
          v-if="tab.count != null"
          class="rounded-full bg-[color:var(--color-surface-sunken)] px-2 py-0.5 text-[10px] font-semibold text-[color:var(--color-text-muted)]"
          >{{ tab.count }}</span
        >
      </button>
    </div>

    <!-- Section content -->
    <div class="min-w-0">
      <slot />
    </div>
  </div>
</template>
