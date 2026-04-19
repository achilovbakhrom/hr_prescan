<script setup lang="ts">
/**
 * ChatErrorState — terminal states for the chat interview flow.
 *
 * T13 redesign: composes GlassCard on top of the ambient background
 * (parent page provides AnimatedBackground).
 */
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import type { ChatErrorState } from '../composables/useChatInterview'

defineProps<{
  errorState: ChatErrorState
  errorMessage: string
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-1 items-center justify-center px-4 py-8">
    <div class="w-full max-w-md">
      <GlassCard :accent="errorState === 'completed' ? 'celebrate' : 'default'" class="text-center">
        <div class="mb-3 flex justify-center">
          <AppLogo variant="glyph" size="md" :linked="false" />
        </div>

        <template v-if="errorState === 'completed'">
          <div
            class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
          >
            <i class="pi pi-check text-3xl text-[color:var(--color-accent-celebrate)]"></i>
          </div>
          <h1 class="mb-2 text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.chatPage.interviewCompleted') }}
          </h1>
          <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
            {{ t('interviews.states.completed') }}
          </p>
          <RouterLink to="/jobs">
            <Button :label="t('interviews.chatPage.browseMoreJobs')" />
          </RouterLink>
        </template>

        <template v-else-if="errorState === 'expired'">
          <div
            class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-warning)]/15"
          >
            <i class="pi pi-clock text-3xl text-[color:var(--color-warning)]"></i>
          </div>
          <h1 class="mb-2 text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.chatPage.linkExpired') }}
          </h1>
          <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
            {{ errorMessage || t('interviews.states.expired') }}
          </p>
          <RouterLink
            to="/jobs"
            class="text-sm font-medium text-[color:var(--color-accent)] hover:underline"
          >
            {{ t('interviews.chatPage.browseMoreJobs') }}
          </RouterLink>
        </template>

        <template v-else-if="errorState === 'closed'">
          <div
            class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-surface-sunken)]"
          >
            <i class="pi pi-ban text-3xl text-[color:var(--color-text-muted)]"></i>
          </div>
          <h1 class="mb-2 text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.chatPage.vacancyClosed') }}
          </h1>
          <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
            {{ errorMessage || t('interviews.states.closed') }}
          </p>
          <RouterLink
            to="/jobs"
            class="text-sm font-medium text-[color:var(--color-accent)] hover:underline"
          >
            {{ t('interviews.chatPage.browseMoreJobs') }}
          </RouterLink>
        </template>

        <template v-else>
          <div
            class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-danger)]/15"
          >
            <i class="pi pi-exclamation-triangle text-3xl text-[color:var(--color-danger)]"></i>
          </div>
          <h1 class="mb-2 text-xl font-semibold text-[color:var(--color-text-primary)]">
            {{ t('interviews.chatPage.somethingWentWrong') }}
          </h1>
          <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">{{ errorMessage }}</p>
          <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="$router.go(0)" />
        </template>
      </GlassCard>
    </div>
  </div>
</template>
