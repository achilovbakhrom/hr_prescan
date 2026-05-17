<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AIAssistantSuggestionCard from './AIAssistantSuggestionCard.vue'

const props = defineProps<{
  isCandidate: boolean
}>()

const emit = defineEmits<{
  send: [prompt: string]
}>()

const { t } = useI18n()

const hrSuggestions = computed(() => [
  {
    icon: 'pi pi-users',
    accent: 'blue',
    featured: true,
    title: t('aiAssistant.suggestions.findCandidates.title'),
    description: t('aiAssistant.suggestions.findCandidates.description'),
    prompt: t('aiAssistant.suggestions.findCandidates.prompt'),
  },
  {
    icon: 'pi pi-briefcase',
    accent: 'emerald',
    featured: true,
    title: t('aiAssistant.suggestions.createVacancy.title'),
    description: t('aiAssistant.suggestions.createVacancy.description'),
    prompt: t('aiAssistant.suggestions.createVacancy.prompt'),
  },
  {
    icon: 'pi pi-list-check',
    accent: 'emerald',
    featured: false,
    title: t('aiAssistant.suggestions.vacancies.title'),
    description: t('aiAssistant.suggestions.vacancies.description'),
    prompt: t('aiAssistant.suggestions.vacancies.prompt'),
  },
  {
    icon: 'pi pi-chart-line',
    accent: 'amber',
    featured: true,
    title: t('aiAssistant.suggestions.analytics.title'),
    description: t('aiAssistant.suggestions.analytics.description'),
    prompt: t('aiAssistant.suggestions.analytics.prompt'),
  },
  {
    icon: 'pi pi-send',
    accent: 'rose',
    featured: false,
    title: t('aiAssistant.suggestions.followUp.title'),
    description: t('aiAssistant.suggestions.followUp.description'),
    prompt: t('aiAssistant.suggestions.followUp.prompt'),
  },
])

const candidateSuggestions = computed(() => [
  {
    icon: 'pi pi-search',
    accent: 'blue',
    featured: true,
    title: t('aiAssistant.suggestions.searchJobs.title'),
    description: t('aiAssistant.suggestions.searchJobs.description'),
    prompt: t('aiAssistant.suggestions.searchJobs.prompt'),
  },
  {
    icon: 'pi pi-file-edit',
    accent: 'emerald',
    featured: true,
    title: t('aiAssistant.suggestions.improveCv.title'),
    description: t('aiAssistant.suggestions.improveCv.description'),
    prompt: t('aiAssistant.suggestions.improveCv.prompt'),
  },
  {
    icon: 'pi pi-list-check',
    accent: 'amber',
    featured: false,
    title: t('aiAssistant.suggestions.applications.title'),
    description: t('aiAssistant.suggestions.applications.description'),
    prompt: t('aiAssistant.suggestions.applications.prompt'),
  },
])

const suggestions = computed(() =>
  (props.isCandidate ? candidateSuggestions.value : hrSuggestions.value).map((item) => ({
    ...item,
    tooltip: `${item.description} ${item.prompt}`,
  })),
)
</script>

<template>
  <div class="grid gap-3">
    <AIAssistantSuggestionCard
      v-for="item in suggestions"
      :key="item.title"
      :item="item"
      :featured-label="t('aiAssistant.featuredLabel')"
      @send="emit('send', $event)"
    />
  </div>
</template>
