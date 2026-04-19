<script setup lang="ts">
/**
 * InterviewGatewayPage — candidate lands here via email link and is
 * routed to the right screening mode (chat or room).
 *
 * T13 redesign: full-bleed ambient background + centered glass card with
 * the Prism glyph as a glow. The page is standalone (no PublicLayout)
 * so we mount AnimatedBackground directly. The picker is suppressed to
 * avoid distracting the candidate right before their interview.
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import AnimatedBackground from '@/shared/components/AnimatedBackground.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import { useThemeStore } from '@/shared/stores/theme.store'
import { interviewService } from '../services/interview.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { InterviewDetail } from '../types/interview.types'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()

const token = route.params.token as string
const loading = ref(true)
const errorState = ref<'expired' | 'closed' | 'completed' | 'error' | null>(null)
const errorMessage = ref('')
const interview = ref<InterviewDetail | null>(null)

onMounted(async () => {
  // Ensure a background is set for the gateway moment.
  if (themeStore.backgroundMode === 'off') {
    themeStore.setBackgroundMode('vellum')
  }

  try {
    const data = await interviewService.getInterviewByToken(token)
    interview.value = data

    if (data.status === 'completed') {
      errorState.value = 'completed'
      loading.value = false
      return
    }

    if (data.status === 'expired') {
      errorState.value = 'expired'
      loading.value = false
      return
    }

    if (data.status === 'cancelled') {
      errorState.value = 'closed'
      loading.value = false
      return
    }

    if (data.screeningMode === 'chat') {
      router.replace({ name: ROUTE_NAMES.CHAT_INTERVIEW, params: { token } })
    } else {
      router.replace({ name: ROUTE_NAMES.INTERVIEW_ROOM, params: { token } })
    }
  } catch (err: unknown) {
    const axiosErr = err as {
      response?: { status?: number; data?: { detail?: string; message?: string } }
    }
    const status = axiosErr.response?.status
    const detail = axiosErr.response?.data?.detail ?? axiosErr.response?.data?.message ?? ''

    if (status === 404) {
      errorState.value = 'error'
      errorMessage.value = 'Interview not found. The link may be invalid.'
    } else if (status === 410 || detail.toLowerCase().includes('expired')) {
      errorState.value = 'expired'
      errorMessage.value = detail || 'This interview link has expired.'
    } else if (detail.toLowerCase().includes('closed')) {
      errorState.value = 'closed'
      errorMessage.value = detail || 'This vacancy has been closed.'
    } else {
      errorState.value = 'error'
      errorMessage.value = detail || 'Something went wrong. Please try again later.'
    }
    loading.value = false
  }
})
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center px-4 py-12">
    <AnimatedBackground />

    <!-- Loading — only the Prism glyph pulses; no chrome -->
    <div v-if="loading" class="animate-in relative z-0 text-center">
      <div class="mx-auto mb-6 flex justify-center">
        <AppLogo variant="glyph" size="lg" :linked="false" />
      </div>
      <p class="text-sm text-[color:var(--color-text-secondary)]">
        {{ t('interviews.gatewayPage.loading') }}
      </p>
    </div>

    <!-- Error / terminal states -->
    <GlassCard
      v-else
      class="animate-in relative z-0 w-full max-w-md text-center"
      :accent="errorState === 'completed' ? 'celebrate' : 'default'"
    >
      <div class="mb-4 flex justify-center">
        <AppLogo variant="glyph" size="lg" :linked="false" />
      </div>

      <template v-if="errorState === 'completed'">
        <div
          class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)]"
        >
          <i class="pi pi-check-circle text-3xl text-[color:var(--color-accent-celebrate)]"></i>
        </div>
        <h1 class="mb-2 text-2xl font-semibold text-[color:var(--color-text-primary)]">
          {{ t('interviews.gatewayPage.interviewCompleted') }}
        </h1>
        <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
          {{ t('interviews.gatewayPage.completedMessage') }}
        </p>
        <RouterLink to="/jobs" class="text-sm text-[color:var(--color-accent)] hover:underline">
          {{ t('interviews.gatewayPage.browseMoreJobs') }}
        </RouterLink>
      </template>

      <template v-else-if="errorState === 'expired'">
        <div
          class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-warning)]/15"
        >
          <i class="pi pi-clock text-3xl text-[color:var(--color-warning)]"></i>
        </div>
        <h1 class="mb-2 text-2xl font-semibold text-[color:var(--color-text-primary)]">
          {{ t('interviews.gatewayPage.linkExpired') }}
        </h1>
        <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
          {{ errorMessage || t('interviews.states.expired') }}
        </p>
        <RouterLink to="/jobs" class="text-sm text-[color:var(--color-accent)] hover:underline">
          {{ t('interviews.gatewayPage.browseMoreJobs') }}
        </RouterLink>
      </template>

      <template v-else-if="errorState === 'closed'">
        <div
          class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-surface-sunken)]"
        >
          <i class="pi pi-ban text-3xl text-[color:var(--color-text-muted)]"></i>
        </div>
        <h1 class="mb-2 text-2xl font-semibold text-[color:var(--color-text-primary)]">
          {{ t('interviews.gatewayPage.vacancyClosed') }}
        </h1>
        <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
          {{ errorMessage || t('interviews.states.closed') }}
        </p>
        <RouterLink to="/jobs" class="text-sm text-[color:var(--color-accent)] hover:underline">
          {{ t('interviews.gatewayPage.browseMoreJobs') }}
        </RouterLink>
      </template>

      <template v-else>
        <div
          class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-danger)]/15"
        >
          <i class="pi pi-exclamation-triangle text-3xl text-[color:var(--color-danger)]"></i>
        </div>
        <h1 class="mb-2 text-2xl font-semibold text-[color:var(--color-text-primary)]">
          {{ t('interviews.gatewayPage.somethingWentWrong') }}
        </h1>
        <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">{{ errorMessage }}</p>
        <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" @click="$router.go(0)" />
      </template>
    </GlassCard>
  </div>
</template>
