<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'
import { useSettingsStore } from '../stores/settings.store'
import type { CompanySize } from '@/shared/types/auth.types'

const { t } = useI18n()
const settingsStore = useSettingsStore()

const name = ref('')
const industry = ref('')
const size = ref<CompanySize | null>(null)
const country = ref('')
const website = ref('')
const description = ref('')
const submitted = ref(false)
const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

const sizeOptions = [
  { label: '1-50 employees', value: 'small' as CompanySize },
  { label: '51-200 employees', value: 'medium' as CompanySize },
  { label: '201-1000 employees', value: 'large' as CompanySize },
  { label: '1000+ employees', value: 'enterprise' as CompanySize },
]

const errors = ref({
  name: false,
  industry: false,
  size: false,
  country: false,
})

function populateForm(): void {
  const profile = settingsStore.companyProfile
  if (!profile) return
  name.value = profile.name
  industry.value = profile.industry
  size.value = profile.size
  country.value = profile.country
  website.value = profile.website ?? ''
  description.value = ''
}

onMounted(async () => {
  await settingsStore.fetchProfile()
  populateForm()
})

function validate(): boolean {
  errors.value.name = !name.value.trim()
  errors.value.industry = !industry.value.trim()
  errors.value.size = !size.value
  errors.value.country = !country.value.trim()
  return !Object.values(errors.value).some(Boolean)
}

async function handleSave(): Promise<void> {
  submitted.value = true
  successMessage.value = null
  errorMessage.value = null

  if (!validate()) return

  try {
    await settingsStore.updateProfile({
      name: name.value,
      industry: industry.value,
      size: size.value!,
      country: country.value,
      website: website.value.trim() || null,
      description: description.value.trim() || null,
    })
    successMessage.value = 'Company profile updated successfully.'
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error
        ? err.message
        : 'Failed to update profile. Please try again.'
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-6 text-2xl font-bold text-gray-900">{{ t('settings.company.title') }}</h1>

    <Message v-if="successMessage" severity="success" class="mb-4">
      {{ successMessage }}
    </Message>

    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <div
      v-if="settingsStore.loading && !settingsStore.companyProfile"
      class="py-12 text-center text-gray-500"
    >
      Loading company profile...
    </div>

    <form
      v-else
      class="flex flex-col gap-5 rounded-lg bg-white p-6 shadow-sm"
      @submit.prevent="handleSave"
    >
      <div class="flex flex-col gap-1">
        <label class="mb-2 text-sm font-medium text-gray-700">
          {{ t('settings.company.logo') }}
        </label>
        <FileUpload
          mode="basic"
          accept="image/*"
          :max-file-size="2000000"
          choose-label="Upload Logo"
          class="w-auto"
          disabled
        />
        <small class="text-gray-500">Logo upload coming soon.</small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="name" class="text-sm font-medium text-gray-700">
          {{ t('settings.company.name') }}
        </label>
        <InputText
          id="name"
          v-model="name"
          placeholder="Enter company name"
          :invalid="submitted && errors.name"
          class="w-full"
        />
        <small v-if="submitted && errors.name" class="text-red-500">
          Company name is required.
        </small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="industry" class="text-sm font-medium text-gray-700">
          {{ t('settings.company.industry') }}
        </label>
        <InputText
          id="industry"
          v-model="industry"
          placeholder="e.g. Technology, Healthcare, Finance"
          :invalid="submitted && errors.industry"
          class="w-full"
        />
        <small v-if="submitted && errors.industry" class="text-red-500">
          Industry is required.
        </small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="size" class="text-sm font-medium text-gray-700">
          {{ t('settings.company.size') }}
        </label>
        <Select
          id="size"
          v-model="size"
          :options="sizeOptions"
          option-label="label"
          option-value="value"
          placeholder="Select company size"
          :invalid="submitted && errors.size"
          class="w-full"
        />
        <small v-if="submitted && errors.size" class="text-red-500">
          Company size is required.
        </small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="country" class="text-sm font-medium text-gray-700">
          {{ t('settings.company.country') }}
        </label>
        <InputText
          id="country"
          v-model="country"
          placeholder="Enter country"
          :invalid="submitted && errors.country"
          class="w-full"
        />
        <small v-if="submitted && errors.country" class="text-red-500">
          Country is required.
        </small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="website" class="text-sm font-medium text-gray-700">
          {{ t('settings.company.website') }}
        </label>
        <InputText
          id="website"
          v-model="website"
          placeholder="https://example.com"
          class="w-full"
        />
      </div>

      <div class="flex flex-col gap-1">
        <label for="description" class="text-sm font-medium text-gray-700">
          {{ t('settings.company.description') }}
        </label>
        <Textarea
          id="description"
          v-model="description"
          placeholder="Tell us about your company"
          rows="4"
          class="w-full"
        />
      </div>

      <div class="flex justify-end pt-2">
        <Button
          type="submit"
          :label="t('settings.company.save')"
          :loading="settingsStore.loading"
        />
      </div>
    </form>
  </div>
</template>
