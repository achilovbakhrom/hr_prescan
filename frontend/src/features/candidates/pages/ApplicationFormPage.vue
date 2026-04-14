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
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { Vacancy } from '@/shared/types/vacancy.types'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const candidateStore = useCandidateStore()
const vacancyId = route.params.vacancyId as string

const vacancy = ref<Vacancy | null>(null)
const vacancyLoading = ref(false)
const name = ref('')
const email = ref('')
const phone = ref('')
const cvFile = ref<File | null>(null)
const errors = ref<Record<string, string>>({})

// Post-submit state
const step = ref<'form' | 'ready'>('form')
const prescanToken = ref<string | null>(null)
const linkCopied = ref(false)

// Chat overlay state
const showChatOverlay = ref(false)
const prescanDismissed = ref(false)

const prescanUrl = computed(() => {
  if (!prescanToken.value) return ''
  return `${window.location.origin}/interview/${prescanToken.value}`
})

const chatUrl = computed(() => {
  if (!prescanToken.value) return ''
  return `/interview/${prescanToken.value}/chat`
})

onMounted(async () => {
  vacancyLoading.value = true
  try {
    vacancy.value = await vacancyService.getPublicDetail(vacancyId)
  } catch {
    vacancy.value = null
  } finally {
    vacancyLoading.value = false
  }
})

function onFileSelect(event: FileUploadSelectEvent): void {
  cvFile.value = event.files[0] as File
}

function validate(): boolean {
  errors.value = {}
  if (!name.value.trim()) errors.value.name = 'Name is required'
  if (!email.value.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.value.email = 'Invalid email format'
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
  if (!prescanToken.value) return
  // Prescanning is always chat-based
  showChatOverlay.value = true
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
    // fallback
  }
}
</script>

<template>
  <div class="relative">
    <!-- Main content -->
    <div class="mx-auto max-w-2xl px-4 py-8">
      <div v-if="vacancyLoading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
      </div>

      <!-- Step 2: Interview Ready -->
      <template v-else-if="step === 'ready'">
        <div class="space-y-6">
          <div class="rounded-lg border border-green-200 bg-green-50 p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-check-circle text-green-600"></i>
              <p class="font-medium text-green-800">{{ t('candidates.application.success') }}</p>
            </div>
          </div>

          <div class="rounded-lg border border-gray-200 bg-white p-8 text-center">
            <div
              class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100"
            >
              <i class="pi pi-comments text-3xl text-blue-600"></i>
            </div>
            <h2 class="mb-2 text-xl font-bold text-gray-900">Your Prescanning is Ready</h2>
            <p class="mb-6 text-sm text-gray-500">
              You can start your AI prescanning chat now, or do it later using the link below.
            </p>

            <Button
              :label="t('candidates.application.startPrescanning')"
              icon="pi pi-play"
              class="mb-4 w-full"
              size="large"
              @click="startPrescanning"
            />

            <div class="mb-6 rounded-lg border border-gray-200 bg-gray-50 p-3">
              <label class="mb-1 block text-xs font-medium text-gray-500">Prescanning Link</label>
              <div class="flex items-center gap-2">
                <input
                  type="text"
                  readonly
                  :value="prescanUrl"
                  class="flex-1 rounded border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700"
                  @focus="($event.target as HTMLInputElement).select()"
                />
                <Button
                  :label="linkCopied ? t('common.copied') : t('common.copyLink')"
                  :icon="linkCopied ? 'pi pi-check' : 'pi pi-copy'"
                  :severity="linkCopied ? 'success' : 'secondary'"
                  size="small"
                  @click="copyLink"
                />
              </div>
            </div>

            <p class="mb-4 text-sm text-gray-500">
              <i class="pi pi-envelope mr-1"></i>
              We've also sent the prescanning link to your email.
            </p>

            <div class="rounded-lg border border-blue-100 bg-blue-50 p-4">
              <p class="text-sm text-blue-800">
                <i class="pi pi-user-plus mr-1"></i>
                <strong>Tip:</strong> Create an account to track your application status and access
                your interview results.
              </p>
              <RouterLink
                to="/register"
                class="mt-2 inline-block text-sm font-medium text-blue-600 hover:underline"
              >
                Create an account
              </RouterLink>
            </div>
          </div>

          <div class="text-center">
            <RouterLink to="/jobs" class="text-sm text-gray-500 hover:text-gray-700">
              Browse more jobs
            </RouterLink>
          </div>
        </div>
      </template>

      <!-- Step 1: Application form -->
      <template v-else>
        <RouterLink
          :to="`/jobs/${vacancyId}`"
          class="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <i class="pi pi-arrow-left mr-1"></i> Back to job details
        </RouterLink>

        <h1 class="mb-1 text-2xl font-bold">{{ t('candidates.application.title') }}</h1>
        <p v-if="vacancy" class="mb-1 text-gray-600">{{ vacancy.title }}</p>
        <p
          v-if="vacancy && ((vacancy as any).employer?.name || (vacancy as any).companyName)"
          class="mb-6 text-sm text-gray-500"
        >
          <i class="pi pi-building mr-1"></i
          >{{ (vacancy as any).employer?.name || (vacancy as any).companyName }}
        </p>
        <div v-else class="mb-6"></div>

        <p v-if="candidateStore.error" class="mb-4 text-sm text-red-600">
          {{ candidateStore.error }}
        </p>

        <form class="space-y-5" @submit.prevent="handleSubmit">
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

          <div>
            <label class="mb-1 block text-sm font-medium">{{
              t('candidates.application.phone')
            }}</label>
            <InputText v-model="phone" class="w-full" placeholder="+1 234 567 890" />
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium">
              {{ t('candidates.application.uploadCv') }}
              <span v-if="vacancy?.cvRequired" class="text-red-500">*</span>
            </label>
            <FileUpload
              mode="basic"
              accept=".pdf,.docx"
              :max-file-size="10000000"
              choose-label="Choose CV"
              :auto="false"
              @select="onFileSelect"
            />
            <small class="text-gray-400">Accepted formats: PDF, DOCX (max 10MB)</small>
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

    <!-- Chat overlay -->
    <div
      v-if="showChatOverlay && prescanToken"
      class="fixed inset-0 z-50 flex flex-col items-center justify-end sm:justify-center bg-black/30 backdrop-blur-sm"
    >
      <div
        class="flex w-full max-w-3xl flex-1 sm:flex-initial sm:h-[85vh] flex-col overflow-hidden rounded-t-3xl sm:rounded-2xl bg-white shadow-2xl"
      >
        <!-- Overlay header -->
        <div
          class="flex items-center justify-between bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3"
        >
          <div class="flex items-center gap-3">
            <div
              class="flex h-10 w-10 items-center justify-center rounded-full bg-white/20 ring-2 ring-white/30"
            >
              <i class="pi pi-comments text-sm text-white"></i>
            </div>
            <div>
              <p class="text-sm font-semibold text-white">
                {{ t('interviews.chat.aiPrescanning') }}
              </p>
              <p class="text-xs text-blue-100">Answer a few questions to get started</p>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <Button
              icon="pi pi-external-link"
              severity="secondary"
              text
              rounded
              size="small"
              class="!text-white/70 hover:!text-white hover:!bg-white/10"
              title="Open full screen"
              @click="openInFullScreen"
            />
            <Button
              icon="pi pi-minus"
              severity="secondary"
              text
              rounded
              size="small"
              class="!text-white/70 hover:!text-white hover:!bg-white/10"
              title="Minimize"
              @click="showChatOverlay = false"
            />
          </div>
        </div>
        <!-- Embedded chat iframe -->
        <iframe :src="chatUrl" class="flex-1 border-0" allow="microphone; camera"></iframe>
      </div>
    </div>

    <!-- Minimized chat bar (shown when overlay is closed but interview started) -->
    <div
      v-if="!showChatOverlay && step === 'ready' && prescanToken && !prescanDismissed"
      class="fixed bottom-0 left-0 right-0 z-40 cursor-pointer border-t border-gray-200 bg-white px-4 py-3 shadow-lg transition-all hover:bg-gray-50"
      @click="showChatOverlay = true"
    >
      <div class="mx-auto flex max-w-3xl items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600">
            <i class="pi pi-comments text-white"></i>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-900">
              {{ t('interviews.chat.aiPrescanning') }}
            </p>
            <p class="text-xs text-gray-500">Click to open prescanning chat</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <i class="pi pi-chevron-up text-gray-400"></i>
          <Button
            icon="pi pi-times"
            severity="secondary"
            text
            rounded
            size="small"
            title="Dismiss"
            @click.stop="prescanDismissed = true"
          />
        </div>
      </div>
    </div>
  </div>
</template>
