<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CandidateBasePanel from '../components/CandidateBasePanel.vue'
import { useCandidateBaseStore } from '../stores/candidateBase.store'

const { t } = useI18n()
const candidateStore = useCandidateBaseStore()
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ t('nav.candidateBase') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ candidateStore.candidates.length }} {{ t('nav.candidates').toLowerCase() }}
        </p>
      </div>
    </div>
    <CandidateBasePanel />
  </div>
</template>
