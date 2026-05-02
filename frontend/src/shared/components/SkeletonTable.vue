<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  rows?: number
  columns?: number
  showHeader?: boolean
}

withDefaults(defineProps<Props>(), {
  rows: 5,
  columns: 4,
  showHeader: true,
})

const { t } = useI18n()
</script>

<template>
  <div
    class="overflow-hidden rounded-xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-800 shadow-sm"
    role="status"
    :aria-label="t('common.aria.loadingTable')"
    aria-busy="true"
  >
    <!-- Table header -->
    <div
      v-if="showHeader"
      class="flex gap-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 px-6 py-3"
    >
      <div
        v-for="col in columns"
        :key="col"
        class="h-4 flex-1 animate-pulse rounded-full bg-gray-200"
        :class="col === 1 ? 'max-w-xs' : ''"
      ></div>
    </div>

    <!-- Table rows -->
    <div class="divide-y divide-gray-50">
      <div v-for="row in rows" :key="row" class="flex items-center gap-4 px-6 py-4">
        <!-- Row checkbox / icon placeholder -->
        <div class="h-4 w-4 shrink-0 animate-pulse rounded bg-gray-200"></div>

        <!-- Column cells -->
        <div v-for="col in columns" :key="col" class="flex-1">
          <div
            class="animate-pulse rounded-full bg-gray-200"
            :class="[col === 1 ? 'h-4 w-3/4' : 'h-3 w-1/2', row % 3 === 0 ? 'opacity-60' : '']"
          ></div>
        </div>

        <!-- Actions placeholder -->
        <div class="flex shrink-0 gap-2">
          <div class="h-7 w-7 animate-pulse rounded-lg bg-gray-200"></div>
          <div class="h-7 w-7 animate-pulse rounded-lg bg-gray-200"></div>
        </div>
      </div>
    </div>
  </div>
</template>
