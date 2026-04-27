<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import ToggleSwitch from 'primevue/toggleswitch'
import ProgressBar from 'primevue/progressbar'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CandidateProfile } from '../types/cv-builder.types'

defineProps<{
  profile: CandidateProfile
}>()
const emit = defineEmits<{
  toggleVisibility: []
  viewPublic: []
  delete: []
}>()
const { t } = useI18n()
const router = useRouter()

function progressColor(score: number): string {
  if (score >= 80) return '!bg-green-500'
  if (score >= 50) return '!bg-yellow-500'
  return '!bg-red-500'
}
</script>

<template>
  <div
    class="mb-6 rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] p-5 shadow-glass backdrop-blur-md dark:border-white/10 dark:bg-slate-800/70"
  >
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-4">
        <div
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-700 dark:bg-blue-500/15 dark:text-blue-300"
        >
          <i class="pi pi-user text-xl"></i>
        </div>
        <div class="min-w-0">
          <p class="font-semibold text-[color:var(--color-text-primary)]">
            {{ profile.headline || t('myCvs.profileCard.noHeadline') }}
          </p>
          <p v-if="profile.location" class="text-sm text-[color:var(--color-text-muted)]">
            <i class="pi pi-map-marker mr-1 text-xs"></i>{{ profile.location }}
          </p>
          <div class="mt-1.5 flex items-center gap-2">
            <ProgressBar
              :value="profile.completeness.score"
              :showValue="false"
              class="!h-1.5 w-24"
              :pt="{ value: { class: progressColor(profile.completeness.score) } }"
            />
            <span class="text-xs font-medium text-[color:var(--color-text-muted)]"
              >{{ profile.completeness.score }}%</span
            >
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <Button
          icon="pi pi-eye"
          severity="secondary"
          text
          rounded
          size="small"
          v-tooltip.top="t('myCvs.view')"
          :disabled="!profile.isOpenToWork"
          @click="emit('viewPublic')"
        />
        <Button
          icon="pi pi-pencil"
          severity="secondary"
          text
          rounded
          size="small"
          v-tooltip.top="t('common.edit')"
          @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
        />
        <span class="h-5 w-px bg-[color:var(--color-border-soft)] dark:bg-white/10"></span>
        <Button
          icon="pi pi-trash"
          severity="danger"
          text
          rounded
          size="small"
          v-tooltip.top="t('myCvs.deleteProfile')"
          @click="emit('delete')"
        />
      </div>
    </div>

    <div
      class="mt-4 flex items-center justify-between rounded-lg px-3 py-2"
      :class="
        profile.isOpenToWork
          ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-200'
          : 'bg-[color:var(--color-surface-sunken)] text-[color:var(--color-text-muted)] dark:bg-white/10'
      "
    >
      <div class="flex items-center gap-2">
        <i
          class="pi text-sm"
          :class="
            profile.isOpenToWork
              ? 'pi-eye text-emerald-600 dark:text-emerald-300'
              : 'pi-eye-slash text-[color:var(--color-text-muted)]'
          "
        ></i>
        <span class="text-sm">
          {{ profile.isOpenToWork ? t('myCvs.cvIsVisible') : t('myCvs.cvIsHidden') }}
        </span>
      </div>
      <ToggleSwitch
        :modelValue="profile.isOpenToWork"
        @update:modelValue="emit('toggleVisibility')"
      />
    </div>
  </div>
</template>
