<script setup lang="ts">
/**
 * PublicCvSections — all body sections (experience/education/skills/etc.)
 * of the public CV page. Split from PublicCvPage to stay ≤200 lines.
 */
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import type { PublicCvProfile } from '../types/cv-builder.types'

defineProps<{
  profile: PublicCvProfile
}>()

const { t } = useI18n()

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { year: 'numeric', month: 'short' })
}

function proficiencyLabel(value: string): string {
  const map: Record<string, string> = {
    native: t('cvBuilder.proficiencies.native'),
    advanced: t('cvBuilder.proficiencies.advanced'),
    upper_intermediate: t('cvBuilder.proficiencies.upperIntermediate'),
    intermediate: t('cvBuilder.proficiencies.intermediate'),
    elementary: t('cvBuilder.proficiencies.elementary'),
    beginner: t('cvBuilder.proficiencies.beginner'),
  }
  return map[value] || value
}
</script>

<template>
  <section v-if="profile.workExperiences.length" class="mb-8">
    <h2
      class="mb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('publicCv.experience') }}
    </h2>
    <div class="space-y-4 border-l-2 border-[color:var(--color-accent-ai-soft)] pl-4">
      <div v-for="exp in profile.workExperiences" :key="exp.id" class="relative">
        <span
          class="absolute -left-[1.35rem] top-1.5 h-2.5 w-2.5 rounded-full bg-[color:var(--color-accent-ai)]"
        ></span>
        <p class="font-semibold text-[color:var(--color-text-primary)]">{{ exp.position }}</p>
        <p class="text-sm text-[color:var(--color-text-secondary)]">
          {{ exp.companyName }}
          <span v-if="exp.location" class="text-[color:var(--color-text-muted)]">
            &middot; {{ exp.location }}
          </span>
        </p>
        <p class="font-mono text-xs text-[color:var(--color-text-muted)]">
          {{ formatDate(exp.startDate) }} &mdash;
          {{ exp.isCurrent ? t('publicCv.present') : formatDate(exp.endDate) }}
        </p>
        <p
          v-if="exp.description"
          class="mt-1 whitespace-pre-line text-sm text-[color:var(--color-text-secondary)]"
        >
          {{ exp.description }}
        </p>
      </div>
    </div>
  </section>

  <section v-if="profile.educations.length" class="mb-8">
    <h2
      class="mb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('publicCv.education') }}
    </h2>
    <div class="space-y-3">
      <div
        v-for="edu in profile.educations"
        :key="edu.id"
        class="rounded-md border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-3"
      >
        <p class="font-semibold text-[color:var(--color-text-primary)]">
          {{ edu.degree || edu.institution }}
        </p>
        <p v-if="edu.degree" class="text-sm text-[color:var(--color-text-secondary)]">
          {{ edu.institution }}
        </p>
        <p v-if="edu.fieldOfStudy" class="text-sm text-[color:var(--color-text-muted)]">
          {{ edu.fieldOfStudy }}
        </p>
        <p class="font-mono text-xs text-[color:var(--color-text-muted)]">
          {{ formatDate(edu.startDate) }}
          <template v-if="edu.endDate"> &mdash; {{ formatDate(edu.endDate) }}</template>
        </p>
      </div>
    </div>
  </section>

  <section v-if="profile.skills.length" class="mb-8">
    <h2
      class="mb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('publicCv.skills') }}
    </h2>
    <div class="flex flex-wrap gap-2">
      <Tag v-for="skill in profile.skills" :key="skill.slug" :value="skill.name" severity="info" />
    </div>
  </section>

  <section v-if="profile.languages.length" class="mb-8">
    <h2
      class="mb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('publicCv.languages') }}
    </h2>
    <div class="flex flex-wrap gap-2">
      <span
        v-for="lang in profile.languages"
        :key="lang.id"
        class="rounded-md border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] px-3 py-1.5 text-sm"
      >
        {{ lang.language.name }}
        <span class="ml-1 text-[color:var(--color-text-muted)]">
          &mdash; {{ proficiencyLabel(lang.proficiency) }}
        </span>
      </span>
    </div>
  </section>

  <section v-if="profile.certifications.length" class="mb-0">
    <h2
      class="mb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('publicCv.certifications') }}
    </h2>
    <div class="space-y-2">
      <div
        v-for="cert in profile.certifications"
        :key="cert.id"
        class="flex items-center gap-2 text-sm"
      >
        <i class="pi pi-verified text-[color:var(--color-accent)]"></i>
        <span class="font-medium text-[color:var(--color-text-primary)]">{{ cert.name }}</span>
        <span v-if="cert.issuingOrganization" class="text-[color:var(--color-text-muted)]">
          &mdash; {{ cert.issuingOrganization }}
        </span>
        <a
          v-if="cert.credentialUrl"
          :href="cert.credentialUrl"
          target="_blank"
          rel="noopener"
          class="text-[color:var(--color-accent)] hover:underline"
        >
          <i class="pi pi-external-link text-xs"></i>
        </a>
      </div>
    </div>
  </section>
</template>
