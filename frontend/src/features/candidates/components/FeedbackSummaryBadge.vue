<script setup lang="ts">
import type { FeedbackSummary } from '@/shared/types/candidate.types'

defineProps<{
  summary?: FeedbackSummary
}>()
</script>

<template>
  <span
    v-if="summary?.total"
    class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700"
    :title="`Manager feedback: ${summary.advance} advance, ${summary.maybe} maybe, ${summary.reject} reject`"
  >
    <i class="pi pi-comments text-[10px]"></i>
    {{ summary.total }}
    <span v-if="summary.avgRating">· {{ summary.avgRating }}/5</span>
  </span>
</template>
