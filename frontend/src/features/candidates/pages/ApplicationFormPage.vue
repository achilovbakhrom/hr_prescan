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
    })
    const resp = application as unknown as Record<string, unknown>
    prescanToken.value = (resp.prescanToken ?? resp.prescan_token ?? resp.interviewToken ?? resp.interview_token ?? null) as string | null
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
    setTimeout(() => { linkCopied.value = false }, 2000)
  } catch {
    // fallback
  }
}
</script>

<template>
  <div class="relative">
    <!-- Main content -->
    <div class="mx-auto max-w-2xl px-4 py-6 sm:py-8">
      <div v-if="vacancyLoading" class="py-12 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
      </div>

      <!-- Step 2: Interview Ready -->
      <template v-else-if="step === 'ready'">
        <div class="space-y-4 sm:space-y-6">
          <div class="rounded-lg border border-green-200 bg-green-50 p-3 sm:p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-check-circle text-green-600"></i>
              <p class="text-sm font-medium text-green-800 sm:text-base">{{ t('candidates.application.success') }}</p>
            </div>
          </div>

          <div class="rounded-lg border border-gray-200 bg-white p-5 text-center sm:p-8">
            <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 sm:mb-4 sm:h-16 sm:w-16">
              <i class="pi pi-comments text-2xl text-blue-600 sm:text-3xl"></i>
            </div>
            <h2 class="mb-2 text-lg font-bold text-gray-900 sm:text-xl">{{ t('candidates.application.prescanReady') }}</h2>
            <p class="mb-4 text-xs text-gray-500 sm:mb-6 sm:text-sm">
              {{ t('candidates.application.prescanReadyHint') }}
            </p>

            <Button
              :label="t('candidates.application.startPrescanning')"
              icon="pi pi-play"
              class="mb-4 w-full"
              size="large"
              @click="startPrescanning"
            />

            <div class="mb-4 rounded-lg border border-gray-200 bg-gray-50 p-3 sm:mb-6">
              <label class="mb-1 block text-xs font-medium text-gray-500">{{ t('candidates.application.prescanLink') }}</label>
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                <input
                  type="text"
                  readonly
                  :value="prescanUrl"
                  class="w-full rounded border border-gray-200 bg-white px-3 py-2 text-xs text-gray-700 sm:flex-1 sm:text-sm"
                  @focus="($event.target as HTMLInputElement).select()"
                />
                <Button
                  :label="linkCopied ? t('common.copied') : t('common.copyLink')"
                  :icon="linkCopied ? 'pi pi-check' : 'pi pi-copy'"
                  :severity="linkCopied ? 'success' : 'secondary'"
                  size="small"
                  class="w-full sm:w-auto"
                  @click="copyLink"
                />
              </div>
            </div>

            <p class="mb-3 text-xs text-gray-500 sm:mb-4 sm:text-sm">
              <i class="pi pi-envelope mr-1"></i>
              {{ t('candidates.application.linkSentToEmail') }}
            </p>

            <div class="rounded-lg border border-blue-100 bg-blue-50 p-3 text-left sm:p-4">
              <p class="text-xs text-blue-800 sm:text-sm">
                <i class="pi pi-user-plus mr-1"></i>
                <strong>{{ t('candidates.application.tip') }}:</strong> {{ t('candidates.application.tipText') }}
              </p>
              <RouterLink
                to="/register"
                class="mt-2 inline-block text-xs font-medium text-blue-600 hover:underline sm:text-sm"
              >
                {{ t('candidates.application.createAccount') }}
              </RouterLink>
            </div>
          </div>

          <div class="text-center">
            <RouterLink to="/jobs" class="text-xs text-gray-500 hover:text-gray-700 sm:text-sm">
              {{ t('candidates.application.browseMoreJobs') }}
            </RouterLink>
          </div>
        </div>
      </template>

      <!-- Step 1: Application form -->
      <template v-else>
        <RouterLink :to="`/jobs/${vacancyId}`" class="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <i class="pi pi-arrow-left mr-1"></i> {{ t('candidates.application.backToJob') }}
        </RouterLink>

        <h1 class="mb-1 text-xl font-bold sm:text-2xl">{{ t('candidates.application.title') }}</h1>
        <p v-if="vacancy" class="mb-1 text-sm text-gray-600 sm:text-base">{{ vacancy.title }}</p>
        <p v-if="vacancy && ((vacancy as any).employer?.name || (vacancy as any).companyName)" class="mb-4 text-xs text-gray-500 sm:mb-6 sm:text-sm">
          <i class="pi pi-building mr-1"></i>{{ (vacancy as any).employer?.name || (vacancy as any).companyName }}
        </p>
        <div v-else class="mb-4 sm:mb-6"></div>

        <p v-if="candidateStore.error" class="mb-4 text-sm text-red-600">
          {{ candidateStore.error }}
        </p>

        <form class="space-y-4 sm:space-y-5" @submit.prevent="handleSubmit">
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('candidates.application.name') }} *</label>
            <InputText v-model="name" class="w-full" placeholder="John Doe" :invalid="!!errors.name" />
            <small v-if="errors.name" class="text-red-500">{{ errors.name }}</small>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('candidates.application.email') }} *</label>
            <InputText v-model="email" type="email" class="w-full" placeholder="john@example.com" :invalid="!!errors.email" />
            <small v-if="errors.email" class="text-red-500">{{ errors.email }}</small>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('candidates.application.phone') }}</label>
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

    <!-- Chat overlay -->
    <div
      v-if="showChatOverlay && prescanToken"
      class="fixed inset-0 z-50 flex flex-col bg-black/30 backdrop-blur-sm sm:items-center sm:justify-center sm:p-4"
    >
      <div class="flex h-full w-full flex-col overflow-hidden bg-white sm:h-[85vh] sm:max-h-[700px] sm:max-w-3xl sm:rounded-2xl sm:shadow-2xl">
        <!-- Overlay header -->
        <div class="flex items-center justify-between bg-gradient-to-r from-blue-600 to-blue-700 px-3 py-2.5 sm:px-4 sm:py-3">
          <div class="flex items-center gap-2 sm:gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white/20 ring-2 ring-white/30 sm:h-10 sm:w-10">
              <i class="pi pi-comments text-xs text-white sm:text-sm"></i>
            </div>
            <div class="min-w-0">
              <p class="truncate text-xs font-semibold text-white sm:text-sm">{{ t('interviews.chat.aiPrescanning') }}</p>
              <p class="hidden text-xs text-blue-100 sm:block">{{ t('candidates.application.answerQuestions') }}</p>
            </div>
          </div>
          <div class="flex items-center gap-0.5 sm:gap-1">
            <Button
              icon="pi pi-external-link"
              severity="secondary"
              text
              rounded
              size="small"
              class="!h-8 !w-8 !text-white/70 hover:!bg-white/10 hover:!text-white sm:!h-9 sm:!w-9"
              @click="openInFullScreen"
            />
            <Button
              icon="pi pi-minus"
              severity="secondary"
              text
              rounded
              size="small"
              class="!h-8 !w-8 !text-white/70 hover:!bg-white/10 hover:!text-white sm:!h-9 sm:!w-9"
              @click="showChatOverlay = false"
            />
          </div>
        </div>
        <!-- Embedded chat iframe -->
        <iframe
          :src="chatUrl"
          class="min-h-0 flex-1 border-0"
          allow="microphone; camera"
        ></iframe>
      </div>
    </div>

    <!-- Minimized chat bar (shown when overlay is closed but interview started) -->
    <div
      v-if="!showChatOverlay && step === 'ready' && prescanToken && !prescanDismissed"
      class="fixed bottom-0 left-0 right-0 z-40 cursor-pointer border-t border-gray-200 bg-white px-3 py-2.5 shadow-lg transition-all hover:bg-gray-50 sm:px-4 sm:py-3"
      @click="showChatOverlay = true"
    >
      <div class="mx-auto flex max-w-3xl items-center justify-between">
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 sm:h-10 sm:w-10">
            <i class="pi pi-comments text-xs text-white sm:text-sm"></i>
          </div>
          <div class="min-w-0">
            <p class="truncate text-xs font-medium text-gray-900 sm:text-sm">{{ t('interviews.chat.aiPrescanning') }}</p>
            <p class="hidden text-xs text-gray-500 sm:block">{{ t('candidates.application.clickToOpenChat') }}</p>
          </div>
        </div>
        <div class="flex items-center gap-1 sm:gap-2">
          <i class="pi pi-chevron-up text-xs text-gray-400 sm:text-sm"></i>
          <Button
            icon="pi pi-times"
            severity="secondary"
            text
            rounded
            size="small"
            class="!h-8 !w-8 sm:!h-9 sm:!w-9"
            @click.stop="prescanDismissed = true"
          />
        </div>
      </div>
    </div>
  </div>
</template>
