<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import { settingsService } from '../services/settings.service'
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

const telegramLinked = ref(false)
const telegramUsername = ref('')
const linkCode = ref('')
const generatingCode = ref(false)

onMounted(() => {
  if (authStore.user) {
    firstName.value = authStore.user.firstName ?? ''
    lastName.value = authStore.user.lastName ?? ''
    phone.value = authStore.user.phone ?? ''
    email.value = authStore.user.email ?? ''
  }
  fetchInvitations()
  fetchTelegramStatus()
})

async function fetchInvitations(): Promise<void> {
  invitationsLoading.value = true
  try {
    invitations.value = await authService.getMyInvitations()
  } catch {
    // silent
  } finally {
    invitationsLoading.value = false
  }
}

async function acceptInvitation(invitation: PendingInvitation): Promise<void> {
  acceptingToken.value = invitation.token
  errorMessage.value = null
  try {
    const result = await authService.acceptCompanyInvitation(invitation.token)
    authStore.user = result.user
    successMessage.value = `You are now part of ${invitation.company.name}`
    invitations.value = invitations.value.filter((i) => i.id !== invitation.id)
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { detail?: string } } }
    errorMessage.value = axiosErr.response?.data?.detail ?? 'Failed to accept invitation'
  } finally {
    acceptingToken.value = null
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

async function fetchTelegramStatus(): Promise<void> {
  try {
    const status = await settingsService.getTelegramStatus()
    telegramLinked.value = status.linked
    telegramUsername.value = status.telegramUsername ?? ''
  } catch {
    // silent
  }
}

async function handleGenerateCode(): Promise<void> {
  generatingCode.value = true
  try {
    const result = await settingsService.generateTelegramLinkCode()
    linkCode.value = result.code
  } catch {
    errorMessage.value = 'Failed to generate Telegram link code'
  } finally {
    generatingCode.value = false
  }
}

async function handleUnlink(): Promise<void> {
  try {
    await settingsService.unlinkTelegram()
    telegramLinked.value = false
    telegramUsername.value = ''
    linkCode.value = ''
    successMessage.value = t('telegram.disconnected')
  } catch {
    errorMessage.value = 'Failed to disconnect Telegram'
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">{{ t('settings.profile.title') }}</h1>

    <Message v-if="successMessage" severity="success" class="mb-4" :closable="true" @close="successMessage = null">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error" class="mb-4" :closable="true" @close="errorMessage = null">
      {{ errorMessage }}
    </Message>

    <!-- Pending Invitations -->
    <div
      v-if="invitations.length > 0"
      class="rounded-lg border-2 border-blue-200 bg-blue-50 p-5"
    >
      <div class="mb-3 flex items-center gap-2">
        <i class="pi pi-envelope text-blue-600"></i>
        <h2 class="text-base font-semibold text-blue-900">
          {{ t('settings.profile.pendingInvitations', { count: invitations.length }) }}
        </h2>
      </div>
      <div class="space-y-3">
        <div
          v-for="inv in invitations"
          :key="inv.id"
          class="flex items-center justify-between rounded-lg bg-white p-4 shadow-sm"
        >
          <div>
            <p class="font-medium text-gray-900">{{ inv.company.name }}</p>
            <p class="text-sm text-gray-500">
              {{ inv.company.industry }} &middot; {{ inv.company.country }}
            </p>
            <p class="mt-1 text-xs text-gray-400">
              {{ t('settings.profile.invitedBy', { name: inv.invitedByName }) }} &middot; {{ formatDate(inv.createdAt) }}
              &middot; {{ t('settings.profile.expires', { date: formatDate(inv.expiresAt) }) }}
            </p>
          </div>
          <Button
            :label="t('settings.profile.accept')"
            icon="pi pi-check"
            size="small"
            :loading="acceptingToken === inv.token"
            @click="acceptInvitation(inv)"
          />
        </div>
      </div>
      <p class="mt-3 text-xs text-blue-700">
        {{ t('settings.profile.acceptInvitationHint') }}
      </p>
    </div>

    <!-- Profile Info -->
    <div class="rounded-lg border border-gray-200 bg-white p-6">
      <!-- Avatar -->
      <div class="mb-6 flex items-center gap-4">
        <div
          class="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 text-2xl font-bold text-blue-700"
        >
          {{ authStore.user?.firstName?.charAt(0) ?? '' }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
        </div>
        <div>
          <p class="text-lg font-semibold text-gray-900">
            {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
          </p>
          <p class="text-sm text-gray-500">{{ authStore.user?.role }}</p>
        </div>
      </div>

      <form class="flex flex-col gap-4" @submit.prevent>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="flex flex-col gap-1">
            <label for="firstName" class="text-sm font-medium text-gray-700">{{ t('settings.profile.firstName') }}</label>
            <InputText id="firstName" v-model="firstName" class="w-full" disabled />
          </div>
          <div class="flex flex-col gap-1">
            <label for="lastName" class="text-sm font-medium text-gray-700">{{ t('settings.profile.lastName') }}</label>
            <InputText id="lastName" v-model="lastName" class="w-full" disabled />
          </div>
        </div>

        <div class="flex flex-col gap-1">
          <label for="email" class="text-sm font-medium text-gray-700">{{ t('settings.profile.email') }}</label>
          <InputText id="email" v-model="email" class="w-full" disabled />
          <small class="text-gray-400">{{ t('settings.profile.emailCannotChange') }}</small>
        </div>

        <div class="flex flex-col gap-1">
          <label for="phone" class="text-sm font-medium text-gray-700">{{ t('settings.profile.phone') }}</label>
          <InputText id="phone" v-model="phone" class="w-full" disabled />
        </div>
      </form>

      <div class="mt-6 border-t border-gray-200 pt-4">
        <h3 class="mb-2 text-sm font-medium text-gray-700">{{ t('settings.profile.accountInfo') }}</h3>
        <div class="space-y-1 text-sm text-gray-500">
          <p>
            {{ t('settings.profile.emailVerified') }}
            <span :class="authStore.user?.emailVerified ? 'text-green-600' : 'text-red-600'">
              {{ authStore.user?.emailVerified ? t('common.yes') : t('common.no') }}
            </span>
          </p>
          <p v-if="authStore.user?.company">
            {{ t('settings.profile.companyLabel') }} <span class="font-medium text-gray-900">{{ authStore.user.company.name }}</span>
          </p>
          <p v-else class="text-gray-400">
            {{ t('settings.profile.noCompany') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Telegram Connection -->
    <div class="rounded-xl border border-gray-200 bg-white p-5">
      <div class="flex items-center gap-3 mb-4">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50">
          <i class="pi pi-send text-blue-500 text-lg"></i>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-gray-900">{{ t('telegram.title') }}</h3>
          <p class="text-xs text-gray-500">{{ t('telegram.subtitle') }}</p>
        </div>
      </div>

      <!-- Connected state -->
      <div v-if="telegramLinked" class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
          <span class="text-sm text-gray-700">{{ t('telegram.connected') }}: @{{ telegramUsername }}</span>
        </div>
        <Button :label="t('telegram.disconnect')" severity="danger" text size="small" @click="handleUnlink" />
      </div>

      <!-- Not connected state -->
      <div v-else>
        <div v-if="linkCode" class="text-center">
          <p class="text-sm text-gray-600 mb-3">{{ t('telegram.linkCodeHint') }}</p>
          <div class="inline-flex items-center gap-3 rounded-xl bg-gray-50 px-6 py-4 mb-3">
            <span class="text-3xl font-bold tracking-[0.3em] text-gray-900">{{ linkCode }}</span>
          </div>
          <p class="text-xs text-gray-400">{{ t('telegram.linkCodeExpires') }}</p>
        </div>
        <div v-else class="text-center">
          <p class="text-sm text-gray-500 mb-3">{{ t('telegram.notConnected') }}</p>
          <Button :label="t('telegram.connect')" icon="pi pi-link" size="small" :loading="generatingCode" @click="handleGenerateCode" />
        </div>
      </div>
    </div>
  </div>
</template>
