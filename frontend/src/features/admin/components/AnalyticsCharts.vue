<script setup lang="ts">
/**
 * AnalyticsCharts — 2×2 admin chart grid composed from per-chart components.
 * Each chart is a ChartCard (glass frame) wrapping a solid Chart.js canvas.
 */
import RevenueTrendChart from './RevenueTrendChart.vue'
import InterviewVolumeChart from './InterviewVolumeChart.vue'
import SubscriptionDistChart from './SubscriptionDistChart.vue'
import UserRegistrationsChart from './UserRegistrationsChart.vue'
import type { PlatformAnalytics } from '../types/admin.types'

const props = defineProps<{ analytics: PlatformAnalytics }>()

const monthlyRevenue =
  props.analytics.estimatedMonthlyRevenue || props.analytics.monthlyRevenue || 0
</script>

<template>
  <div class="grid grid-cols-1 gap-3 lg:grid-cols-2">
    <RevenueTrendChart :monthly-revenue="monthlyRevenue" />
    <InterviewVolumeChart :volume="analytics.monthlyInterviewVolume" />
    <SubscriptionDistChart :distribution="analytics.subscriptionDistribution" />
    <UserRegistrationsChart :registrations="analytics.monthlyRegistrations" />
  </div>
</template>
