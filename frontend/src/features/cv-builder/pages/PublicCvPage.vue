<script setup lang="ts">
/**
 * PublicCvPage — public share view for a candidate CV.
 *
 * T13 redesign: forces Vellum background on mount so the surrounding
 * ambience stays calm and print-friendly. Content body is a solid
 * paper-look card — NO glass on CV data for legibility. Body sections
 * live in PublicCvSections to keep this page ≤200 lines.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { cvBuilderService } from '../services/cv-builder.service'
import { useThemeStore } from '@/shared/stores/theme.store'
import type { PublicCvProfile } from '../types/cv-builder.types'
import { sanitizeHtml } from '@/shared/utils/sanitize'
import PublicCvSections from '../components/PublicCvSections.vue'

const { t } = useI18n()
const route = useRoute()
const themeStore = useThemeStore()

const profile = ref<PublicCvProfile | null>(null)
const loading = ref(false)
const error = ref(false)

onMounted(async () => {
  // Force Vellum for a calm, focused "paper" feel on CV share pages.
  if (themeStore.backgroundMode !== 'vellum') {
    themeStore.setBackgroundMode('vellum')
  }

  loading.value = true
  try {
    profile.value = await cvBuilderService.getPublicCv(route.params.token as string)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-3xl px-4 py-8">
    <div v-if="loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <i class="pi pi-eye-slash mb-3 text-4xl text-[color:var(--color-text-muted)]"></i>
      <p class="font-medium text-[color:var(--color-text-secondary)]">
        {{ t('publicCv.notFound') }}
      </p>
      <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
        {{ t('publicCv.notFoundHint') }}
      </p>
    </div>

    <article
      v-else-if="profile"
      class="cv-paper relative rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-base)] p-6 shadow-card sm:p-10"
    >
      <header class="mb-8">
        <h1 class="text-3xl font-semibold text-[color:var(--color-text-primary)]">
          {{ profile.firstName }} {{ profile.lastName }}
        </h1>
        <p v-if="profile.headline" class="mt-1 text-lg text-[color:var(--color-text-secondary)]">
          {{ profile.headline }}
        </p>
        <div
          class="mt-3 flex flex-wrap items-center gap-3 text-sm text-[color:var(--color-text-muted)]"
        >
          <span v-if="profile.location">
            <i class="pi pi-map-marker mr-1 text-xs"></i>{{ profile.location }}
          </span>
          <a
            v-if="profile.linkedinUrl"
            :href="profile.linkedinUrl"
            target="_blank"
            rel="noopener"
            class="text-[color:var(--color-accent)] hover:underline"
          >
            <i class="pi pi-linkedin mr-1 text-xs"></i>LinkedIn
          </a>
          <a
            v-if="profile.githubUrl"
            :href="profile.githubUrl"
            target="_blank"
            rel="noopener"
            class="text-[color:var(--color-text-secondary)] hover:underline"
          >
            <i class="pi pi-github mr-1 text-xs"></i>GitHub
          </a>
          <a
            v-if="profile.websiteUrl"
            :href="profile.websiteUrl"
            target="_blank"
            rel="noopener"
            class="text-[color:var(--color-accent)] hover:underline"
          >
            <i class="pi pi-globe mr-1 text-xs"></i>Website
          </a>
        </div>
      </header>

      <section v-if="profile.summary" class="mb-8">
        <h2
          class="mb-2 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('publicCv.summary') }}
        </h2>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div
          class="prose prose-sm max-w-none text-[color:var(--color-text-secondary)]"
          v-html="sanitizeHtml(profile.summary)"
        ></div>
      </section>

      <PublicCvSections :profile="profile" />
    </article>
  </div>
</template>

<style scoped>
@media print {
  .cv-paper {
    border: none;
    box-shadow: none;
    padding: 0;
  }
}
</style>
