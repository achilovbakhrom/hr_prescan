import { ref } from 'vue'
import { defineStore } from 'pinia'
import { extractErrorMessage } from '@/shared/api/errors'
import { settingsService } from '../services/settings.service'
import type { Company } from '@/shared/types/auth.types'
import type {
  CompanyProfileUpdate,
  Invitation,
  TeamMember,
  InviteHRRequest,
} from '../types/settings.types'

export const useSettingsStore = defineStore('settings', () => {
  const companyProfile = ref<Company | null>(null)
  const team = ref<TeamMember[]>([])
  const invitations = ref<Invitation[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProfile(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      companyProfile.value = await settingsService.getCompanyProfile()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data: CompanyProfileUpdate): Promise<void> {
    loading.value = true
    error.value = null
    try {
      companyProfile.value = await settingsService.updateCompanyProfile(data)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function inviteHR(data: InviteHRRequest): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const invitation = await settingsService.inviteHR(data)
      invitations.value.push(invitation)
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  async function fetchTeam(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      team.value = await settingsService.getTeam()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchInvitations(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      invitations.value = await settingsService.getInvitations()
    } catch (err: unknown) {
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function toggleMemberActive(userId: string): Promise<void> {
    const member = team.value.find((m) => m.id === userId)
    if (!member) return

    try {
      const updated = await settingsService.updateTeamMember(userId, {
        isActive: !member.isActive,
      })
      const index = team.value.findIndex((m) => m.id === userId)
      if (index !== -1) {
        team.value[index] = updated
      }
    } catch (err: unknown) {
      const message = extractErrorMessage(err)
      error.value = message
      throw new Error(message)
    }
  }

  return {
    companyProfile,
    team,
    invitations,
    loading,
    error,
    fetchProfile,
    updateProfile,
    inviteHR,
    fetchTeam,
    fetchInvitations,
    toggleMemberActive,
  }
})
