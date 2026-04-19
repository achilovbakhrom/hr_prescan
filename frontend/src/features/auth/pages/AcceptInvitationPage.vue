<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import InvitationNewUserForm from '../components/InvitationNewUserForm.vue'
import { useAuthStore } from '../stores/auth.store'
import { apiClient } from '@/shared/api/client'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const token = ref((route.query.token as string) || '')
const errorMessage = ref<string | null>(null)
const loading = ref(true)
const existingUser = ref(false)
const invitationEmail = ref('')
const accountOwnerName = ref('')
const companyNames = ref<string[]>([])
const invitationError = ref<string | null>(null)

onMounted(async () => {
  if (!token.value) {
    loading.value = false
    return
  }
  try {
    const response = await apiClient.get('/auth/check-invitation', {
      params: { token: token.value },
    })
    existingUser.value = response.data.existingUser
    invitationEmail.value = response.data.email
    accountOwnerName.value = response.data.accountOwnerName || ''
    companyNames.value = response.data.companyNames || []
    if (authStore.isAuthenticated && authStore.user?.email === invitationEmail.value) {
      await handleAcceptAsLoggedIn()
      return
    }
  } catch (err: unknown) {
    const axErr = err as { response?: { data?: { detail?: string } } }
    invitationError.value = axErr.response?.data?.detail || 'Invalid invitation link.'
  } finally {
    loading.value = false
  }
})

async function handleSubmit(data: {
  firstName: string
  lastName: string
  password: string
}): Promise<void> {
  errorMessage.value = null
  try {
    await authStore.acceptInvitation({
      token: token.value,
      password: data.password,
      firstName: data.firstName,
      lastName: data.lastName,
    })
    await router.push({ name: ROUTE_NAMES.LOGIN, query: { message: 'invitation-accepted' } })
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Failed to accept invitation. Please try again.'
  }
}

async function handleAcceptAsLoggedIn(): Promise<void> {
  try {
    await authStore.acceptCompanyInvitation(token.value)
    await authStore.fetchCompanies()
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to accept invitation.'
    loading.value = false
  }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-800 p-8 shadow-md">
      <div v-if="loading" class="py-8 text-center">
        <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
      </div>

      <template v-else-if="invitationError || !token">
        <h1 class="mb-4 text-center text-2xl font-bold text-gray-900">
          {{ t('auth.acceptInvitation.title') }}
        </h1>
        <Message severity="error">{{
          invitationError || 'Invalid invitation link. Please check the link in your email.'
        }}</Message>
      </template>

      <template v-else-if="existingUser && !authStore.isAuthenticated">
        <div class="text-center">
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100"
          >
            <i class="pi pi-building text-2xl text-blue-600"></i>
          </div>
          <h1 class="mb-2 text-2xl font-bold text-gray-900">
            {{ t('auth.acceptInvitation.title') }}
          </h1>
          <p class="mb-6 text-sm text-gray-600">
            You've been invited to join <strong>{{ accountOwnerName }}</strong> as an HR team member
            <template v-if="companyNames.length">
              with access to <strong>{{ companyNames.join(', ') }}</strong></template>.
            Please sign in to your existing account to accept.
          </p>
          <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>
          <Button
            :label="t('nav.signIn')"
            icon="pi pi-sign-in"
            class="w-full"
            @click="router.push({ name: ROUTE_NAMES.LOGIN, query: { redirect: route.fullPath } })"
          />
          <p class="mt-3 text-xs text-gray-500">
            Account: <strong>{{ invitationEmail }}</strong>
          </p>
        </div>
      </template>

      <InvitationNewUserForm
        v-else-if="!existingUser"
        :invitation-email="invitationEmail"
        :account-owner-name="accountOwnerName"
        :company-names="companyNames"
        :error-message="errorMessage"
        :loading="authStore.loading"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>
