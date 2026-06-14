<script setup lang="ts">
/**
 * ProfilePage — two-column settings layout (desktop).
 * Left rail: SettingsNav, content: personal + invitations + telegram.
 * Spec: docs/design/spec.md §9.
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Message from 'primevue/message'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import TelegramConnection from '../components/TelegramConnection.vue'
import ProfileInvitationsCard from '../components/ProfileInvitationsCard.vue'
import ProfilePersonalCard from '../components/ProfilePersonalCard.vue'
import SettingsAccountCard from '../components/SettingsAccountCard.vue'
import type { PendingInvitation } from '@/shared/types/auth.types'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'admin')

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

const tabs = computed(() => [
  { id: 'profile', label: t('nav.profile'), active: true },
  ...(isAdmin.value
    ? [{ id: 'team', label: t('nav.team'), route: ROUTE_NAMES.TEAM_MANAGEMENT }]
    : []),
  { id: 'notifications', label: t('settings.profile.notifications'), scroll: 'notifications' },
  ...(isAdmin.value
    ? [{ id: 'billing', label: t('nav.subscription'), route: ROUTE_NAMES.SUBSCRIPTION }]
    : []),
])

function onTab(tab: { route?: string; scroll?: string }): void {
  if (tab.route) router.push({ name: tab.route })
  else if (tab.scroll) scrollToSection(tab.scroll)
}

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
  <div class="w-full">
    <header class="mb-6 flex flex-col gap-1">
      <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
        {{ t('settings.profile.title') }}
      </h1>
      <p class="text-sm text-[color:var(--color-text-muted)]">
        {{ t('settings.profile.subtitle') }}
      </p>
    </header>

    <div
      class="mb-6 -mx-1 flex gap-1 overflow-x-auto border-b border-[color:var(--color-border-soft)] px-1"
    >
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="shrink-0 border-b-2 px-3 pb-3 text-sm font-medium transition-colors"
        :class="
          tab.active
            ? 'border-[color:var(--color-accent)] text-[color:var(--color-accent)]'
            : 'border-transparent text-[color:var(--color-text-secondary)] hover:text-[color:var(--color-text-primary)]'
        "
        @click="onTab(tab)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_340px]">
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

      <aside>
        <SettingsAccountCard />
      </aside>
    </div>
  </div>
</template>
