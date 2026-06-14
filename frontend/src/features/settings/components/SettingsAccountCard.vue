<script setup lang="ts">
/** SettingsAccountCard — Figma settings right rail: account summary rows. */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'

const { t } = useI18n()
const authStore = useAuthStore()

const rows = computed(() => [
  { label: t('settings.account.role'), value: authStore.user?.role ?? '—' },
  { label: t('settings.profile.email'), value: authStore.user?.email ?? '—' },
])
</script>

<template>
  <GlassCard class="overflow-hidden p-0">
    <div class="px-5 py-4">
      <h3 class="text-base font-semibold text-[color:var(--color-text-primary)]">
        {{ t('settings.account.title') }}
      </h3>
    </div>
    <div class="space-y-3 border-t border-[color:var(--color-border-soft)] px-5 py-4">
      <div v-for="r in rows" :key="r.label" class="flex items-center justify-between gap-3">
        <span class="text-sm text-[color:var(--color-text-muted)]">{{ r.label }}</span>
        <span
          class="truncate text-sm font-medium capitalize text-[color:var(--color-text-primary)]"
        >
          {{ r.value }}
        </span>
      </div>
    </div>
  </GlassCard>
</template>
