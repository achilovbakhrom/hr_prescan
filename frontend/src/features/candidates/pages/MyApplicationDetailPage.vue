<script setup lang="ts">
/**
 * MyApplicationDetailPage — full detail of a candidate's application.
 * Timeline (ApplicationTimeline) + vacancy card + score card + CV card.
 * Spec: docs/design/spec.md §9 — timeline events as glass chips, mono timestamps.
 */
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import CandidateTelegramShortcut from '@/shared/components/CandidateTelegramShortcut.vue'
import ApplicationStatusBadge from '../components/ApplicationStatusBadge.vue'
import ApplicationTimeline from '../components/ApplicationTimeline.vue'
import { useCandidateStore } from '../stores/candidate.store'
import { calculateOverallScore } from '../utils/score'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const applicationId = computed(() => route.params.id as string)
const application = computed(() => candidateStore.currentApplication)
const overallScore = computed(() => {
  if (!application.value) return null
  return calculateOverallScore({
    cvMatchScore: application.value.matchScore,
    prescanningScore: application.value.prescanningScore,
    interviewScore: application.value.interviewScore,
  })
})

onMounted(() => candidateStore.fetchMyApplicationDetail(applicationId.value))

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function goBack(): void {
  router.push({ name: ROUTE_NAMES.MY_APPLICATIONS })
}
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-6">
    <div class="flex items-center gap-3">
      <Button
        icon="pi pi-arrow-left"
        severity="secondary"
        text
        rounded
        aria-label="Back"
        @click="goBack"
      />
      <h1 class="text-2xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
        {{ t('candidates.overview') }}
      </h1>
    </div>

    <div v-if="candidateStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <p v-if="candidateStore.error" class="text-sm text-[color:var(--color-danger)]">
      {{ candidateStore.error }}
    </p>

    <template v-if="application">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Left: timeline + status -->
        <div class="lg:col-span-1">
          <GlassCard class="h-full">
            <ApplicationTimeline :application="application" />
            <div class="mt-5 flex justify-center">
              <ApplicationStatusBadge :status="application.status" />
            </div>
          </GlassCard>
        </div>

        <!-- Right: meta + score + cv -->
        <div class="space-y-6 lg:col-span-2">
          <GlassCard>
            <span
              class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
            >
              {{ t('nav.vacancies') }}
            </span>
            <p class="mt-1 text-xl font-semibold text-[color:var(--color-text-primary)]">
              {{ application.vacancyTitle }}
            </p>
            <p
              class="mt-2 flex items-center gap-1.5 text-sm text-[color:var(--color-text-secondary)]"
            >
              <i class="pi pi-calendar text-xs"></i>
              {{ t('candidates.myApplication.appliedOn') }}
              <span class="font-mono">{{ formatDate(application.createdAt) }}</span>
            </p>
          </GlassCard>

          <CandidateTelegramShortcut
            :prescan-token="application.prescanToken ?? null"
            :telegram-code="application.telegramCode ?? null"
            :title="t('candidates.myApplication.telegramVacancyTitle')"
            :hint="t('candidates.myApplication.telegramVacancyHint')"
            :open-label="t('candidates.application.openInTelegram')"
            :copy-label="t('candidates.application.copyTelegramLink')"
          />

          <GlassCard accent="ai">
            <span
              class="text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
            >
              {{ t('candidates.matchScore') }}
            </span>
            <p
              v-if="overallScore !== null"
              class="mt-2 font-mono text-5xl font-semibold leading-none tracking-tight text-[color:var(--color-accent-ai)]"
            >
              {{ overallScore }}%
            </p>
            <p v-else class="mt-2 text-sm text-[color:var(--color-text-muted)]">
              <i class="pi pi-spin pi-spinner mr-1.5"></i>
              {{ t('candidates.myApplication.cvBeingAnalyzed') }}
            </p>
            <div
              class="mt-5 grid grid-cols-1 gap-3 border-t border-[color:var(--color-border-soft)] pt-4 sm:grid-cols-3"
            >
              <div>
                <span class="text-xs text-[color:var(--color-text-muted)]">
                  {{ t('candidates.cvScore') }}
                </span>
                <p
                  class="mt-1 font-mono text-lg font-semibold text-[color:var(--color-text-primary)]"
                >
                  {{ application.matchScore !== null ? `${application.matchScore}%` : '—' }}
                </p>
              </div>
              <div>
                <span class="text-xs text-[color:var(--color-text-muted)]">
                  {{ t('candidates.prescanScore') }}
                </span>
                <p
                  class="mt-1 font-mono text-lg font-semibold text-[color:var(--color-text-primary)]"
                >
                  {{
                    application.prescanningScore !== null
                      ? `${application.prescanningScore}/10`
                      : '—'
                  }}
                </p>
              </div>
              <div>
                <span class="text-xs text-[color:var(--color-text-muted)]">
                  {{ t('candidates.interviewScore') }}
                </span>
                <p
                  class="mt-1 font-mono text-lg font-semibold text-[color:var(--color-text-primary)]"
                >
                  {{
                    application.interviewScore !== null ? `${application.interviewScore}/10` : '—'
                  }}
                </p>
              </div>
            </div>
          </GlassCard>

          <GlassCard :title="t('candidates.cv')">
            <Button
              v-if="application.cvFile"
              :label="application.cvOriginalFilename || t('candidates.myApplication.downloadCv')"
              icon="pi pi-download"
              size="small"
              severity="secondary"
              outlined
              :href="application.cvFile"
              as="a"
              target="_blank"
            />
            <p v-else class="text-sm text-[color:var(--color-text-muted)]">
              {{ t('candidates.myApplication.noCvUploaded') }}
            </p>
          </GlassCard>
        </div>
      </div>
    </template>
  </div>
</template>
