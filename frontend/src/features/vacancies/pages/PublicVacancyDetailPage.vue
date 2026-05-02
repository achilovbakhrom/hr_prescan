<script setup lang="ts">
/**
 * PublicVacancyDetailPage — public vacancy detail + share-token view.
 *
 * T13 redesign: glass header block on top of ambient background, content
 * organised into glass cards. Sticky Apply CTA floats bottom-right on
 * mobile; inline at top on desktop. Sub-blocks are extracted so this
 * page stays ≤200 lines.
 */
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import { vacancyService } from '../services/vacancy.service'
import { formatDate } from '../composables/useVacancyLabels'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Vacancy } from '../types/vacancy.types'
import type { Company } from '@/features/companies/types/company.types'
import { sanitizeHtml } from '@/shared/utils/sanitize'
import TranslatableText from '@/shared/components/TranslatableText.vue'
import PublicVacancyHeader from '../components/PublicVacancyHeader.vue'
import PublicVacancyCompanyCard from '../components/PublicVacancyCompanyCard.vue'

interface VacancyWithCompany extends Vacancy {
  company?: Company
  companyName?: string | null
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const vacancy = ref<VacancyWithCompany | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const isShareRoute = computed(() => route.name === 'job-share')

onMounted(async () => {
  loading.value = true
  try {
    if (isShareRoute.value) {
      vacancy.value = await vacancyService.getByShareToken(route.params.token as string)
    } else {
      vacancy.value = await vacancyService.getPublicDetail(route.params.id as string)
    }
  } catch {
    error.value = 'Failed to load vacancy details'
  } finally {
    loading.value = false
  }
})

function goApply(): void {
  if (!vacancy.value || vacancy.value.canApply === false) return
  router.push(`/jobs/${vacancy.value.id}/apply`)
}
</script>

<template>
  <div class="relative">
    <div class="mx-auto max-w-3xl px-4 py-6 sm:py-8">
      <button
        class="mb-4 inline-flex items-center gap-1.5 text-sm text-[color:var(--color-text-muted)] ease-ios transition-colors hover:text-[color:var(--color-text-primary)]"
        @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
      >
        <i class="pi pi-arrow-left text-xs"></i>
        {{ t('common.back') }}
      </button>

      <div v-if="loading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
      </div>
      <GlassCard v-else-if="error" class="text-center text-[color:var(--color-danger)]">
        <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
        <p>{{ error }}</p>
      </GlassCard>

      <template v-else-if="vacancy">
        <PublicVacancyHeader :vacancy="vacancy" @apply="goApply" />

        <GlassCard v-if="vacancy.description" class="mb-5" :title="t('vacancies.form.description')">
          <TranslatableText
            :text="vacancy.description"
            :translations="vacancy.descriptionTranslations || {}"
            model="vacancy"
            :object-id="vacancy.id"
            field="description"
            scope="public"
            :share-token="isShareRoute ? String(route.params.token) : undefined"
            @translated="(tr) => (vacancy!.descriptionTranslations = tr)"
          >
            <template #default="{ text }">
              <!-- eslint-disable-next-line vue/no-v-html -->
              <div
                class="prose prose-sm max-w-none text-[color:var(--color-text-secondary)]"
                v-html="sanitizeHtml(text)"
              ></div>
            </template>
          </TranslatableText>
        </GlassCard>

        <GlassCard
          v-if="vacancy.requirements"
          class="mb-5"
          :title="t('vacancies.form.requirements')"
        >
          <TranslatableText
            :text="vacancy.requirements"
            :translations="vacancy.requirementsTranslations || {}"
            model="vacancy"
            :object-id="vacancy.id"
            field="requirements"
            scope="public"
            :share-token="isShareRoute ? String(route.params.token) : undefined"
            @translated="(tr) => (vacancy!.requirementsTranslations = tr)"
          >
            <template #default="{ text }">
              <p class="whitespace-pre-line text-sm text-[color:var(--color-text-secondary)]">
                {{ text }}
              </p>
            </template>
          </TranslatableText>
        </GlassCard>

        <GlassCard
          v-if="vacancy.responsibilities"
          class="mb-5"
          :title="t('vacancies.form.responsibilities')"
        >
          <TranslatableText
            :text="vacancy.responsibilities"
            :translations="vacancy.responsibilitiesTranslations || {}"
            model="vacancy"
            :object-id="vacancy.id"
            field="responsibilities"
            scope="public"
            :share-token="isShareRoute ? String(route.params.token) : undefined"
            @translated="(tr) => (vacancy!.responsibilitiesTranslations = tr)"
          >
            <template #default="{ text }">
              <p class="whitespace-pre-line text-sm text-[color:var(--color-text-secondary)]">
                {{ text }}
              </p>
            </template>
          </TranslatableText>
        </GlassCard>

        <PublicVacancyCompanyCard v-if="vacancy.company" :company="vacancy.company" />

        <div
          v-if="vacancy.deadline"
          class="text-xs text-[color:var(--color-text-muted)] sm:text-sm"
        >
          <i class="pi pi-clock mr-1"></i>{{ t('vacancies.form.deadline') }}:
          <span class="font-mono">{{ formatDate(vacancy.deadline) }}</span>
        </div>

        <div class="fixed bottom-4 right-4 z-40 sm:hidden">
          <GlassSurface v-if="vacancy.canApply !== false" level="float" class="rounded-full !p-0">
            <Button
              :label="t('jobBoard.apply')"
              icon="pi pi-send"
              class="!rounded-full"
              size="large"
              @click="goApply"
            />
          </GlassSurface>
        </div>
      </template>
    </div>
  </div>
</template>
