<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { buildCandidateTelegramBotUrl } from '@/shared/utils/telegram'

const props = withDefaults(
  defineProps<{
    telegramCode?: number | null
    title: string
    hint: string
    openLabel: string
    copyLabel: string
    compact?: boolean
  }>(),
  {
    telegramCode: null,
    compact: false,
  },
)

const { t } = useI18n()

const telegramUrl = computed(() => buildCandidateTelegramBotUrl(props.telegramCode))
const copied = ref(false)

async function copyTelegramLink(): Promise<void> {
  if (!telegramUrl.value) return
  try {
    await navigator.clipboard.writeText(telegramUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    /* clipboard unavailable */
  }
}
</script>

<template>
  <div
    v-if="telegramUrl"
    class="rounded-2xl border border-sky-200/80 bg-sky-50/85 text-left shadow-[0_10px_24px_rgba(14,116,144,0.08)] backdrop-blur-xl dark:border-sky-900/60 dark:bg-sky-950/35"
    :class="compact ? 'p-3.5' : 'p-4 sm:p-5'"
  >
    <div class="flex items-start gap-3">
      <span
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white/85 text-sky-600 shadow-sm dark:bg-sky-900/70 dark:text-sky-300"
      >
        <i class="pi pi-telegram text-lg"></i>
      </span>
      <div class="min-w-0 flex-1">
        <p
          class="font-semibold text-sky-950 dark:text-sky-50"
          :class="compact ? 'text-sm' : 'text-sm sm:text-base'"
        >
          {{ title }}
        </p>
        <p
          class="mt-1 text-sky-800/90 dark:text-sky-100/85"
          :class="compact ? 'text-xs leading-relaxed' : 'text-xs leading-relaxed sm:text-sm'"
        >
          {{ hint }}
        </p>
      </div>
    </div>

    <div class="mt-3 flex flex-col gap-2 sm:flex-row">
      <Button
        as="a"
        :href="telegramUrl"
        target="_blank"
        rel="noopener"
        :label="openLabel"
        icon="pi pi-external-link"
        size="small"
        class="w-full sm:w-auto"
      />
      <Button
        :label="copied ? t('common.copied') : copyLabel"
        :icon="copied ? 'pi pi-check' : 'pi pi-copy'"
        :severity="copied ? 'success' : 'secondary'"
        size="small"
        outlined
        class="w-full sm:w-auto"
        @click="copyTelegramLink"
      />
    </div>
  </div>
</template>
