<script setup lang="ts">
/**
 * Sticky table of contents. Desktop only — on mobile the sections simply
 * stack and the ToC is hidden to keep the page focused.
 */
import type { GuideFlow } from '../data/guide.types'

defineProps<{
  flows: GuideFlow[]
  label: string
}>()

function scrollTo(id: string): void {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <nav class="sticky top-24" aria-label="Guide contents">
    <p class="mb-3 px-3 text-[11px] font-semibold uppercase tracking-widest text-gray-400">
      {{ label }}
    </p>
    <ul class="flex flex-col gap-0.5">
      <li v-for="(flow, i) in flows" :key="flow.id">
        <button
          type="button"
          class="flex w-full items-start gap-3 rounded-lg px-3 py-2 text-left text-[13px] font-medium leading-snug text-gray-600 transition-colors hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800"
          @click="scrollTo(flow.id)"
        >
          <i
            :class="flow.icon"
            class="mt-0.5 shrink-0 text-sm text-[color:var(--color-accent)]"
            aria-hidden="true"
          ></i>
          <span class="min-w-0 break-words">{{ i + 1 }}. {{ flow.title }}</span>
        </button>
      </li>
    </ul>
  </nav>
</template>
