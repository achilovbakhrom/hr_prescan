<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Message from 'primevue/message'
import { useSettingsStore } from '../stores/settings.store'
import CompanyProfileForm from '../components/CompanyProfileForm.vue'

const { t } = useI18n()
const settingsStore = useSettingsStore()

const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-6 text-2xl font-bold text-gray-900">{{ t('settings.company.title') }}</h1>

    <Message v-if="successMessage" severity="success" class="mb-4">{{ successMessage }}</Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <div
      v-if="settingsStore.loading && !settingsStore.companyProfile"
      class="py-12 text-center text-gray-500"
    >
      {{ t('settings.company.loadingProfile') }}
    </div>

    <CompanyProfileForm
      v-else
      @success="
        (msg) => {
          successMessage = msg
          errorMessage = null
        }
      "
      @error="
        (msg) => {
          errorMessage = msg
          successMessage = null
        }
      "
    />
  </div>
</template>
