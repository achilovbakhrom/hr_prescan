<script setup lang="ts">
/**
 * CvBuilderPreview — right-side live preview, paper-look (solid, not glass).
 * Shows headline + skills + experience + education preview.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import type { CandidateProfile } from '../types/cv-builder.types'

const props = defineProps<{
  profile: CandidateProfile | null
}>()

const { t } = useI18n()
const authStore = useAuthStore()

const fullName = computed(() => {
  const first = authStore.user?.firstName || ''
  const last = authStore.user?.lastName || ''
  const combined = `${first} ${last}`.trim()
  return combined || t('cvBuilder.preview.yourName') || 'Your name'
})

const headline = computed(
  () => props.profile?.headline || t('cvBuilder.preview.headline') || 'Professional title',
)
const email = computed(() => authStore.user?.email || '')
const phone = computed(() => authStore.user?.phone || '')
</script>

<template>
  <aside class="sticky top-6 hidden xl:block">
    <div class="cv-preview">
      <div class="cv-preview__paper">
        <div class="cv-preview__label">
          <i class="pi pi-eye text-[10px]"></i>
          {{ t('cvBuilder.preview.title') || 'Live preview' }}
        </div>
        <div v-if="profile" class="flex flex-col gap-5">
          <header class="border-b border-[color:var(--color-border-soft)] pb-3">
            <h2 class="text-xl font-semibold text-[color:var(--color-text-primary)]">
              {{ fullName }}
            </h2>
            <p class="mt-0.5 text-sm text-[color:var(--color-text-secondary)]">
              {{ headline }}
            </p>
            <div
              class="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[color:var(--color-text-muted)]"
            >
              <span v-if="email" class="flex items-center gap-1">
                <i class="pi pi-envelope text-[10px]"></i>{{ email }}
              </span>
              <span v-if="phone" class="flex items-center gap-1">
                <i class="pi pi-phone text-[10px]"></i>{{ phone }}
              </span>
              <span v-if="profile.location" class="flex items-center gap-1">
                <i class="pi pi-map-marker text-[10px]"></i>{{ profile.location }}
              </span>
            </div>
          </header>

          <section v-if="profile.skills?.length">
            <h3 class="cv-preview__h3">{{ t('cvBuilder.tabs.skills') }}</h3>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="skill in profile.skills.slice(0, 10)"
                :key="skill.slug"
                class="rounded-full bg-[color:var(--color-surface-sunken)] px-2 py-0.5 text-[11px] text-[color:var(--color-text-secondary)]"
              >
                {{ skill.name }}
              </span>
            </div>
          </section>

          <section v-if="profile.workExperiences?.length">
            <h3 class="cv-preview__h3">{{ t('cvBuilder.tabs.experience') }}</h3>
            <div class="space-y-2">
              <div
                v-for="exp in profile.workExperiences.slice(0, 3)"
                :key="exp.id"
                class="text-[11px]"
              >
                <p class="font-semibold text-[color:var(--color-text-primary)]">
                  {{ exp.position }}
                </p>
                <p class="text-[color:var(--color-text-muted)]">
                  {{ exp.companyName }}
                </p>
              </div>
            </div>
          </section>

          <section v-if="profile.educations?.length">
            <h3 class="cv-preview__h3">{{ t('cvBuilder.tabs.education') }}</h3>
            <div class="space-y-2">
              <div v-for="edu in profile.educations.slice(0, 2)" :key="edu.id" class="text-[11px]">
                <p class="font-semibold text-[color:var(--color-text-primary)]">
                  {{ edu.degree }}
                </p>
                <p class="text-[color:var(--color-text-muted)]">
                  {{ edu.institution }}
                </p>
              </div>
            </div>
          </section>
        </div>
        <p v-else class="text-xs text-[color:var(--color-text-muted)]">
          {{ t('cvBuilder.preview.empty') || 'Start adding your details to see the preview.' }}
        </p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.cv-preview {
  width: 100%;
}
.cv-preview__paper {
  background: var(--color-surface-base);
  border: 1px solid var(--color-border-soft);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  aspect-ratio: 1 / 1.414; /* A4 */
  overflow: hidden;
  position: relative;
  font-family: var(--font-sans);
}
.cv-preview__label {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-muted);
  background: var(--color-surface-sunken);
  border-radius: 9999px;
}
.cv-preview__h3 {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-accent-ai);
  margin-bottom: 0.5rem;
}
</style>
