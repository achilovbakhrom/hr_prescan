<script setup lang="ts">
/**
 * ProfilePage — two-column settings layout (desktop).
 * Left rail: SettingsNav, content: personal + invitations + telegram.
 * Spec: docs/design/spec.md §9.
 */
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Message from 'primevue/message'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import SettingsNav from '../components/SettingsNav.vue'
import TelegramConnection from '../components/TelegramConnection.vue'
import ProfileInvitationsCard from '../components/ProfileInvitationsCard.vue'
import ProfilePersonalCard from '../components/ProfilePersonalCard.vue'
import type { PendingInvitation } from '@/shared/types/auth.types'

const { t } = useI18n()
const authStore = useAuthStore()

const firstName = ref('')
const lastName = ref('')
const phone = ref('')
const email = ref('')
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

const invitations = ref<PendingInvitation[]>([])
const invitationsLoading = ref(false)
const acceptingToken = ref<string | null>(null)

const activeSection = ref('personal')

const navItems = [
  { id: 'invitations', labelKey: 'settings.profile.invitations', icon: 'pi pi-envelope' },
  { id: 'personal', labelKey: 'settings.profile.personalInfo', icon: 'pi pi-user' },
  { id: 'notifications', labelKey: 'settings.profile.notifications', icon: 'pi pi-bell' },
]

onMounted(() => {
  if (authStore.user) {
    firstName.value = authStore.user.firstName ?? ''
    lastName.value = authStore.user.lastName ?? ''
    phone.value = authStore.user.phone ?? ''
    email.value = authStore.user.email ?? ''
  }
  fetchInvitations()
})

async function fetchInvitations(): Promise<void> {
  invitationsLoading.value = true
  try {
    invitations.value = await authService.getMyInvitations()
  } catch {
    /* silent */
  } finally {
    invitationsLoading.value = false
  }
}

async function acceptInvitation(inv: PendingInvitation): Promise<void> {
  acceptingToken.value = inv.token
  errorMessage.value = null
  try {
    const result = await authService.acceptCompanyInvitation(inv.token)
    authStore.user = result.user
    successMessage.value = t('settings.profile.invitationAccepted', {
      company: inv.accountOwnerName,
    })
    invitations.value = invitations.value.filter((i) => i.id !== inv.id)
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { detail?: string } } }
    errorMessage.value =
      axiosErr.response?.data?.detail ?? t('settings.profile.acceptInvitationError')
  } finally {
    acceptingToken.value = null
  }
}

function scrollToSection(id: string): void {
  activeSection.value = id
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<template>
  <div class="mx-auto max-w-6xl">
    <header class="mb-6 flex flex-col gap-1">
      <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
        {{ t('settings.profile.title') }}
      </h1>
      <p class="text-sm text-[color:var(--color-text-muted)]">
        {{ t('settings.profile.subtitle') }}
      </p>
    </header>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-[220px_1fr]">
      <SettingsNav :active-id="activeSection" :items="navItems" @select="scrollToSection" />

      <div class="space-y-6">
        <Message
          v-if="successMessage"
          severity="success"
          :closable="true"
          @close="successMessage = null"
        >
          {{ successMessage }}
        </Message>
        <Message v-if="errorMessage" severity="error" :closable="true" @close="errorMessage = null">
          {{ errorMessage }}
        </Message>

        <div v-if="invitations.length > 0" id="invitations">
          <ProfileInvitationsCard
            :invitations="invitations"
            :accepting-token="acceptingToken"
            @accept="acceptInvitation"
          />
        </div>

        <div id="personal">
          <ProfilePersonalCard
            :first-name="firstName"
            :last-name="lastName"
            :email="email"
            :phone="phone"
          />
        </div>

        <div id="notifications">
          <TelegramConnection
            @success="(msg: string) => (successMessage = msg)"
            @error="(msg: string) => (errorMessage = msg)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
