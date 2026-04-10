<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import ToggleSwitch from 'primevue/toggleswitch'
import ProgressBar from 'primevue/progressbar'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CandidateProfile } from '../types/cv-builder.types'

const { t } = useI18n()
const router = useRouter()

defineProps<{
  profile: CandidateProfile
}>()

const emit = defineEmits<{
  toggleVisibility: []
  viewPublic: []
  delete: []
}>()

function progressColor(score: number): string {
  if (score >= 80) return '!bg-green-500'
  if (score >= 50) return '!bg-yellow-500'
  return '!bg-red-500'
}
</script>

<template>
  <div class="mb-6 rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50/50 to-white p-5">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-4">
        <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
          <i class="pi pi-user text-xl"></i>
        </div>
        <div class="min-w-0">
          <p class="font-semibold text-gray-900">{{ profile.headline || t('myCvs.profileCard.noHeadline') }}</p>
          <p v-if="profile.location" class="text-sm text-gray-500">
            <i class="pi pi-map-marker mr-1 text-xs"></i>{{ profile.location }}
          </p>
          <div class="mt-1.5 flex items-center gap-2">
            <ProgressBar :value="profile.completeness.score" :showValue="false" class="!h-1.5 w-24" :pt="{ value: { class: progressColor(profile.completeness.score) } }" />
            <span class="text-xs font-medium text-gray-500">{{ profile.completeness.score }}%</span>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <Button icon="pi pi-eye" severity="secondary" text rounded size="small" v-tooltip.top="t('myCvs.view')" :disabled="!profile.isOpenToWork" @click="emit('viewPublic')" />
        <Button icon="pi pi-pencil" severity="secondary" text rounded size="small" v-tooltip.top="t('common.edit')" @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })" />
        <span class="h-5 w-px bg-gray-200"></span>
        <Button icon="pi pi-trash" severity="danger" text rounded size="small" v-tooltip.top="t('myCvs.deleteProfile')" @click="emit('delete')" />
      </div>
    </div>

    <div class="mt-4 flex items-center justify-between rounded-lg px-3 py-2" :class="profile.isOpenToWork ? 'bg-green-50' : 'bg-gray-100'">
      <div class="flex items-center gap-2">
        <i class="pi text-sm" :class="profile.isOpenToWork ? 'pi-eye text-green-600' : 'pi-eye-slash text-gray-400'"></i>
        <span class="text-sm" :class="profile.isOpenToWork ? 'text-green-700' : 'text-gray-500'">
          {{ profile.isOpenToWork ? t('myCvs.cvIsVisible') : t('myCvs.cvIsHidden') }}
        </span>
      </div>
      <ToggleSwitch :modelValue="profile.isOpenToWork" @update:modelValue="emit('toggleVisibility')" />
    </div>
  </div>
</template>
