<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import VacancyStatusBadge from './VacancyStatusBadge.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { VacancyStatus } from '../types/vacancy.types'

const { t } = useI18n()
const router = useRouter()

const props = defineProps<{
  title: string
  status: VacancyStatus
  shareToken?: string
  loading: boolean
}>()

const emit = defineEmits<{
  statusChange: [status: VacancyStatus]
}>()

const linkCopied = ref(false)

function copyShareLink(): void {
  if (!props.shareToken) return
  const url = `${window.location.origin}/jobs/share/${props.shareToken}`
  navigator.clipboard.writeText(url).then(() => {
    linkCopied.value = true
    setTimeout(() => { linkCopied.value = false }, 2000)
  })
}
</script>

<template>
  <div class="space-y-3 sm:space-y-4">
    <div class="flex items-center gap-2 sm:gap-3">
      <button class="shrink-0 rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700" @click="router.push({ name: ROUTE_NAMES.VACANCY_LIST })">
        <i class="pi pi-arrow-left"></i>
      </button>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <h1 class="truncate text-base font-bold sm:text-lg md:text-2xl">{{ title }}</h1>
          <VacancyStatusBadge :status="status" />
        </div>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
      <Button v-if="status === 'draft'" :label="t('vacancies.actions.publish')" icon="pi pi-send" size="small" @click="emit('statusChange', 'published')" />
      <Button v-if="status === 'published'" :label="t('vacancies.actions.pause')" icon="pi pi-pause" severity="warn" size="small" @click="emit('statusChange', 'paused')" />
      <Button v-if="status === 'paused'" :label="t('vacancies.actions.resume')" icon="pi pi-play" severity="success" size="small" @click="emit('statusChange', 'published')" />
      <Button v-if="status === 'published' || status === 'paused'" :label="t('vacancies.actions.archive')" icon="pi pi-inbox" severity="secondary" size="small" outlined @click="emit('statusChange', 'archived')" />
      <Button :label="linkCopied ? t('common.copied') : t('common.copyLink')" :icon="linkCopied ? 'pi pi-check' : 'pi pi-link'" :severity="linkCopied ? 'success' : 'secondary'" size="small" outlined @click="copyShareLink" />
    </div>
  </div>
</template>
