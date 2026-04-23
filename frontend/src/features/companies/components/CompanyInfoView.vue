<script setup lang="ts">
/**
 * CompanyInfoView — read-only company metadata panel.
 * Renders inside a GlassCard on CompanyDetailPage.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { resolveCountryDisplayName } from '@/shared/constants/countries'
import type { Company } from '../types/company.types'

const props = defineProps<{
  company: Company
}>()

const { t, locale } = useI18n()

const countryName = computed(() => resolveCountryDisplayName(props.company.country, locale.value))
</script>

<template>
  <div class="space-y-4">
    <div v-if="company.customIndustry">
      <p class="text-xs uppercase tracking-wider text-[color:var(--color-text-muted)]">
        {{ t('companies.industry') }}
      </p>
      <p class="mt-1 font-medium text-[color:var(--color-text-primary)]">
        {{ company.customIndustry }}
      </p>
    </div>
    <div>
      <p class="text-xs uppercase tracking-wider text-[color:var(--color-text-muted)]">
        {{ t('companies.country') }}
      </p>
      <p class="mt-1 font-medium text-[color:var(--color-text-primary)]">
        {{ countryName }}
      </p>
    </div>
    <div v-if="company.website">
      <p class="text-xs uppercase tracking-wider text-[color:var(--color-text-muted)]">
        {{ t('companies.website') }}
      </p>
      <a
        :href="company.website"
        target="_blank"
        rel="noopener noreferrer"
        class="mt-1 block font-medium text-[color:var(--color-accent)] hover:underline"
      >
        {{ company.website }}
      </a>
    </div>
    <div v-if="company.description">
      <p class="text-xs uppercase tracking-wider text-[color:var(--color-text-muted)]">
        {{ t('companies.description') }}
      </p>
      <p class="mt-1 whitespace-pre-line text-sm text-[color:var(--color-text-secondary)]">
        {{ company.description }}
      </p>
    </div>
  </div>
</template>
