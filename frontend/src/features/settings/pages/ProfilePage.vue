<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { authService } from '@/features/auth/services/auth.service'
import TelegramConnection from '../components/TelegramConnection.vue'
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
    successMessage.value = `You are now part of ${inv.accountOwnerName}`
    invitations.value = invitations.value.filter((i) => i.id !== inv.id)
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
</script>

<template>
  <div class="mx-auto max-w-2xl space-y-6">
    <h1 class="text-2xl font-bold text-gray-900">{{ t('settings.profile.title') }}</h1>

    <Message
      v-if="successMessage"
      severity="success"
      class="mb-4"
      :closable="true"
      @close="successMessage = null"
      >{{ successMessage }}</Message
    >
    <Message
      v-if="errorMessage"
      severity="error"
      class="mb-4"
      :closable="true"
      @close="errorMessage = null"
      >{{ errorMessage }}</Message
    >

    <div v-if="invitations.length > 0" class="rounded-lg border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 p-5">
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
          class="flex items-center justify-between rounded-lg bg-white dark:bg-gray-800 p-4 shadow-sm"
        >
          <div>
            <p class="font-medium text-gray-900">{{ inv.accountOwnerName }}</p>
            <p v-if="inv.companies?.length" class="text-sm text-gray-500">
              {{ inv.companies.map((c) => c.name).join(', ') }}
            </p>
            <p class="mt-1 text-xs text-gray-400">
              {{ t('settings.profile.invitedBy', { name: inv.invitedByName }) }} &middot;
              {{ formatDate(inv.createdAt) }} &middot;
              {{ t('settings.profile.expires', { date: formatDate(inv.expiresAt) }) }}
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
      <p class="mt-3 text-xs text-blue-700">{{ t('settings.profile.acceptInvitationHint') }}</p>
    </div>

    <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
      <div class="mb-6 flex items-center gap-4">
        <div
          class="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-950 text-2xl font-bold text-blue-700"
        >
          {{ authStore.user?.firstName?.charAt(0) ?? ''
          }}{{ authStore.user?.lastName?.charAt(0) ?? '' }}
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
            <label for="firstName" class="text-sm font-medium text-gray-700">{{
              t('settings.profile.firstName')
            }}</label
            ><InputText id="firstName" v-model="firstName" class="w-full" disabled />
          </div>
          <div class="flex flex-col gap-1">
            <label for="lastName" class="text-sm font-medium text-gray-700">{{
              t('settings.profile.lastName')
            }}</label
            ><InputText id="lastName" v-model="lastName" class="w-full" disabled />
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <label for="email" class="text-sm font-medium text-gray-700">{{
            t('settings.profile.email')
          }}</label
          ><InputText id="email" v-model="email" class="w-full" disabled /><small
            class="text-gray-400"
            >{{ t('settings.profile.emailCannotChange') }}</small
          >
        </div>
        <div class="flex flex-col gap-1">
          <label for="phone" class="text-sm font-medium text-gray-700">{{
            t('settings.profile.phone')
          }}</label
          ><InputText id="phone" v-model="phone" class="w-full" disabled />
        </div>
      </form>
      <div class="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4">
        <h3 class="mb-2 text-sm font-medium text-gray-700">
          {{ t('settings.profile.accountInfo') }}
        </h3>
        <div class="space-y-1 text-sm text-gray-500">
          <p>
            {{ t('settings.profile.emailVerified') }}
            <span :class="authStore.user?.emailVerified ? 'text-green-600' : 'text-red-600'">{{
              authStore.user?.emailVerified ? t('common.yes') : t('common.no')
            }}</span>
          </p>
          <p v-if="authStore.user?.company">
            {{ t('settings.profile.companyLabel') }}
            <span class="font-medium text-gray-900">{{ authStore.user.company.name }}</span>
          </p>
          <p v-else class="text-gray-400">{{ t('settings.profile.noCompany') }}</p>
        </div>
      </div>
    </div>

    <TelegramConnection
      @success="(msg) => (successMessage = msg)"
      @error="(msg) => (errorMessage = msg)"
    />
  </div>
</template>
