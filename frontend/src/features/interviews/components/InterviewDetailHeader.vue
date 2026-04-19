<script setup lang="ts">
/**
 * InterviewDetailHeader — GlassCard header for the interview detail page.
 * Shows candidate / vacancy / timestamp + session-type + status badges and
 * action buttons (open room / cancel / watch live). Room-link banner shown
 * when interview is scheduled or in-progress.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import GlassCard from '@/shared/components/GlassCard.vue'
import InterviewStatusBadge from './InterviewStatusBadge.vue'
import type { Interview } from '../types/interview.types'

const props = defineProps<{
  interview: Interview
  loading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
  watchLive: []
}>()

const { t } = useI18n()
const router = useRouter()

const isScheduled = computed(() => props.interview.status === 'pending')
const isInProgress = computed(() => props.interview.status === 'in_progress')
const roomUrl = computed(() => `${window.location.origin}/interview/${props.interview.id}/room`)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString()
}
</script>

<template>
  <GlassCard>
    <div
      class="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-start sm:justify-between sm:gap-4"
    >
      <div class="space-y-1">
        <p class="text-base font-semibold text-[color:var(--color-text-primary)] md:text-lg">
          {{ interview.candidateName }}
        </p>
        <p class="text-sm text-[color:var(--color-text-secondary)]">
          {{ interview.vacancyTitle }}
        </p>
        <p class="font-mono text-xs text-[color:var(--color-text-muted)] sm:text-sm">
          {{ formatDate(interview.createdAt) }} · {{ interview.durationMinutes }} min
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2 sm:gap-3">
        <Tag
          :value="
            interview.sessionType === 'prescanning'
              ? t('candidates.prescanning')
              : t('candidates.interview')
          "
          :severity="interview.sessionType === 'prescanning' ? 'info' : 'success'"
        />
        <InterviewStatusBadge :status="interview.status" />
        <Button
          v-if="isScheduled || isInProgress"
          :label="t('interviews.detailPage.openRoom')"
          icon="pi pi-external-link"
          size="small"
          severity="info"
          @click="router.push(`/interview/${interview.id}/room`)"
        />
        <Button
          v-if="isScheduled"
          :label="t('common.cancel')"
          severity="danger"
          size="small"
          outlined
          :loading="loading"
          @click="emit('cancel')"
        />
        <Button
          v-if="isInProgress"
          :label="t('interviews.detailPage.watchLive')"
          icon="pi pi-eye"
          size="small"
          @click="emit('watchLive')"
        />
      </div>
    </div>
    <div
      v-if="isScheduled || isInProgress"
      class="mt-4 rounded border border-[color:var(--color-accent-soft)] bg-[color:var(--color-accent-soft)]/40 p-3"
    >
      <p class="text-sm font-medium text-[color:var(--color-accent)]">
        {{ t('interviews.detailPage.roomLink') }}
      </p>
      <p class="mt-1 break-all font-mono text-xs text-[color:var(--color-accent)]">
        {{ roomUrl }}
      </p>
      <p class="mt-1 text-xs text-[color:var(--color-text-muted)]">
        {{ t('interviews.detailPage.roomLinkHint') }}
      </p>
    </div>
  </GlassCard>
</template>
