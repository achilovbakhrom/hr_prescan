<script setup lang="ts">
/**
 * PublicVacancyCompanyCard — "About the company" block on
 * PublicVacancyDetailPage. Extracted to keep the page file small.
 */
import GlassCard from '@/shared/components/GlassCard.vue'
import type { Company } from '@/features/companies/types/company.types'

defineProps<{
  company: Company
}>()
</script>

<template>
  <GlassCard class="mb-5" :title="company.name">
    <div class="flex items-center gap-3 sm:gap-4">
      <div
        v-if="company.logo"
        class="bg-glass-2 flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-lg sm:h-14 sm:w-14"
      >
        <img :src="company.logo" :alt="company.name" class="h-full w-full object-contain" />
      </div>
      <div
        v-else
        class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-[color:var(--color-accent-ai-soft)] text-[color:var(--color-accent-ai)] sm:h-14 sm:w-14"
      >
        <i class="pi pi-building text-lg sm:text-2xl"></i>
      </div>
      <div class="min-w-0">
        <p
          v-if="company.customIndustry"
          class="text-xs text-[color:var(--color-text-muted)] sm:text-sm"
        >
          {{ company.customIndustry }}
        </p>
        <a
          v-if="company.website"
          :href="company.website"
          target="_blank"
          rel="noopener noreferrer"
          class="text-xs text-[color:var(--color-accent)] hover:underline sm:text-sm"
        >
          {{ company.website }}
        </a>
      </div>
    </div>
    <p
      v-if="company.description"
      class="mt-3 whitespace-pre-line text-sm text-[color:var(--color-text-secondary)]"
    >
      {{ company.description }}
    </p>
  </GlassCard>
</template>
