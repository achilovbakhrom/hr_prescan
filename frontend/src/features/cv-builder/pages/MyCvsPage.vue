<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import CvProfileCard from '../components/CvProfileCard.vue'
import CvFileCard from '../components/CvFileCard.vue'
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

const hasProfileData = computed(() =>
  profile.value ? profile.value.completeness.score > 0 : false,
)

async function fetchData(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const [p, c] = await Promise.all([cvBuilderService.getProfile(), cvBuilderService.listCvs()])
    profile.value = p ?? null
    cvs.value = c
  } catch {
    error.value = t('myCvs.loadError')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function viewCv(cv: CvFile): void {
  if (cv.downloadUrl) window.open(cv.downloadUrl, '_blank')
}

function viewPublicCv(): void {
  if (profile.value?.shareToken)
    window.open(`${window.location.origin}/cv/${profile.value.shareToken}`, '_blank')
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
      cvs.value.forEach((c) => {
        c.isActive = c.id === cv.id
      })
    } else {
      cv.isActive = false
    }
    successMessage.value = result.isActive ? t('myCvs.activated') : t('myCvs.deactivated')
  } catch {
    error.value = t('common.error')
  } finally {
    actionLoading.value = null
  }
}

function handleDeleteProfile(): void {
  confirm.require({
    message: t('myCvs.deleteProfileConfirm'),
    header: t('common.confirm'),
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      successMessage.value = null
      error.value = null
      try {
        await cvBuilderService.deleteProfile()
        profile.value = null
        cvs.value = []
        successMessage.value = t('myCvs.profileDeleted')
      } catch {
        error.value = t('common.error')
      }
    },
  })
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
      <CvProfileCard
        v-if="profile"
        :profile="profile"
        @toggle-visibility="toggleVisibility"
        @view-public="viewPublicCv"
        @delete="handleDeleteProfile"
      />

      <div
        v-if="!hasProfileData && cvs.length === 0"
        class="rounded-xl border border-dashed border-gray-200 dark:border-gray-700 py-16 text-center"
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

      <div v-if="cvs.length > 0">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          {{ t('myCvs.generatedPdfs') }}
        </h2>
        <div class="space-y-3">
          <CvFileCard
            v-for="cv in cvs"
            :key="cv.id"
            :cv="cv"
            :action-loading="actionLoading"
            @view="viewCv"
            @toggle-active="handleToggleActive"
            @delete="handleDelete"
          />
        </div>
      </div>
    </template>

    <ConfirmDialog />
  </div>
</template>
