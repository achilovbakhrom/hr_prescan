<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
  totalApplications: number
  totalInterviews: number
  completionRate: number
  averageScore: number | null
}>()
</script>

<template>
  <div class="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50"><i class="pi pi-users text-lg text-blue-600"></i></div>
        <span class="text-2xl font-bold text-gray-900">{{ totalApplications }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.totalApplications') }}</p>
    </div>
    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50"><i class="pi pi-video text-lg text-violet-600"></i></div>
        <span class="text-2xl font-bold text-gray-900">{{ totalInterviews }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.totalInterviews') }}</p>
    </div>
    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50"><i class="pi pi-check-circle text-lg text-emerald-600"></i></div>
        <span class="text-2xl font-bold text-gray-900">{{ completionRate }}%</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.completionRate') }}</p>
    </div>
    <div class="rounded-xl border border-gray-100 bg-white p-5">
      <div class="flex items-center justify-between">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50"><i class="pi pi-star text-lg text-amber-600"></i></div>
        <span class="text-2xl font-bold text-gray-900">{{ averageScore !== null ? averageScore : '-' }}</span>
      </div>
      <p class="mt-3 text-sm font-medium text-gray-500">{{ t('analytics.avgInterviewScore') }}</p>
    </div>
  </div>
</template>
