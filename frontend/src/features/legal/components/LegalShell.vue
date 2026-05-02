<script setup lang="ts">
/**
 * LegalShell — solid reading layout for privacy + terms pages.
 *
 * Per spec §9: "solid reading layout — NO glass on content body (legibility
 * for long-form text). Nav (if any) can be glass; body stays solid."
 *
 * Legal routes live inside PublicLayout, so the animated background +
 * PublicHeader + FloatingBackgroundPicker are already in place. This shell
 * just provides the centered prose container + page header.
 */
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

defineProps<{
  title: string
  lastUpdated: string
}>()

const router = useRouter()
const { t } = useI18n()
function goBack(): void {
  router.back()
}
</script>

<template>
  <div class="py-10">
    <div class="mx-auto max-w-3xl px-4 sm:px-6">
      <!-- Page header -->
      <div class="mb-6">
        <Button
          :label="t('common.back')"
          icon="pi pi-arrow-left"
          text
          severity="secondary"
          class="mb-4 -ml-2"
          @click="goBack"
        />
        <h1
          class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
        >
          {{ title }}
        </h1>
        <p class="mt-2 text-sm text-[color:var(--color-text-muted)]">
          {{ t('legal.lastUpdated', { date: lastUpdated }) }}
        </p>
      </div>

      <!-- Solid reading body. Tailwind Typography plugin provides sensible
           defaults; we override colors to respect our tokens and dark mode. -->
      <article
        class="legal-prose prose prose-slate max-w-none rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-base)] p-6 shadow-sm sm:p-10 dark:prose-invert"
      >
        <slot />
      </article>
    </div>
  </div>
</template>

<style scoped>
/* Token-aware prose colors — keeps legibility regardless of theme and
   doesn't fight with the AnimatedBackground peeking at the edges. */
.legal-prose :deep(h2) {
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: 1.25rem;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}
.legal-prose :deep(h2):first-child {
  margin-top: 0;
}
.legal-prose :deep(p),
.legal-prose :deep(li) {
  color: var(--color-text-secondary);
  line-height: 1.65;
}
.legal-prose :deep(a) {
  color: var(--color-accent);
  text-decoration: none;
}
.legal-prose :deep(a:hover) {
  text-decoration: underline;
}
.legal-prose :deep(strong) {
  color: var(--color-text-primary);
}
</style>
