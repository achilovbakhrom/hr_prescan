<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { useCandidateStore } from '../stores/candidate.store'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import ApplicationReadyStep from '../components/ApplicationReadyStep.vue'
import PrescanChatOverlay from '../components/PrescanChatOverlay.vue'
import CvSelectionSection from '../components/CvSelectionSection.vue'
import type { Vacancy } from '@/shared/types/vacancy.types'
import type { EmployerCompany } from '@/features/employers/types/employer.types'

interface VacancyWithEmployer extends Vacancy {
  employer?: EmployerCompany
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const authStore = useAuthStore()
const vacancyId = route.params.vacancyId as string

const vacancy = ref<VacancyWithEmployer | null>(null)
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

function onFileSelect(event: FileUploadSelectEvent): void {
  cvFile.value = event.files[0] as File
}

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
  <div class="relative">
    <div class="mx-auto max-w-2xl px-4 py-6 sm:py-8">
      <div v-if="vacancyLoading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
      </div>

      <ApplicationReadyStep
        v-else-if="step === 'ready'"
        :prescan-url="prescanUrl"
        :link-copied="linkCopied"
        @start-prescanning="startPrescanning"
        @copy-link="copyLink"
      />

      <div v-else-if="step === 'done'" class="py-14 text-center">
        <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
          <i class="pi pi-check-circle text-3xl text-green-600"></i>
        </div>
        <h2 class="mb-2 text-xl font-bold text-gray-900">{{ t('candidates.application.prescanComplete') }}</h2>
        <p class="mb-7 text-sm text-gray-500">{{ t('candidates.application.prescanCompleteHint') }}</p>
        <RouterLink
          to="/jobs"
          class="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          <i class="pi pi-briefcase"></i>
          {{ t('candidates.application.browseVacancies') }}
        </RouterLink>
      </div>

      <template v-else>
        <RouterLink
          :to="`/jobs/${vacancyId}`"
          class="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <i class="pi pi-arrow-left mr-1"></i> {{ t('candidates.application.backToJob') }}
        </RouterLink>

        <h1 class="mb-1 text-xl font-bold sm:text-2xl">{{ t('candidates.application.title') }}</h1>
        <p v-if="vacancy" class="mb-1 text-sm text-gray-600 sm:text-base">{{ vacancy.title }}</p>
        <p
          v-if="vacancy && (vacancy.employer?.name || vacancy.companyName)"
          class="mb-4 text-xs text-gray-500 sm:mb-6 sm:text-sm"
        >
          <i class="pi pi-building mr-1"></i>{{ vacancy.employer?.name || vacancy.companyName }}
        </p>
        <div v-else class="mb-4 sm:mb-6"></div>

        <!-- Logged-in banner -->
        <div
          v-if="isLoggedIn"
          class="mb-4 flex items-center gap-2 rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-700"
        >
          <i class="pi pi-user"></i>
          {{ t('candidates.application.loggedInAs', { name: fullName }) }}
        </div>

        <p v-if="candidateStore.error" class="mb-4 text-sm text-red-600">
          {{ candidateStore.error }}
        </p>

        <form class="space-y-4 sm:space-y-5" @submit.prevent="handleSubmit">
          <!-- Name & Email: editable if guest, read-only if logged in -->
          <template v-if="isLoggedIn">
            <div
              class="grid grid-cols-1 gap-4 rounded-lg border border-gray-100 bg-gray-50 p-4 sm:grid-cols-2"
            >
              <div>
                <label class="block text-xs font-medium text-gray-500">{{
                  t('candidates.application.name')
                }}</label>
                <p class="text-sm font-medium text-gray-900">{{ name }}</p>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500">{{
                  t('candidates.application.email')
                }}</label>
                <p class="text-sm font-medium text-gray-900">{{ email }}</p>
              </div>
            </div>
          </template>
          <template v-else>
            <div>
              <label class="mb-1 block text-sm font-medium"
                >{{ t('candidates.application.name') }} *</label
              >
              <InputText
                v-model="name"
                class="w-full"
                placeholder="John Doe"
                :invalid="!!errors.name"
              />
              <small v-if="errors.name" class="text-red-500">{{ errors.name }}</small>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium"
                >{{ t('candidates.application.email') }} *</label
              >
              <InputText
                v-model="email"
                type="email"
                class="w-full"
                placeholder="john@example.com"
                :invalid="!!errors.email"
              />
              <small v-if="errors.email" class="text-red-500">{{ errors.email }}</small>
            </div>
          </template>

          <div>
            <label class="mb-1 block text-sm font-medium">{{
              t('candidates.application.phone')
            }}</label>
            <InputText v-model="phone" class="w-full" placeholder="+1 234 567 890" />
          </div>

          <!-- CV Section: smart if logged in, basic upload if guest -->
          <CvSelectionSection
            v-if="isLoggedIn"
            :cv-required="vacancy?.cvRequired ?? false"
            @update:cv-file="cvFile = $event"
            @update:cv-id="cvId = $event"
          />
          <div v-else>
            <label class="mb-1 block text-sm font-medium"
              >{{ t('candidates.application.uploadCv')
              }}<span v-if="vacancy?.cvRequired" class="text-red-500">*</span></label
            >
            <FileUpload
              mode="basic"
              accept=".pdf,.docx"
              :max-file-size="10000000"
              :choose-label="t('candidates.application.chooseCv')"
              :auto="false"
              @select="onFileSelect"
            />
            <small class="text-gray-400">{{ t('candidates.application.acceptedFormats') }}</small>
          </div>

          <Button
            type="submit"
            :label="t('candidates.application.submit')"
            icon="pi pi-send"
            class="w-full"
            :loading="candidateStore.loading"
          />
        </form>
      </template>
    </div>

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
