<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Tag from 'primevue/tag'
import Button from 'primevue/button'

const { t } = useI18n()

interface MatchDetails {
  overall?: number
  criteria_scores?: Record<string, number>
  notes?: string
  matching_skills?: string[]
  missing_skills?: string[]
}

const props = defineProps<{
  data: Record<string, unknown> | null
  cvFile?: string
  cvFilename?: string
  matchScore?: number | null
  matchDetails?: MatchDetails | null
}>()

const emit = defineEmits<{
  downloadCv: []
}>()

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
  return langs.map((l: unknown) => {
    if (typeof l === 'string') return { language: l, level: '' }
    const obj = l as Record<string, string>
    return { language: obj.language || '', level: obj.level || '' }
  }).filter((l: { language: string }) => l.language)
})
const certifications = computed(() => (props.data?.certifications as string[]) || [])
const summary = computed(() => (props.data?.summary as string) || '')
const experienceYears = computed(() => props.data?.experience_years as number | null)

const hasData = computed(() => {
  if (!props.data) return false
  return skills.value.length > 0 || experience.value.length > 0 || education.value.length > 0 || summary.value
})

function formatCriteriaName(name: string): string {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function scoreColor(score: number): string {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-blue-500'
  if (score >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}

function scoreBg(score: number): string {
  if (score >= 80) return 'bg-green-100 text-green-700'
  if (score >= 60) return 'bg-blue-100 text-blue-700'
  if (score >= 40) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

function contactHref(label: string, value: string): string | undefined {
  if (label === 'email') return `mailto:${value}`
  if (label === 'phone') return `tel:${value}`
  if (label === 'linkedin' || label === 'github' || label === 'website') {
    return value.startsWith('http') ? value : `https://${value}`
  }
  if (label === 'telegram') return `https://t.me/${value.replace('@', '')}`
  return undefined
}
</script>

<template>
  <!-- Download CV button -->
  <div v-if="props.cvFile" class="mb-4 flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3">
    <i class="pi pi-file-pdf text-2xl text-red-500"></i>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-medium text-gray-700">{{ props.cvFilename || t('candidates.cvData.file') }}</p>
      <p class="text-xs text-gray-400">{{ t('candidates.cvData.clickToDownload') }}</p>
    </div>
    <Button
      :label="t('candidates.cv')"
      icon="pi pi-download"
      size="small"
      outlined
      @click="emit('downloadCv')"
    />
  </div>

  <!-- CV Processing indicator -->
  <div
    v-if="props.cvFile && (props.matchScore === null || props.matchScore === undefined) && !hasData"
    class="mb-4 flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 p-4"
  >
    <i class="pi pi-spinner pi-spin text-lg text-blue-500"></i>
    <div>
      <p class="text-sm font-medium text-blue-800">{{ t('candidates.cvData.analyzing') }}</p>
      <p class="text-xs text-blue-600">{{ t('candidates.cvData.extracting') }}</p>
    </div>
  </div>

  <!-- CV Match Score -->
  <div v-if="props.matchScore !== null && props.matchScore !== undefined" class="mb-4 rounded-xl border border-gray-200 bg-white p-4">
    <div class="flex items-center gap-4">
      <div
        class="flex h-16 w-16 shrink-0 items-center justify-center rounded-full"
        :class="scoreBg(props.matchScore)"
      >
        <span class="text-xl font-bold">{{ props.matchScore }}%</span>
      </div>
      <div class="flex-1">
        <p class="text-sm font-semibold text-gray-700">{{ t('candidates.matchScore') }}</p>
        <p v-if="props.matchDetails?.notes" class="mt-0.5 text-xs text-gray-500">{{ props.matchDetails.notes }}</p>
      </div>
    </div>

    <div v-if="props.matchDetails?.criteria_scores" class="mt-3 grid grid-cols-3 gap-2">
      <div
        v-for="(score, name) in props.matchDetails.criteria_scores"
        :key="name"
        class="rounded-lg bg-gray-50 p-2 text-center"
      >
        <p class="text-xs text-gray-500">{{ formatCriteriaName(String(name)) }}</p>
        <p class="text-sm font-bold" :class="score >= 70 ? 'text-green-600' : score >= 40 ? 'text-yellow-600' : 'text-red-600'">{{ score }}%</p>
      </div>
    </div>

    <div v-if="props.matchDetails?.matching_skills?.length || props.matchDetails?.missing_skills?.length" class="mt-3 space-y-2">
      <div v-if="props.matchDetails?.matching_skills?.length">
        <p class="mb-1 text-xs font-medium text-gray-500">{{ t('candidates.cvData.matchingSkills') }}</p>
        <div class="flex flex-wrap gap-1">
          <Tag v-for="s in props.matchDetails.matching_skills" :key="s" :value="s" severity="success" class="!text-[10px]" />
        </div>
      </div>
      <div v-if="props.matchDetails?.missing_skills?.length">
        <p class="mb-1 text-xs font-medium text-gray-500">{{ t('candidates.cvData.missingSkills') }}</p>
        <div class="flex flex-wrap gap-1">
          <Tag v-for="s in props.matchDetails.missing_skills" :key="s" :value="s" severity="danger" class="!text-[10px]" />
        </div>
      </div>
    </div>
  </div>

  <div v-if="!hasData" class="py-8 text-center text-gray-400">
    <i class="pi pi-file mb-2 text-3xl"></i>
    <p>{{ t('candidates.cvData.notParsed') }}</p>
  </div>

  <div v-if="hasData" class="space-y-6">
    <!-- Summary -->
    <div v-if="summary">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.summary') }}</h3>
      <div class="rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm text-gray-700">
        <div class="prose prose-sm max-w-none" v-html="summary"></div>
        <span v-if="experienceYears" class="ml-1 text-gray-400">({{ experienceYears }}+ {{ t('candidates.cvData.years') }})</span>
      </div>
    </div>

    <!-- Contacts -->
    <div v-if="contacts.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.contacts') }}</h3>
      <div class="grid grid-cols-1 gap-2 md:grid-cols-2">
        <a
          v-for="c in contacts"
          :key="c.label"
          :href="contactHref(c.label, c.value)"
          target="_blank"
          rel="noopener"
          class="flex items-center gap-2.5 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-sm transition-colors hover:bg-gray-100"
          :class="contactHref(c.label, c.value) ? 'cursor-pointer' : 'cursor-default'"
        >
          <i class="pi text-gray-400" :class="c.icon"></i>
          <div class="min-w-0 flex-1">
            <p class="text-[10px] font-medium text-gray-400 uppercase">{{ c.label }}</p>
            <p class="truncate text-sm text-gray-700">{{ c.value }}</p>
          </div>
        </a>
      </div>
    </div>

    <!-- Skills -->
    <div v-if="skills.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.skills') }}</h3>
      <div class="flex flex-wrap gap-2">
        <Tag
          v-for="skill in skills"
          :key="skill"
          :value="skill"
          severity="info"
        />
      </div>
    </div>

    <!-- Experience -->
    <div v-if="experience.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.experience') }}</h3>
      <div class="space-y-3 border-l-2 border-blue-200 pl-4">
        <div
          v-for="(entry, idx) in experience"
          :key="idx"
          class="relative"
        >
          <div class="absolute -left-[1.35rem] top-1 h-2.5 w-2.5 rounded-full bg-blue-500"></div>
          <p class="font-medium">{{ entry.position || entry.role }}</p>
          <p class="text-sm text-gray-600">
            {{ entry.company }}
            <span v-if="entry.duration" class="text-gray-400">
              &middot; {{ entry.duration }}
            </span>
          </p>
          <p v-if="entry.description" class="mt-1 text-sm text-gray-500">
            {{ entry.description }}
          </p>
        </div>
      </div>
    </div>

    <!-- Education -->
    <div v-if="education.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.education') }}</h3>
      <div class="space-y-3">
        <div
          v-for="(entry, idx) in education"
          :key="idx"
          class="rounded border border-gray-100 bg-gray-50 p-3"
        >
          <p class="font-medium">{{ entry.degree }}<template v-if="entry.field"> {{ t('candidates.cvData.inField') }} {{ entry.field }}</template></p>
          <p class="text-sm text-gray-600">
            {{ entry.institution }}
            <span v-if="entry.year" class="text-gray-400">
              &middot; {{ entry.year }}
            </span>
          </p>
        </div>
      </div>
    </div>

    <!-- Languages -->
    <div v-if="languages.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.languages') }}</h3>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(lang, idx) in languages"
          :key="idx"
          class="rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-sm"
        >
          {{ lang.language }}<span v-if="lang.level" class="ml-1 text-gray-400">— {{ lang.level }}</span>
        </span>
      </div>
    </div>

    <!-- Certifications -->
    <div v-if="certifications.length">
      <h3 class="mb-2 text-sm font-semibold text-gray-600">{{ t('candidates.cvData.certifications') }}</h3>
      <ul class="list-inside list-disc space-y-1 text-sm text-gray-700">
        <li v-for="(cert, idx) in certifications" :key="idx">{{ cert }}</li>
      </ul>
    </div>
  </div>
</template>
