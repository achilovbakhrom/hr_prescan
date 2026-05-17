<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlassCard from '@/shared/components/GlassCard.vue'
import type { StatusBreakdownItem } from '../types/analytics.types'

const props = defineProps<{
  items: StatusBreakdownItem[]
}>()

const { t } = useI18n()

const rows = computed(() =>
  props.items.map((item) => ({
    ...item,
    label: t(`candidates.status.${item.status}`),
    width: `${Math.max(item.percentage, item.count > 0 ? 3 : 0)}%`,
  })),
)

const total = computed(() => props.items.reduce((sum, item) => sum + item.count, 0))
</script>

<template>
  <GlassCard>
    <template #header>
      <h2
        class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('analytics.statusBreakdown') }}
      </h2>
    </template>

    <div v-if="total > 0" class="flex flex-col gap-3">
      <div v-for="item in rows" :key="item.status" class="flex flex-col gap-1.5">
        <div class="flex items-center justify-between gap-3">
          <span class="text-sm font-medium text-[color:var(--color-text-secondary)]">
            {{ item.label }}
          </span>
          <span class="font-mono text-xs text-[color:var(--color-text-muted)]">
            {{ item.count }} / {{ item.percentage }}%
          </span>
        </div>
        <div class="h-2 w-full overflow-hidden rounded-full bg-[color:var(--color-border-soft)]">
          <div
            class="h-full rounded-full bg-[color:var(--color-accent-ai)] transition-all duration-500 ease-ios"
            :style="{ width: item.width }"
          ></div>
        </div>
      </div>
    </div>
    <div
      v-else
      class="flex flex-col items-center py-8 text-center text-[color:var(--color-text-muted)]"
    >
      <i class="pi pi-list-check mb-2 text-2xl"></i>
      <p class="text-sm">{{ t('analytics.noData') }}</p>
    </div>
  </GlassCard>
</template>
