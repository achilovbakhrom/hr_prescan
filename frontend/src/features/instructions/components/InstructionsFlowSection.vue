<script setup lang="ts">
/**
 * One guide flow: header (icon, title, audience badge, summary) followed by an
 * ordered list of steps. The section id is the scroll anchor for the ToC.
 */
import GlassCard from '@/shared/components/GlassCard.vue'
import InstructionsStep from './InstructionsStep.vue'
import type { GuideFlow } from '../data/guide.types'

defineProps<{
  flow: GuideFlow
  index: number
  forHr: string
  forCandidates: string
}>()
</script>

<template>
  <section :id="flow.id" class="scroll-mt-24">
    <GlassCard>
      <header
        class="mb-6 flex items-start gap-4 border-b border-[color:var(--color-border-soft)] pb-5"
      >
        <span
          class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
          aria-hidden="true"
        >
          <i :class="flow.icon" class="text-lg"></i>
        </span>
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <h2 class="text-xl font-semibold text-[color:var(--color-text-primary)]">
              {{ index }}. {{ flow.title }}
            </h2>
            <span
              class="rounded-full px-2 py-0.5 text-[11px] font-medium"
              :class="
                flow.audience === 'hr'
                  ? 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
                  : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300'
              "
            >
              {{ flow.audience === 'hr' ? forHr : forCandidates }}
            </span>
          </div>
          <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">{{ flow.summary }}</p>
        </div>
      </header>

      <ol class="flex flex-col">
        <InstructionsStep
          v-for="(step, i) in flow.steps"
          :key="step.image"
          :step="step"
          :index="i + 1"
        />
      </ol>
    </GlassCard>
  </section>
</template>
