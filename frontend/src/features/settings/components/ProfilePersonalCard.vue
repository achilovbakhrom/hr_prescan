<script setup lang="ts">
/**
 * ProfilePersonalCard — personal info + account summary section.
 */
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import GlassCard from '@/shared/components/GlassCard.vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'

defineProps<{
  firstName: string
  lastName: string
  email: string
  phone: string
}>()

const { t } = useI18n()
const authStore = useAuthStore()
</script>

<template>
  <GlassCard id="personal">
    <div class="mb-6 flex items-center gap-4">
      <div
        class="flex h-16 w-16 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-2xl font-semibold text-[color:var(--color-accent)]"
      >
        {{ authStore.user?.firstName?.charAt(0) ?? ''
        }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
      </div>
      <div>
        <p class="text-lg font-semibold text-[color:var(--color-text-primary)]">
          {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
        </p>
        <p
          class="mt-0.5 inline-flex items-center gap-1.5 text-xs uppercase tracking-wider text-[color:var(--color-accent-ai)]"
        >
          <i class="pi pi-shield text-[10px]"></i>
          {{ authStore.user?.role }}
        </p>
      </div>
    </div>

    <form class="grid grid-cols-1 gap-4 sm:grid-cols-2" @submit.prevent>
      <div class="flex flex-col gap-1.5">
        <label for="firstName" class="text-sm font-medium text-[color:var(--color-text-secondary)]">
          {{ t('settings.profile.firstName') }}
        </label>
        <InputText id="firstName" :value="firstName" class="w-full" disabled />
      </div>
      <div class="flex flex-col gap-1.5">
        <label for="lastName" class="text-sm font-medium text-[color:var(--color-text-secondary)]">
          {{ t('settings.profile.lastName') }}
        </label>
        <InputText id="lastName" :value="lastName" class="w-full" disabled />
      </div>
      <div class="flex flex-col gap-1.5 sm:col-span-2">
        <label for="email" class="text-sm font-medium text-[color:var(--color-text-secondary)]">
          {{ t('settings.profile.email') }}
        </label>
        <InputText id="email" :value="email" class="w-full" disabled />
        <small class="text-[color:var(--color-text-muted)]">
          {{ t('settings.profile.emailCannotChange') }}
        </small>
      </div>
      <div class="flex flex-col gap-1.5 sm:col-span-2">
        <label for="phone" class="text-sm font-medium text-[color:var(--color-text-secondary)]">
          {{ t('settings.profile.phone') }}
        </label>
        <InputText id="phone" :value="phone" class="w-full" disabled />
      </div>
    </form>

    <div class="mt-6 border-t border-[color:var(--color-border-soft)] pt-4">
      <h3 class="mb-2 text-sm font-medium text-[color:var(--color-text-secondary)]">
        {{ t('settings.profile.accountInfo') }}
      </h3>
      <div class="space-y-1 text-sm text-[color:var(--color-text-muted)]">
        <p>
          {{ t('settings.profile.emailVerified') }}
          <span
            :class="
              authStore.user?.emailVerified
                ? 'text-[color:var(--color-success)]'
                : 'text-[color:var(--color-danger)]'
            "
          >
            {{ authStore.user?.emailVerified ? t('common.yes') : t('common.no') }}
          </span>
        </p>
        <p v-if="authStore.user?.company">
          {{ t('settings.profile.companyLabel') }}
          <span class="font-medium text-[color:var(--color-text-primary)]">
            {{ authStore.user.company.name }}
          </span>
        </p>
        <p v-else>{{ t('settings.profile.noCompany') }}</p>
      </div>
    </div>
  </GlassCard>
</template>
