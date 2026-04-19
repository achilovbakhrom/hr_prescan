/**
 * useMyCvs — state + actions for MyCvsPage.
 * Keeps the page component thin; same behavior as before.
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirm } from 'primevue/useconfirm'
import { cvBuilderService } from '../services/cv-builder.service'
import type { CvFile, CandidateProfile, ProfileUpdatePayload } from '../types/cv-builder.types'

export function useMyCvs() {
  const { t } = useI18n()
  const confirm = useConfirm()

  const profile = ref<CandidateProfile | null>(null)
  const cvs = ref<CvFile[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const actionLoading = ref<string | null>(null)
  const successMessage = ref<string | null>(null)

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

  return {
    profile,
    cvs,
    loading,
    error,
    actionLoading,
    successMessage,
    fetchData,
    viewCv,
    viewPublicCv,
    toggleVisibility,
    handleToggleActive,
    handleDeleteProfile,
    handleDelete,
  }
}
