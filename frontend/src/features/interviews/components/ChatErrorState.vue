<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import type { ChatErrorState } from '../composables/useChatInterview'

defineProps<{
  errorState: ChatErrorState
  errorMessage: string
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-1 items-center justify-center px-4">
    <div class="w-full max-w-md text-center">
      <template v-if="errorState === 'completed'">
        <div class="rounded-2xl bg-white p-8 shadow-lg">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <i class="pi pi-check text-3xl text-green-600"></i>
          </div>
          <h1 class="mb-2 text-xl font-bold text-gray-900">{{ t('interviews.chatPage.interviewCompleted') }}</h1>
          <p class="mb-6 text-sm text-gray-500">{{ t('interviews.states.completed') }}</p>
          <RouterLink
            to="/jobs"
            class="inline-block rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            {{ t('interviews.chatPage.browseMoreJobs') }}
          </RouterLink>
        </div>
      </template>

      <template v-else-if="errorState === 'expired'">
        <div class="rounded-2xl bg-white p-8 shadow-lg">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100">
            <i class="pi pi-clock text-3xl text-yellow-600"></i>
          </div>
          <h1 class="mb-2 text-xl font-bold text-gray-900">{{ t('interviews.chatPage.linkExpired') }}</h1>
          <p class="mb-6 text-sm text-gray-500">{{ errorMessage || t('interviews.states.expired') }}</p>
          <RouterLink to="/jobs" class="text-sm font-medium text-blue-600 hover:underline">{{ t('interviews.chatPage.browseMoreJobs') }}</RouterLink>
        </div>
      </template>

      <template v-else-if="errorState === 'closed'">
        <div class="rounded-2xl bg-white p-8 shadow-lg">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
            <i class="pi pi-ban text-3xl text-gray-400"></i>
          </div>
          <h1 class="mb-2 text-xl font-bold text-gray-900">{{ t('interviews.chatPage.vacancyClosed') }}</h1>
          <p class="mb-6 text-sm text-gray-500">{{ errorMessage || t('interviews.states.closed') }}</p>
          <RouterLink to="/jobs" class="text-sm font-medium text-blue-600 hover:underline">{{ t('interviews.chatPage.browseMoreJobs') }}</RouterLink>
        </div>
      </template>

      <template v-else>
        <div class="rounded-2xl bg-white p-8 shadow-lg">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <i class="pi pi-exclamation-triangle text-3xl text-red-400"></i>
          </div>
          <h1 class="mb-2 text-xl font-bold text-gray-900">{{ t('interviews.chatPage.somethingWentWrong') }}</h1>
          <p class="mb-6 text-sm text-gray-500">{{ errorMessage }}</p>
          <Button :label="t('errors.tryAgain')" icon="pi pi-refresh" rounded @click="$router.go(0)" />
        </div>
      </template>
    </div>
  </div>
</template>
