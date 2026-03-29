<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Message from 'primevue/message'
import CompanySetupForm from '../components/CompanySetupForm.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { CompanySize } from '../types/auth.types'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

type Step = 'role' | 'company-form'
const step = ref<Step>('role')
const loading = ref(false)
const errorMessage = ref<string | null>(null)

const isTelegramUser = computed(() => authStore.user?.email?.endsWith('@telegram.local') ?? false)

async function handleCandidateClick(): Promise<void> {
  loading.value = true; errorMessage.value = null
  try { await authStore.completeOnboarding(); await router.push({ name: ROUTE_NAMES.DASHBOARD }) }
  catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : 'Something went wrong. Please try again.' }
  finally { loading.value = false }
}

async function handleCompanySubmit(data: { companyName: string; industries: string[]; size: CompanySize; country: string; email?: string }): Promise<void> {
  loading.value = true; errorMessage.value = null
  try {
    await authStore.completeCompanySetup({
      companyName: data.companyName, industries: data.industries, size: data.size, country: data.country,
      ...(data.email ? { email: data.email } : {}),
    })
    await router.push({ name: ROUTE_NAMES.DASHBOARD })
  } catch (err: unknown) { errorMessage.value = err instanceof Error ? err.message : 'Something went wrong. Please try again.' }
  finally { loading.value = false }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center py-12">
    <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-md sm:p-8">
      <template v-if="step === 'role'">
        <h1 class="mb-8 text-center text-xl font-bold text-gray-900 sm:text-2xl">{{ t('auth.chooseRole.title') }}</h1>
        <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

        <div class="flex flex-col gap-4">
          <button class="flex w-full cursor-pointer items-center gap-4 rounded-lg border-2 border-gray-200 p-4 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 sm:p-6" :disabled="loading" @click="handleCandidateClick">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-green-100 sm:h-14 sm:w-14"><i class="pi pi-user text-xl text-green-600 sm:text-2xl" /></div>
            <div><p class="text-base font-semibold text-gray-900 sm:text-lg">{{ t('auth.chooseRole.candidate') }}</p><p class="mt-1 text-sm text-gray-500">{{ t('auth.chooseRole.candidateDescription') }}</p></div>
          </button>

          <button class="flex w-full cursor-pointer items-center gap-4 rounded-lg border-2 border-gray-200 p-4 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 sm:p-6" :disabled="loading" @click="step = 'company-form'">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 sm:h-14 sm:w-14"><i class="pi pi-building text-xl text-blue-600 sm:text-2xl" /></div>
            <div><p class="text-base font-semibold text-gray-900 sm:text-lg">{{ t('auth.chooseRole.company') }}</p><p class="mt-1 text-sm text-gray-500">{{ t('auth.chooseRole.companyDescription') }}</p></div>
          </button>
        </div>
      </template>

      <CompanySetupForm v-else :error-message="errorMessage" :loading="loading" :show-email-field="isTelegramUser" @submit="handleCompanySubmit" @back="step = 'role'; errorMessage = null" />
    </div>
  </div>
</template>
