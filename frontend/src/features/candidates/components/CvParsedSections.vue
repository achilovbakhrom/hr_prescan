<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import TranslatableText from '@/shared/components/TranslatableText.vue'
import { sanitizeHtml } from '@/shared/utils/sanitize'

const props = defineProps<{
  data: Record<string, unknown>
  cvSummaryTranslations?: Record<string, string>
  applicationId?: string
}>()

const { t } = useI18n()

const contacts = computed(() => {
  const c = props.data?.contacts as Record<string, string | null> | undefined
  if (!c) return []
  const iconMap: Record<string, string> = {
    email: 'pi-envelope',
    phone: 'pi-phone',
    location: 'pi-map-marker',
    linkedin: 'pi-linkedin',
    github: 'pi-github',
    website: 'pi-globe',
    telegram: 'pi-send',
  }
  return Object.entries(c)
    .filter(([, v]) => v)
    .map(([key, val]) => ({ label: key, value: val!, icon: iconMap[key] || 'pi-info-circle' }))
})

const skills = computed(() => (props.data?.skills as string[]) || [])
const experience = computed(() => (props.data?.experience as Record<string, string>[]) || [])
const education = computed(() => (props.data?.education as Record<string, string>[]) || [])
const languages = computed(() => {
  const langs = props.data?.languages
  if (!langs || !Array.isArray(langs)) return []
  return langs
    .map((l: unknown) => {
      if (typeof l === 'string') return { language: l, level: '' }
      const obj = l as Record<string, string>
      return { language: obj.language || '', level: obj.level || '' }
    })
    .filter((l: { language: string }) => l.language)
})
const certifications = computed(() => (props.data?.certifications as string[]) || [])
const summary = computed(() => (props.data?.summary as string) || '')
const experienceYears = computed(() => props.data?.experience_years as number | null)

function contactHref(label: string, value: string): string | undefined {
  if (label === 'email') return `mailto:${value}`
  if (label === 'phone') return `tel:${value}`
  if (label === 'linkedin' || label === 'github' || label === 'website')
    return value.startsWith('http') ? value : `https://${value}`
  if (label === 'telegram') return `https://t.me/${value.replace('@', '')}`
  return undefined
}
</script>

<template>
  <div class="space-y-6">
    <div v-if="summary">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.summary') }}</h3>
      <div class="rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3 text-sm text-gray-700">
        <TranslatableText
          v-if="applicationId"
          :text="summary"
          :translations="cvSummaryTranslations || {}"
          model="application"
          :object-id="applicationId"
          field="cv_summary"
        >
          <template #default="{ text }"
            ><div class="prose prose-sm max-w-none">{{ text }}</div></template
          >
        </TranslatableText>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div v-else class="prose prose-sm max-w-none" v-html="sanitizeHtml(summary)"></div>
        <span v-if="experienceYears" class="ml-1 text-gray-400"
          >({{ experienceYears }}+ {{ t('candidates.cvData.years') }})</span
        >
      </div>
    </div>

    <div v-if="contacts.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">
        {{ t('candidates.cvData.contacts') }}
      </h3>
      <div class="grid grid-cols-1 gap-2 md:grid-cols-2">
        <a
          v-for="c in contacts"
          :key="c.label"
          :href="contactHref(c.label, c.value)"
          target="_blank"
          rel="noopener"
          class="flex items-center gap-2.5 rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 px-3 py-2 text-sm transition-colors hover:bg-gray-100"
          :class="contactHref(c.label, c.value) ? 'cursor-pointer' : 'cursor-default'"
        >
          <i class="pi text-gray-400" :class="c.icon"></i>
          <div class="min-w-0 flex-1">
            <p class="text-[10px] font-medium text-gray-400 dark:text-gray-500 uppercase">{{ c.label }}</p>
            <p class="truncate text-sm text-gray-700">{{ c.value }}</p>
          </div>
        </a>
      </div>
    </div>

    <div v-if="skills.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.skills') }}</h3>
      <div class="flex flex-wrap gap-2">
        <Tag v-for="skill in skills" :key="skill" :value="skill" severity="info" />
      </div>
    </div>

    <div v-if="experience.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">
        {{ t('candidates.cvData.experience') }}
      </h3>
      <div class="space-y-3 border-l-2 border-blue-200 dark:border-blue-800 pl-4">
        <div v-for="(entry, idx) in experience" :key="idx" class="relative">
          <div class="absolute -left-[1.35rem] top-1 h-2.5 w-2.5 rounded-full bg-blue-500"></div>
          <p class="font-medium">{{ entry.position || entry.role }}</p>
          <p class="text-sm text-gray-600">
            {{ entry.company
            }}<span v-if="entry.duration" class="text-gray-400">
              &middot; {{ entry.duration }}</span
            >
          </p>
          <p v-if="entry.description" class="mt-1 text-sm text-gray-500">{{ entry.description }}</p>
        </div>
      </div>
    </div>

    <div v-if="education.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">
        {{ t('candidates.cvData.education') }}
      </h3>
      <div class="space-y-3">
        <div
          v-for="(entry, idx) in education"
          :key="idx"
          class="rounded border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-3"
        >
          <p class="font-medium">
            {{ entry.degree
            }}<template v-if="entry.field">
              {{ t('candidates.cvData.inField') }} {{ entry.field }}</template
            >
          </p>
          <p class="text-sm text-gray-600">
            {{ entry.institution
            }}<span v-if="entry.year" class="text-gray-400"> &middot; {{ entry.year }}</span>
          </p>
        </div>
      </div>
    </div>

    <div v-if="languages.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">
        {{ t('candidates.cvData.languages') }}
      </h3>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(lang, idx) in languages"
          :key="idx"
          class="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 px-3 py-1.5 text-sm"
        >
          {{ lang.language
          }}<span v-if="lang.level" class="ml-1 text-gray-400">-- {{ lang.level }}</span>
        </span>
      </div>
    </div>

    <div v-if="certifications.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">
        {{ t('candidates.cvData.certifications') }}
      </h3>
      <ul class="list-inside list-disc space-y-1 text-sm text-gray-700">
        <li v-for="(cert, idx) in certifications" :key="idx">{{ cert }}</li>
      </ul>
    </div>
  </div>
</template>
