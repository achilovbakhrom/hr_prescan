<script setup lang="ts">
/**
 * VacancyDetailHeader — glass header card with title, status badge, and
 * one-directional state-transition actions (draft → published ↔ paused →
 * archived). Copy-share-link button included.
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import VacancyStatusBadge from './VacancyStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { VacancyStatus } from '../types/vacancy.types'

const props = defineProps<{
  title: string
  status: VacancyStatus
  shareToken?: string
  loading: boolean
  companyName?: string | null
}>()
const emit = defineEmits<{
  statusChange: [status: VacancyStatus]
}>()
const { t } = useI18n()
const router = useRouter()

const linkCopied = ref(false)

function copyShareLink(): void {
  if (!props.shareToken) return
  const url = `${window.location.origin}/jobs/share/${props.shareToken}`
  navigator.clipboard.writeText(url).then(() => {
    linkCopied.value = true
    setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  })
}
</script>

<template>
  <GlassCard>
    <div class="flex flex-col gap-3">
      <div class="flex items-center gap-2 sm:gap-3">
        <button
          class="shrink-0 rounded-lg p-1.5 text-[color:var(--color-text-muted)] transition-colors hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]"
          :aria-label="t('common.back')"
          @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })"
        >
          <i class="pi pi-arrow-left"></i>
        </button>
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-2">
            <h1
              class="truncate text-base font-bold text-[color:var(--color-text-primary)] sm:text-lg md:text-2xl"
            >
              {{ title }}
            </h1>
            <VacancyStatusBadge :status="status" />
          </div>
          <p
            v-if="companyName"
            class="mt-0.5 truncate text-xs text-[color:var(--color-text-muted)]"
          >
            <i class="pi pi-building mr-1"></i>{{ companyName }}
          </p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
        <Button
          v-if="status === 'draft'"
          :label="t('vacancies.actions.publish')"
          icon="pi pi-send"
          size="small"
          @click="emit('statusChange', 'published')"
        />
        <Button
          v-if="status === 'published'"
          :label="t('vacancies.actions.pause')"
          icon="pi pi-pause"
          severity="warn"
          size="small"
          @click="emit('statusChange', 'paused')"
        />
        <Button
          v-if="status === 'paused'"
          :label="t('vacancies.actions.resume')"
          icon="pi pi-play"
          severity="success"
          size="small"
          @click="emit('statusChange', 'published')"
        />
        <Button
          v-if="status === 'published' || status === 'paused'"
          :label="t('vacancies.actions.archive')"
          icon="pi pi-inbox"
          severity="secondary"
          size="small"
          outlined
          @click="emit('statusChange', 'archived')"
        />
        <Button
          :label="linkCopied ? t('common.copied') : t('common.copyLink')"
          :icon="linkCopied ? 'pi pi-check' : 'pi pi-link'"
          :severity="linkCopied ? 'success' : 'secondary'"
          size="small"
          outlined
          @click="copyShareLink"
        />
      </div>
    </div>
  </GlassCard>
</template>
