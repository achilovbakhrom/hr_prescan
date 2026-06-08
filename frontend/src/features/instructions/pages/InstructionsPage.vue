<script setup lang="ts">
/**
 * InstructionsPage — "How it works" guide.
 *
 * Walks an HR user through the five core flows end to end, each illustrated
 * with real screenshots captured from the app. Two-column on desktop (sticky
 * ToC + content), single column on mobile.
 */
import InstructionsToc from '../components/InstructionsToc.vue'
import InstructionsFlowSection from '../components/InstructionsFlowSection.vue'
import { GUIDE_FLOWS } from '../data/flows'
</script>

<template>
  <div class="mx-auto max-w-6xl">
    <header class="mb-8">
      <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
        How it works
      </h1>
      <p class="mt-2 max-w-2xl text-sm text-[color:var(--color-text-muted)]">
        A step-by-step walkthrough of PreScreen AI — from posting a role to reviewing scored
        candidates, plus what applicants experience. Click any screenshot to view it full size.
      </p>
    </header>

    <div class="grid grid-cols-1 gap-8 lg:grid-cols-[220px_1fr]">
      <!-- Table of contents (desktop) -->
      <aside class="hidden lg:block">
        <InstructionsToc />
      </aside>

      <!-- Flow sections -->
      <div class="flex min-w-0 flex-col gap-6">
        <InstructionsFlowSection
          v-for="(flow, i) in GUIDE_FLOWS"
          :key="flow.id"
          :flow="flow"
          :index="i + 1"
        />
      </div>
    </div>
  </div>
</template>
