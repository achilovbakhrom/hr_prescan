<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { appConfigService, type PublicAppConfig } from '@/shared/services/app-config.service'
import { buildCandidateTelegramBotUrl, buildHrTelegramBotUrl } from '@/shared/utils/telegram'

const { t } = useI18n()
const publicConfig = ref<PublicAppConfig | null>(null)

onMounted(async () => {
  try {
    publicConfig.value = await appConfigService.getPublicConfig()
  } catch {
    /* fallback to Vite env */
  }
})

const telegramLinks = computed(() =>
  [
    {
      key: 'candidate',
      href: buildCandidateTelegramBotUrl(
        undefined,
        publicConfig.value?.telegramCandidateBotUsername,
      ),
      icon: 'pi pi-user',
      title: t('landing.hero.telegramCandidateTitle'),
      hint: t('landing.hero.telegramCandidateHint'),
      action: t('landing.hero.openCandidateTelegram'),
    },
    {
      key: 'hr',
      href: buildHrTelegramBotUrl(publicConfig.value?.telegramHrBotUsername),
      icon: 'pi pi-briefcase',
      title: t('landing.hero.telegramHrTitle'),
      hint: t('landing.hero.telegramHrHint'),
      action: t('landing.hero.openHrTelegram'),
    },
  ].filter((item) => item.href),
)
</script>

<template>
  <div
    v-if="telegramLinks.length"
    class="bg-glass-1 border-glass shadow-glass hero-stagger hero-stagger-4 mt-5 rounded-[28px] p-3 backdrop-blur-xl sm:p-4"
  >
    <div class="flex items-center gap-2 px-2 pb-3">
      <span
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
      >
        <i class="pi pi-send text-sm"></i>
      </span>
      <div class="min-w-0">
        <p class="text-sm font-semibold text-[color:var(--color-text-primary)]">
          {{ t('telegram.title') }}
        </p>
      </div>
    </div>

    <div class="grid gap-2">
      <a
        v-for="item in telegramLinks"
        :key="item.key"
        :href="item.href"
        target="_blank"
        rel="noopener"
        class="group flex flex-col gap-3 rounded-[22px] border border-[color:var(--color-border-glass)] bg-white/58 px-4 py-3 text-left shadow-[0_10px_28px_rgba(15,23,42,0.06)] transition-all duration-200 hover:-translate-y-px hover:border-[color:color-mix(in_srgb,var(--color-accent)_28%,var(--color-border-glass))] hover:shadow-[0_16px_32px_rgba(15,23,42,0.1)] dark:bg-white/6 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
      >
        <div class="flex min-w-0 items-start gap-3">
          <span
            class="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
          >
            <i :class="item.icon" class="text-sm"></i>
          </span>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-[color:var(--color-text-primary)]">
              {{ item.title }}
            </p>
            <p class="mt-1 text-xs leading-relaxed text-[color:var(--color-text-muted)]">
              {{ item.hint }}
            </p>
          </div>
        </div>

        <span
          class="inline-flex self-start shrink-0 items-center gap-2 rounded-full bg-[color:var(--color-accent-soft)] px-3 py-2 text-xs font-semibold text-[color:var(--color-accent)] transition-colors group-hover:bg-[color:var(--color-accent)] group-hover:text-white sm:self-center"
        >
          {{ item.action }}
          <i class="pi pi-arrow-up-right text-[10px]"></i>
        </span>
      </a>
    </div>
  </div>
</template>
