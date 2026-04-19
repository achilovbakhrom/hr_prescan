<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Company } from '../types/company.types'

defineProps<{ company: Company }>()

const { t } = useI18n()
</script>

<template>
  <div
    class="space-y-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6"
  >
    <div v-if="company.customIndustry">
      <p class="text-sm text-gray-500">{{ t('companies.industry') }}</p>
      <p class="font-medium">{{ company.customIndustry }}</p>
    </div>
    <div>
      <p class="text-sm text-gray-500">{{ t('companies.country') }}</p>
      <p class="font-medium">{{ company.country }}</p>
    </div>
    <div v-if="company.website">
      <p class="text-sm text-gray-500">{{ t('companies.website') }}</p>
      <a
        :href="company.website"
        target="_blank"
        rel="noopener noreferrer"
        class="font-medium text-blue-600 dark:text-blue-400 hover:underline"
      >
        {{ company.website }}
      </a>
    </div>
    <div v-if="company.description">
      <p class="text-sm text-gray-500">{{ t('companies.description') }}</p>
      <p class="whitespace-pre-line text-gray-700">{{ company.description }}</p>
    </div>
  </div>
</template>
