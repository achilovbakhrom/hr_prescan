<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAnalyticsStore } from '../stores/analytics.store'
import GlassCard from '@/shared/components/GlassCard.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import AnalyticsProcessCards from '../components/AnalyticsProcessCards.vue'
import AnalyticsScoreDistribution from '../components/AnalyticsScoreDistribution.vue'
import AnalyticsStatCards from '../components/AnalyticsStatCards.vue'
import AnalyticsStatusBreakdown from '../components/AnalyticsStatusBreakdown.vue'
import AnalyticsVacancyPerformanceTable from '../components/AnalyticsVacancyPerformanceTable.vue'
import HiringFunnel from '../components/HiringFunnel.vue'

const { t } = useI18n()
const analyticsStore = useAnalyticsStore()

onMounted(() => {
  analyticsStore.fetchAnalytics()
})

const funnel = computed(() => analyticsStore.analytics?.funnel)
const vacancyPerformance = computed(() => analyticsStore.analytics?.vacancyPerformance ?? [])
const insights = computed(() => analyticsStore.analytics?.interviewInsights)
const statusBreakdown = computed(() => analyticsStore.analytics?.statusBreakdown ?? [])
const scoreDistribution = computed(() => analyticsStore.analytics?.scoreDistribution ?? [])
const processMetrics = computed(() => analyticsStore.analytics?.processMetrics ?? null)
</script>

<template>
  <div class="w-full">
    <!-- Sticky glass toolbar -->
    <GlassSurface
      level="1"
      class="sticky top-4 z-10 mb-6 flex items-center justify-between gap-4 px-5 py-3"
    >
      <div class="min-w-0">
        <p
          class="font-mono text-[11px] uppercase tracking-[0.18em] text-[color:var(--color-text-muted)]"
        >
          {{ t('analytics.title') }}
        </p>
        <h1
          class="truncate text-xl font-semibold text-[color:var(--color-text-primary)] sm:text-2xl"
        >
          {{ t('analytics.subtitle') }}
        </h1>
      </div>
    </GlassSurface>

    <div v-if="analyticsStore.loading" class="flex items-center justify-center py-20">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>
    <GlassCard v-else-if="analyticsStore.error" class="border-[color:var(--color-danger)]">
      <div class="flex flex-col items-center py-6 text-center text-[color:var(--color-danger)]">
        <i class="pi pi-exclamation-triangle mb-2 text-2xl"></i>
        <p class="text-sm">{{ analyticsStore.error }}</p>
      </div>
    </GlassCard>

    <template v-else-if="analyticsStore.analytics">
      <AnalyticsStatCards
        :total-applications="funnel?.total ?? 0"
        :total-interviews="insights?.total ?? 0"
        :completion-rate="insights?.completionRate ?? 0"
        :average-score="insights?.averageScore ?? null"
      />

      <AnalyticsProcessCards :metrics="processMetrics" />

      <div class="mb-6 grid gap-6 xl:grid-cols-3">
        <HiringFunnel :funnel="funnel ?? null" />
        <AnalyticsStatusBreakdown :items="statusBreakdown" />
        <AnalyticsScoreDistribution :buckets="scoreDistribution" />
      </div>

      <AnalyticsVacancyPerformanceTable :vacancies="vacancyPerformance" />
    </template>
  </div>
</template>
