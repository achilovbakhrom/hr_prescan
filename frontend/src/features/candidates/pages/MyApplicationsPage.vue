<script setup lang="ts">
/**
 * MyApplicationsPage — candidate's view of their applications.
 * Card grid; each card = glass surface + vacancy meta + status pill + CTA.
 * Spec: docs/design/spec.md §9.
 */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import CandidateTelegramShortcut from '@/shared/components/CandidateTelegramShortcut.vue'
import MyApplicationCard from '../components/MyApplicationCard.vue'
import { useCandidateStore } from '../stores/candidate.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()
const candidateStore = useCandidateStore()

const latestTelegramApplication = computed(
  () => candidateStore.myApplications.find((app) => app.prescanToken || app.telegramCode) ?? null,
)

onMounted(() => candidateStore.fetchMyApplications())

function openDetail(id: string): void {
  router.push({ name: ROUTE_NAMES.MY_APPLICATION_DETAIL, params: { id } })
}

function browseJobs(): void {
  router.push('/jobs')
}
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-6">
    <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
          {{ t('nav.myApplications') }}
        </h1>
        <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
          {{
            t('candidates.myApplication.trackYourApps') ||
            'Track your application pipeline in one place.'
          }}
        </p>
      </div>
      <Button
        :label="t('landing.hero.browseJobs')"
        icon="pi pi-search"
        severity="secondary"
        outlined
        size="small"
        @click="browseJobs"
      />
    </header>

    <p v-if="candidateStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ candidateStore.error }}
    </p>

    <CandidateTelegramShortcut
      :prescan-token="latestTelegramApplication?.prescanToken ?? null"
      :telegram-code="latestTelegramApplication?.telegramCode ?? null"
      :title="t('candidates.myApplication.telegramTitle')"
      :hint="t('candidates.myApplication.telegramHint')"
      :open-label="t('candidates.application.openInTelegram')"
      :copy-label="t('candidates.application.copyTelegramLink')"
      compact
    />

    <div v-if="candidateStore.loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <div
      v-else-if="candidateStore.myApplications.length === 0"
      class="rounded-lg border border-dashed border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-sunken)] px-6 py-16 text-center"
    >
      <i class="pi pi-inbox mb-3 text-4xl text-[color:var(--color-text-muted)]"></i>
      <p class="text-base font-medium text-[color:var(--color-text-secondary)]">
        {{ t('candidates.myApplication.none') || 'No applications yet' }}
      </p>
      <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
        {{
          t('candidates.myApplication.browseHint') ||
          'Browse jobs to submit your first application.'
        }}
      </p>
      <Button
        :label="t('landing.hero.browseJobs')"
        icon="pi pi-search"
        size="small"
        class="mt-5"
        @click="browseJobs"
      />
    </div>

    <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
      <MyApplicationCard
        v-for="app in candidateStore.myApplications"
        :key="app.id"
        :application="app"
        @open="openDetail"
      />
    </div>

    <GlassCard v-if="candidateStore.myApplications.length > 0" class="!p-4">
      <div class="flex items-center justify-between text-sm">
        <span class="font-medium text-[color:var(--color-text-secondary)]">
          {{ t('common.total') || 'Total' }}
        </span>
        <span class="font-mono text-base font-semibold text-[color:var(--color-text-primary)]">
          {{ candidateStore.myApplications.length }}
        </span>
      </div>
    </GlassCard>
  </div>
</template>
