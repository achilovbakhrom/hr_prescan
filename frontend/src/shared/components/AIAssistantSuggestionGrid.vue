<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

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
    title: t('aiAssistant.suggestions.findCandidates.title'),
    description: t('aiAssistant.suggestions.findCandidates.description'),
    prompt: t('aiAssistant.suggestions.findCandidates.prompt'),
  },
  {
    icon: 'pi pi-briefcase',
    title: t('aiAssistant.suggestions.vacancies.title'),
    description: t('aiAssistant.suggestions.vacancies.description'),
    prompt: t('aiAssistant.suggestions.vacancies.prompt'),
  },
  {
    icon: 'pi pi-chart-line',
    title: t('aiAssistant.suggestions.analytics.title'),
    description: t('aiAssistant.suggestions.analytics.description'),
    prompt: t('aiAssistant.suggestions.analytics.prompt'),
  },
  {
    icon: 'pi pi-send',
    title: t('aiAssistant.suggestions.followUp.title'),
    description: t('aiAssistant.suggestions.followUp.description'),
    prompt: t('aiAssistant.suggestions.followUp.prompt'),
  },
])

const candidateSuggestions = computed(() => [
  {
    icon: 'pi pi-search',
    title: t('aiAssistant.suggestions.searchJobs.title'),
    description: t('aiAssistant.suggestions.searchJobs.description'),
    prompt: t('aiAssistant.suggestions.searchJobs.prompt'),
  },
  {
    icon: 'pi pi-file-edit',
    title: t('aiAssistant.suggestions.improveCv.title'),
    description: t('aiAssistant.suggestions.improveCv.description'),
    prompt: t('aiAssistant.suggestions.improveCv.prompt'),
  },
  {
    icon: 'pi pi-list-check',
    title: t('aiAssistant.suggestions.applications.title'),
    description: t('aiAssistant.suggestions.applications.description'),
    prompt: t('aiAssistant.suggestions.applications.prompt'),
  },
])

const suggestions = computed(() =>
  props.isCandidate ? candidateSuggestions.value : hrSuggestions.value,
)
</script>

<template>
  <div class="grid gap-2">
    <button
      v-for="item in suggestions"
      :key="item.title"
      type="button"
      class="group flex min-h-[76px] w-full items-start gap-3 rounded-lg border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] p-3 text-left transition-colors hover:border-[color:var(--color-accent)] hover:bg-[color:var(--color-accent-soft)]"
      @click="emit('send', item.prompt)"
    >
      <span
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-[color:var(--color-surface-sunken)] text-[color:var(--color-accent)]"
      >
        <i :class="item.icon" class="text-sm"></i>
      </span>
      <span class="min-w-0">
        <span class="block text-sm font-semibold text-[color:var(--color-text-primary)]">
          {{ item.title }}
        </span>
        <span class="mt-0.5 block text-xs leading-5 text-[color:var(--color-text-secondary)]">
          {{ item.description }}
        </span>
      </span>
    </button>
  </div>
</template>
