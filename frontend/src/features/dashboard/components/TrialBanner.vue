<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const company = computed(() => authStore.user?.company)
const isTrial = computed(() => company.value?.subscriptionStatus === 'trial')
const daysRemaining = computed(() => {
  if (!company.value?.trialEndsAt) return null
  const diff = new Date(company.value.trialEndsAt).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})

const bannerClass = computed(() => {
  if (!daysRemaining.value || daysRemaining.value > 3)
    return 'bg-blue-50 border-blue-200 text-blue-800'
  if (daysRemaining.value > 0) return 'bg-amber-50 border-amber-200 text-amber-800'
  return 'bg-red-50 border-red-200 text-red-800'
})
</script>

<template>
  <div v-if="isTrial" class="rounded-xl border p-4" :class="bannerClass">
    <div class="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
      <div class="flex items-center gap-3">
        <i class="pi pi-clock text-lg"></i>
        <div>
          <p class="text-sm font-semibold">
            {{
              daysRemaining && daysRemaining > 0
                ? t('trial.daysLeft', { days: daysRemaining })
                : t('trial.expired')
            }}
          </p>
          <p class="text-xs opacity-75">{{ t('trial.banner') }}</p>
        </div>
      </div>
      <Button
        :label="t('trial.choosePlan')"
        icon="pi pi-arrow-right"
        icon-pos="right"
        size="small"
        @click="router.push({ name: ROUTE_NAMES.PRICING })"
      />
    </div>
  </div>
</template>
