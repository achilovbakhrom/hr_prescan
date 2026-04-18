<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import Tag from 'primevue/tag'
import { cvBuilderService } from '../services/cv-builder.service'
import type { PublicCvProfile } from '../types/cv-builder.types'
import { sanitizeHtml } from '@/shared/utils/sanitize'

const { t } = useI18n()
const route = useRoute()

const profile = ref<PublicCvProfile | null>(null)
const loading = ref(false)
const error = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    profile.value = await cvBuilderService.getPublicCv(route.params.token as string)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})

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
  <div class="mx-auto max-w-3xl px-4 py-8">
    <div v-if="loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div v-else-if="error" class="py-16 text-center">
      <i class="pi pi-eye-slash mb-3 text-4xl text-gray-300"></i>
      <p class="font-medium text-gray-600">{{ t('publicCv.notFound') }}</p>
      <p class="mt-1 text-sm text-gray-400">{{ t('publicCv.notFoundHint') }}</p>
    </div>

    <template v-else-if="profile">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          {{ profile.firstName }} {{ profile.lastName }}
        </h1>
        <p v-if="profile.headline" class="mt-1 text-lg text-gray-600">{{ profile.headline }}</p>
        <div class="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500">
          <span v-if="profile.location">
            <i class="pi pi-map-marker mr-1 text-xs"></i>{{ profile.location }}
          </span>
          <a
            v-if="profile.linkedinUrl"
            :href="profile.linkedinUrl"
            target="_blank"
            rel="noopener"
            class="text-blue-600 hover:underline"
          >
            <i class="pi pi-linkedin mr-1 text-xs"></i>LinkedIn
          </a>
          <a
            v-if="profile.githubUrl"
            :href="profile.githubUrl"
            target="_blank"
            rel="noopener"
            class="text-gray-700 hover:underline"
          >
            <i class="pi pi-github mr-1 text-xs"></i>GitHub
          </a>
          <a
            v-if="profile.websiteUrl"
            :href="profile.websiteUrl"
            target="_blank"
            rel="noopener"
            class="text-blue-600 hover:underline"
          >
            <i class="pi pi-globe mr-1 text-xs"></i>Website
          </a>
        </div>
      </div>

      <!-- Summary -->
      <div v-if="profile.summary" class="mb-8">
        <h2 class="mb-2 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('publicCv.summary') }}
        </h2>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div
          class="prose prose-sm max-w-none text-gray-700"
          v-html="sanitizeHtml(profile.summary)"
        ></div>
      </div>

      <!-- Experience -->
      <div v-if="profile.workExperiences.length" class="mb-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('publicCv.experience') }}
        </h2>
        <div class="space-y-4 border-l-2 border-blue-200 pl-4">
          <div v-for="exp in profile.workExperiences" :key="exp.id" class="relative">
            <div
              class="absolute -left-[1.35rem] top-1.5 h-2.5 w-2.5 rounded-full bg-blue-500"
            ></div>
            <p class="font-semibold text-gray-900">{{ exp.position }}</p>
            <p class="text-sm text-gray-600">
              {{ exp.companyName }}
              <span v-if="exp.location" class="text-gray-400"> &middot; {{ exp.location }}</span>
            </p>
            <p class="text-xs text-gray-400">
              {{ formatDate(exp.startDate) }} &mdash;
              {{ exp.isCurrent ? t('publicCv.present') : formatDate(exp.endDate) }}
            </p>
            <p v-if="exp.description" class="mt-1 whitespace-pre-line text-sm text-gray-600">
              {{ exp.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- Education -->
      <div v-if="profile.educations.length" class="mb-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('publicCv.education') }}
        </h2>
        <div class="space-y-3">
          <div
            v-for="edu in profile.educations"
            :key="edu.id"
            class="rounded-lg border border-gray-100 bg-gray-50 p-3"
          >
            <p class="font-semibold text-gray-900">{{ edu.degree || edu.institution }}</p>
            <p v-if="edu.degree" class="text-sm text-gray-600">{{ edu.institution }}</p>
            <p v-if="edu.fieldOfStudy" class="text-sm text-gray-500">{{ edu.fieldOfStudy }}</p>
            <p class="text-xs text-gray-400">
              {{ formatDate(edu.startDate) }}
              <template v-if="edu.endDate"> &mdash; {{ formatDate(edu.endDate) }}</template>
            </p>
          </div>
        </div>
      </div>

      <!-- Skills -->
      <div v-if="profile.skills.length" class="mb-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('publicCv.skills') }}
        </h2>
        <div class="flex flex-wrap gap-2">
          <Tag
            v-for="skill in profile.skills"
            :key="skill.slug"
            :value="skill.name"
            severity="info"
          />
        </div>
      </div>

      <!-- Languages -->
      <div v-if="profile.languages.length" class="mb-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('publicCv.languages') }}
        </h2>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="lang in profile.languages"
            :key="lang.id"
            class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-sm"
          >
            {{ lang.language.name }}
            <span class="ml-1 text-gray-400">&mdash; {{ proficiencyLabel(lang.proficiency) }}</span>
          </span>
        </div>
      </div>

      <!-- Certifications -->
      <div v-if="profile.certifications.length" class="mb-8">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('publicCv.certifications') }}
        </h2>
        <div class="space-y-2">
          <div
            v-for="cert in profile.certifications"
            :key="cert.id"
            class="flex items-center gap-2 text-sm"
          >
            <i class="pi pi-verified text-blue-500"></i>
            <span class="font-medium text-gray-900">{{ cert.name }}</span>
            <span v-if="cert.issuingOrganization" class="text-gray-500"
              >&mdash; {{ cert.issuingOrganization }}</span
            >
            <a
              v-if="cert.credentialUrl"
              :href="cert.credentialUrl"
              target="_blank"
              rel="noopener"
              class="text-blue-600 hover:underline"
            >
              <i class="pi pi-external-link text-xs"></i>
            </a>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
