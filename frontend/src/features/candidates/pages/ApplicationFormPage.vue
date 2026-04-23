<script setup lang="ts">
/**
 * ApplicationFormPage — candidate applies to a public vacancy.
 *
 * T13 redesign: steps sit inside glass cards; a glass progress breadcrumb
 * sits above indicating where the user is (Form → Ready → Prescan done).
 * Each step is extracted into its own component to stay under 200 lines.
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { useCandidateStore } from '../stores/candidate.store'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import ApplicationReadyStep from '../components/ApplicationReadyStep.vue'
import ApplicationFormCard from '../components/ApplicationFormCard.vue'
import ApplicationDoneStep from '../components/ApplicationDoneStep.vue'
import ApplicationStepsBar from '../components/ApplicationStepsBar.vue'
import PrescanChatOverlay from '../components/PrescanChatOverlay.vue'
import type { Vacancy } from '@/shared/types/vacancy.types'
import type { Company } from '@/features/companies/types/company.types'

interface VacancyWithCompany extends Vacancy {
  company?: Company
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const authStore = useAuthStore()
const vacancyId = route.params.vacancyId as string

const vacancy = ref<VacancyWithCompany | null>(null)
const vacancyLoading = ref(false)
const name = ref('')
const email = ref('')
const phone = ref('')
const cvFile = ref<File | null>(null)
const cvId = ref<string | null>(null)
const errors = ref<Record<string, string>>({})

const step = ref<'form' | 'ready' | 'done'>('form')
const prescanToken = ref<string | null>(null)
const linkCopied = ref(false)
const showChatOverlay = ref(false)
const prescanDismissed = ref(false)

const isLoggedIn = computed(() => authStore.isAuthenticated)
const fullName = computed(() => {
  const u = authStore.user
  return u ? `${u.firstName} ${u.lastName}`.trim() || u.email : ''
})

const prescanUrl = computed(() =>
  prescanToken.value ? `${window.location.origin}/interview/${prescanToken.value}` : '',
)
const chatUrl = computed(() => (prescanToken.value ? `/interview/${prescanToken.value}/chat` : ''))

const steps = computed(() => [
  { id: 'form', label: t('candidates.application.title') },
  { id: 'ready', label: t('candidates.application.prescanReady') },
  { id: 'done', label: t('candidates.application.prescanComplete') },
])

onMounted(async () => {
  vacancyLoading.value = true
  try {
    vacancy.value = await vacancyService.getPublicDetail(vacancyId)
  } catch {
    vacancy.value = null
  } finally {
    vacancyLoading.value = false
  }

  if (isLoggedIn.value && authStore.user) {
    name.value = fullName.value
    email.value = authStore.user.email
  }
})

function validate(): boolean {
  errors.value = {}
  if (!name.value.trim()) errors.value.name = t('candidates.application.validation.nameRequired')
  if (!email.value.trim()) {
    errors.value.email = t('candidates.application.validation.emailRequired')
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.value.email = t('candidates.application.validation.emailInvalid')
  }
  return Object.keys(errors.value).length === 0
}

async function handleSubmit(): Promise<void> {
  if (!validate()) return
  try {
    const application = await candidateStore.submitApplication(vacancyId, {
      candidateName: name.value.trim(),
      candidateEmail: email.value.trim(),
      candidatePhone: phone.value.trim() || undefined,
      cvFile: cvFile.value ?? undefined,
      cvId: cvId.value ?? undefined,
    })
    const resp = application as unknown as Record<string, unknown>
    prescanToken.value = (resp.prescanToken ??
      resp.prescan_token ??
      resp.interviewToken ??
      resp.interview_token ??
      null) as string | null
    step.value = 'ready'
  } catch {
    /* store handles error */
  }
}

function startPrescanning(): void {
  if (prescanToken.value) showChatOverlay.value = true
}

function handlePrescanComplete(): void {
  showChatOverlay.value = false
  step.value = 'done'
}

function openInFullScreen(): void {
  router.push({ name: ROUTE_NAMES.INTERVIEW_GATEWAY, params: { token: prescanToken.value! } })
}

async function copyLink(): Promise<void> {
  try {
    await navigator.clipboard.writeText(prescanUrl.value)
    linkCopied.value = true
    setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  } catch {
    /* fallback */
  }
}
</script>

<template>
  <div class="relative mx-auto max-w-2xl px-4 py-6 sm:py-8">
    <ApplicationStepsBar :steps="steps" :current="step" class="mb-5" />

    <div v-if="vacancyLoading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <ApplicationReadyStep
      v-else-if="step === 'ready'"
      :prescan-url="prescanUrl"
      :link-copied="linkCopied"
      :prescan-token="prescanToken"
      :telegram-code="vacancy?.telegramCode ?? null"
      @start-prescanning="startPrescanning"
      @copy-link="copyLink"
    />

    <ApplicationDoneStep v-else-if="step === 'done'" />

    <ApplicationFormCard
      v-else
      :vacancy-id="vacancyId"
      :vacancy="vacancy"
      :is-logged-in="isLoggedIn"
      :full-name="fullName"
      :name="name"
      :email="email"
      :phone="phone"
      :errors="errors"
      :candidate-store-error="candidateStore.error"
      :candidate-store-loading="candidateStore.loading"
      @update:name="name = $event"
      @update:email="email = $event"
      @update:phone="phone = $event"
      @update:cv-file="cvFile = $event"
      @update:cv-id="cvId = $event"
      @submit="handleSubmit"
    />

    <PrescanChatOverlay
      :show-overlay="showChatOverlay"
      :prescan-token="prescanToken"
      :chat-url="chatUrl"
      :show-minimized="!showChatOverlay && step === 'ready' && !!prescanToken && !prescanDismissed"
      @open-full-screen="openInFullScreen"
      @minimize="showChatOverlay = false"
      @restore="showChatOverlay = true"
      @dismiss="prescanDismissed = true"
      @completed="handlePrescanComplete"
    />
  </div>
</template>
