<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import GlassSurface from '@/shared/components/GlassSurface.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const isTrial = computed(() => user.value?.subscriptionStatus === 'trial')
const daysRemaining = computed(() => {
  if (!user.value?.trialEndsAt) return null
  const diff = new Date(user.value.trialEndsAt).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})

const bannerClass = computed(() => {
  if (!daysRemaining.value || daysRemaining.value > 3) return ''
  if (daysRemaining.value > 0) return 'urgent'
  return 'critical'
})
</script>

<template>
  <GlassSurface v-if="isTrial" level="1" class="trial-banner p-4" :class="bannerClass">
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
          <p class="text-xs opacity-80">{{ t('trial.banner') }}</p>
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
  </GlassSurface>
</template>

<style scoped>
.trial-banner.urgent {
  border-color: color-mix(in srgb, var(--color-warning) 50%, transparent);
  background: color-mix(in srgb, var(--color-warning) 12%, var(--color-surface-glass-1));
  color: var(--color-text-primary);
}
.trial-banner.critical {
  border-color: color-mix(in srgb, var(--color-danger) 50%, transparent);
  background: color-mix(in srgb, var(--color-danger) 12%, var(--color-surface-glass-1));
  color: var(--color-text-primary);
}
</style>
