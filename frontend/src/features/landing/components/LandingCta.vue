<script setup lang="ts">
/**
 * LandingCta — Figma closing CTA: a violet→pink gradient card with a headline
 * and "Start free trial" button, plus a "prefer Telegram?" band underneath.
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { appConfigService, type PublicAppConfig } from '@/shared/services/app-config.service'
import { buildCandidateTelegramBotUrl, buildHrTelegramBotUrl } from '@/shared/utils/telegram'

const router = useRouter()
const { t } = useI18n()
const publicConfig = ref<PublicAppConfig | null>(null)

onMounted(async () => {
  try {
    publicConfig.value = await appConfigService.getPublicConfig()
  } catch {
    /* fallback to env */
  }
})

const candidateHref = computed(() =>
  buildCandidateTelegramBotUrl(
    undefined,
    undefined,
    publicConfig.value?.telegramCandidateBotUsername,
  ),
)
const hrHref = computed(() => buildHrTelegramBotUrl(publicConfig.value?.telegramHrBotUsername))
</script>

<template>
  <section id="pricing" class="px-4 py-20 sm:px-6 md:py-28">
    <div class="scroll-animate mx-auto max-w-5xl">
      <div
        class="relative overflow-hidden rounded-[28px] bg-[linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)] px-6 py-14 text-center text-white shadow-[0_30px_80px_-30px_rgba(124,58,237,0.6)] sm:px-10"
      >
        <h2 class="mx-auto max-w-2xl text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
          {{ t('landing.cta.title') }}
        </h2>
        <p class="mx-auto mt-4 max-w-lg text-base text-white/85 md:text-lg">
          {{ t('landing.cta.subtitle') }}
        </p>
        <button
          type="button"
          class="mt-8 inline-flex items-center gap-2 rounded-full bg-white px-7 py-3 text-sm font-semibold text-[#7c3aed] shadow-lg transition-transform hover:-translate-y-0.5"
          @click="router.push({ name: ROUTE_NAMES.REGISTER })"
        >
          {{ t('landing.cta.startFree') }}
          <i class="pi pi-arrow-right text-xs"></i>
        </button>
      </div>

      <!-- Prefer Telegram? -->
      <div v-if="candidateHref || hrHref" class="mt-8 text-center">
        <p
          class="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
        >
          {{ t('landing.telegram.prefer') }}
        </p>
        <div class="mt-4 flex flex-wrap items-center justify-center gap-3">
          <a
            v-if="candidateHref"
            :href="candidateHref"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-2 rounded-full border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] px-5 py-2.5 text-sm font-medium text-[color:var(--color-text-primary)] transition-colors hover:bg-[color:var(--color-surface-sunken)]"
          >
            <i class="pi pi-send text-[color:var(--color-accent)]"></i>
            {{ t('landing.telegram.apply') }}
          </a>
          <a
            v-if="hrHref && hrHref !== candidateHref"
            :href="hrHref"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-2 rounded-full border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-glass-1)] px-5 py-2.5 text-sm font-medium text-[color:var(--color-text-primary)] transition-colors hover:bg-[color:var(--color-surface-sunken)]"
          >
            <i class="pi pi-briefcase text-[color:var(--color-accent)]"></i>
            {{ t('landing.telegram.recruiter') }}
          </a>
        </div>
      </div>
    </div>
  </section>
</template>
