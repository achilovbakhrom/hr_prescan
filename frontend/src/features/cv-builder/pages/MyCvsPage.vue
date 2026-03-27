<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import Message from 'primevue/message'
import ProgressBar from 'primevue/progressbar'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { cvBuilderService } from '../services/cv-builder.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CvFile, CandidateProfile, ProfileUpdatePayload } from '../types/cv-builder.types'

const { t } = useI18n()
const router = useRouter()
const confirm = useConfirm()

const profile = ref<CandidateProfile | null>(null)
const cvs = ref<CvFile[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const actionLoading = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const hasProfileData = computed(() => {
  if (!profile.value) return false
  return profile.value.completeness.score > 0
})

const activeCv = computed(() => cvs.value.find((c) => c.isActive) ?? null)

async function fetchData(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const [p, c] = await Promise.all([
      cvBuilderService.getProfile(),
      cvBuilderService.listCvs(),
    ])
    profile.value = p
    cvs.value = c
  } catch {
    error.value = t('myCvs.loadError')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function templateLabel(template: string): string {
  const map: Record<string, string> = {
    classic: t('myCvs.templates.classic'),
    modern: t('myCvs.templates.modern'),
    minimal: t('myCvs.templates.minimal'),
  }
  return map[template] || template
}

function progressColor(score: number): string {
  if (score >= 80) return '!bg-green-500'
  if (score >= 50) return '!bg-yellow-500'
  return '!bg-red-500'
}

function viewCv(cv: CvFile): void {
  if (cv.downloadUrl) {
    window.open(cv.downloadUrl, '_blank')
  }
}

function viewPublicCv(): void {
  if (profile.value?.shareToken) {
    const url = `${window.location.origin}/cv/${profile.value.shareToken}`
    window.open(url, '_blank')
  }
}

async function toggleVisibility(): Promise<void> {
  if (!profile.value) return
  successMessage.value = null
  error.value = null
  try {
    const newValue = !profile.value.isOpenToWork
    await cvBuilderService.updateProfile({ isOpenToWork: newValue } as ProfileUpdatePayload)
    profile.value.isOpenToWork = newValue
    successMessage.value = newValue ? t('myCvs.cvVisible') : t('myCvs.cvHidden')
  } catch {
    error.value = t('common.error')
  }
}

async function handleToggleActive(cv: CvFile): Promise<void> {
  actionLoading.value = cv.id
  successMessage.value = null
  error.value = null
  try {
    const result = await cvBuilderService.toggleCvActive(cv.id)
    if (result.isActive) {
      // Activated this one — deactivate all others locally
      cvs.value.forEach((c) => { c.isActive = c.id === cv.id })
    } else {
      // Deactivated
      cv.isActive = false
    }
    successMessage.value = result.isActive ? t('myCvs.activated') : t('myCvs.deactivated')
  } catch {
    error.value = t('common.error')
  } finally {
    actionLoading.value = null
  }
}

function handleDelete(cv: CvFile): void {
  confirm.require({
    message: t('myCvs.deleteConfirm', { name: cv.name }),
    header: t('common.confirm'),
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      actionLoading.value = cv.id
      successMessage.value = null
      try {
        await cvBuilderService.deleteCv(cv.id)
        cvs.value = cvs.value.filter((c) => c.id !== cv.id)
        successMessage.value = t('myCvs.deleted')
      } catch {
        error.value = t('common.error')
      } finally {
        actionLoading.value = null
      }
    },
  })
}
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-2xl font-bold text-gray-900">{{ t('myCvs.title') }}</h1>
      <Button
        :label="t('myCvs.goToBuilder')"
        icon="pi pi-pencil"
        size="small"
        @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
      />
    </div>

    <Message v-if="successMessage" severity="success" class="mb-4">{{ successMessage }}</Message>
    <Message v-if="error" severity="error" class="mb-4">{{ error }}</Message>

    <div v-if="loading" class="py-12 text-center text-gray-400">
      <i class="pi pi-spinner pi-spin text-3xl"></i>
    </div>

    <template v-else>
      <!-- Current CV Profile Card -->
      <div
        v-if="profile"
        class="mb-6 rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50/50 to-white p-5"
      >
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
              <i class="pi pi-user text-xl"></i>
            </div>
            <div class="min-w-0">
              <p class="font-semibold text-gray-900">
                {{ profile.headline || t('myCvs.profileCard.noHeadline') }}
              </p>
              <p v-if="profile.location" class="text-sm text-gray-500">
                <i class="pi pi-map-marker mr-1 text-xs"></i>{{ profile.location }}
              </p>
              <div class="mt-1.5 flex items-center gap-2">
                <ProgressBar
                  :value="profile.completeness.score"
                  :showValue="false"
                  class="!h-1.5 w-24"
                  :pt="{ value: { class: progressColor(profile.completeness.score) } }"
                />
                <span class="text-xs font-medium text-gray-500">{{ profile.completeness.score }}%</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button
              icon="pi pi-eye"
              severity="secondary"
              text
              rounded
              size="small"
              v-tooltip.top="t('myCvs.view')"
              :disabled="!profile.isOpenToWork"
              @click="viewPublicCv"
            />
            <Button
              :label="t('common.edit')"
              icon="pi pi-pencil"
              size="small"
              outlined
              @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
            />
          </div>
        </div>

        <!-- Visibility toggle -->
        <div class="mt-4 flex items-center justify-between rounded-lg px-3 py-2" :class="profile.isOpenToWork ? 'bg-green-50' : 'bg-gray-100'">
          <div class="flex items-center gap-2">
            <i class="pi text-sm" :class="profile.isOpenToWork ? 'pi-eye text-green-600' : 'pi-eye-slash text-gray-400'"></i>
            <span class="text-sm" :class="profile.isOpenToWork ? 'text-green-700' : 'text-gray-500'">
              {{ profile.isOpenToWork ? t('myCvs.cvIsVisible') : t('myCvs.cvIsHidden') }}
            </span>
          </div>
          <ToggleSwitch :modelValue="profile.isOpenToWork" @update:modelValue="toggleVisibility" />
        </div>
      </div>

      <!-- No profile data at all -->
      <div
        v-if="!hasProfileData && cvs.length === 0"
        class="rounded-xl border border-dashed border-gray-200 py-16 text-center"
      >
        <i class="pi pi-file-pdf mb-3 text-4xl text-gray-300"></i>
        <p class="font-medium text-gray-600">{{ t('myCvs.empty') }}</p>
        <p class="mt-1 text-sm text-gray-400">{{ t('myCvs.emptyHint') }}</p>
        <Button
          :label="t('myCvs.goToBuilder')"
          icon="pi pi-pencil"
          size="small"
          class="mt-4"
          @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
        />
      </div>

      <!-- Generated PDFs -->
      <div v-if="cvs.length > 0">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('myCvs.generatedPdfs') }}
        </h2>
        <div class="space-y-3">
          <div
            v-for="cv in cvs"
            :key="cv.id"
            class="rounded-xl border bg-white p-4 transition-all"
            :class="cv.isActive ? 'border-green-200 bg-green-50/20' : 'border-gray-200'"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <!-- Left: icon + info -->
              <div class="flex items-center gap-3">
                <div
                  class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                  :class="cv.isActive ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'"
                >
                  <i class="pi pi-file-pdf text-lg"></i>
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <p class="truncate font-medium text-gray-900">{{ cv.name }}</p>
                    <Tag v-if="cv.isActive" :value="t('myCvs.active')" severity="success" class="!text-[10px]" />
                  </div>
                  <div class="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                    <span>{{ templateLabel(cv.template) }}</span>
                    <span>&middot;</span>
                    <span>{{ formatDate(cv.createdAt) }}</span>
                  </div>
                </div>
              </div>

              <!-- Right: actions -->
              <div class="flex items-center gap-3">
                <!-- Toggle active -->
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-500">{{ cv.isActive ? t('myCvs.active') : t('myCvs.inactive') }}</span>
                  <ToggleSwitch
                    :modelValue="cv.isActive"
                    :disabled="actionLoading === cv.id"
                    @update:modelValue="handleToggleActive(cv)"
                  />
                </div>

                <span class="h-5 w-px bg-gray-200"></span>

                <!-- View -->
                <Button
                  v-if="cv.downloadUrl"
                  icon="pi pi-eye"
                  severity="secondary"
                  text
                  rounded
                  size="small"
                  v-tooltip.top="t('myCvs.view')"
                  @click="viewCv(cv)"
                />

                <!-- Delete -->
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  text
                  rounded
                  size="small"
                  v-tooltip.top="t('common.delete')"
                  :loading="actionLoading === cv.id"
                  @click="handleDelete(cv)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <ConfirmDialog />
  </div>
</template>
