<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const items = computed(() => [
  { icon: 'pi pi-filter', text: t('vacancies.form.screeningIntroFilter') },
  { icon: 'pi pi-sparkles', text: t('vacancies.form.screeningIntroAi') },
  { icon: 'pi pi-link', text: t('vacancies.form.screeningIntroLink') },
])
</script>

<template>
  <div
    class="mb-5 rounded-2xl border border-[color:var(--color-border-glass)] bg-[color:var(--color-accent-ai-soft)] p-4"
  >
    <div class="flex items-start gap-3">
      <span
        class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/80 text-[color:var(--color-accent-ai)] shadow-sm dark:bg-white/10"
      >
        <i class="pi pi-sparkles"></i>
      </span>
      <div>
        <h2 class="text-sm font-semibold text-[color:var(--color-text-primary)]">
          {{ t('vacancies.form.screeningIntroTitle') }}
        </h2>
        <p class="mt-1 text-sm leading-relaxed text-[color:var(--color-text-secondary)]">
          {{ t('vacancies.form.screeningIntroHint') }}
        </p>
      </div>
    </div>
    <div class="mt-4 grid gap-2 sm:grid-cols-3">
      <div
        v-for="item in items"
        :key="item.text"
        class="flex items-center gap-2 rounded-xl bg-white/70 px-3 py-2 text-xs font-medium text-[color:var(--color-text-secondary)] dark:bg-white/10"
      >
        <i :class="item.icon" class="text-[color:var(--color-accent-ai)]"></i>
        <span>{{ item.text }}</span>
      </div>
    </div>
  </div>
</template>
