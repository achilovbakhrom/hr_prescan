<script setup lang="ts">
/**
 * InstructionsPage — "How it works" guide.
 *
 * Walks an HR user through the five core flows end to end, each illustrated
 * with real screenshots captured from the app. Content and screenshots are
 * localized to the current UI language. Two-column on desktop (sticky ToC +
 * content), single column on mobile.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InstructionsToc from '../components/InstructionsToc.vue'
import InstructionsFlowSection from '../components/InstructionsFlowSection.vue'
import { getGuide } from '../data/guide'

const { locale } = useI18n()
const guide = computed(() => getGuide(locale.value))
</script>

<template>
  <div class="mx-auto max-w-7xl">
    <header class="mb-8">
      <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
        {{ guide.page.title }}
      </h1>
      <p class="mt-2 max-w-2xl text-sm text-[color:var(--color-text-muted)]">
        {{ guide.page.subtitle }}
      </p>
    </header>

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-[240px_1fr]">
      <!-- Table of contents (desktop) -->
      <aside class="hidden lg:block">
        <InstructionsToc :flows="guide.flows" :label="guide.page.onThisPage" />
      </aside>

      <!-- Flow sections -->
      <div class="flex min-w-0 flex-col gap-6">
        <InstructionsFlowSection
          v-for="(flow, i) in guide.flows"
          :key="flow.id"
          :flow="flow"
          :index="i + 1"
          :for-hr="guide.page.forHr"
          :for-candidates="guide.page.forCandidates"
        />
      </div>
    </div>
  </div>
</template>
