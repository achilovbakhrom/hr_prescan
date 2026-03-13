<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { useCandidateStore } from '../stores/candidate.store'
import type { Vacancy } from '@/features/vacancies/types/vacancy.types'

const route = useRoute()
const candidateStore = useCandidateStore()
const vacancyId = route.params.vacancyId as string

const vacancy = ref<Vacancy | null>(null)
const vacancyLoading = ref(false)
const submitted = ref(false)
const name = ref('')
const email = ref('')
const phone = ref('')
const cvFile = ref<File | null>(null)
const errors = ref<Record<string, string>>({})

onMounted(async () => {
  vacancyLoading.value = true
  try {
    vacancy.value = await vacancyService.getPublicDetail(vacancyId)
  } catch {
    vacancy.value = null
  } finally {
    vacancyLoading.value = false
  }
})

function onFileSelect(event: FileUploadSelectEvent): void {
  cvFile.value = event.files[0] as File
}

function validate(): boolean {
  errors.value = {}
  if (!name.value.trim()) errors.value.name = 'Name is required'
  if (!email.value.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.value.email = 'Invalid email format'
  }
  return Object.keys(errors.value).length === 0
}

async function handleSubmit(): Promise<void> {
  if (!validate()) return
  try {
    await candidateStore.submitApplication(vacancyId, {
      candidateName: name.value.trim(),
      candidateEmail: email.value.trim(),
      candidatePhone: phone.value.trim() || undefined,
      cvFile: cvFile.value ?? undefined,
    })
    submitted.value = true
  } catch {
    /* store handles error */
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-8">
    <div v-if="vacancyLoading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <template v-else-if="submitted">
      <div class="py-12 text-center">
        <i class="pi pi-check-circle mb-4 text-5xl text-green-500"></i>
        <h1 class="mb-2 text-2xl font-bold">Application Submitted!</h1>
        <p class="text-gray-600">
          Thank you for applying{{ vacancy ? ` for ${vacancy.title}` : '' }}.
          We will review your application and get back to you soon.
        </p>
        <RouterLink to="/jobs" class="mt-4 inline-block text-blue-600 hover:underline">
          Browse more jobs
        </RouterLink>
      </div>
    </template>

    <template v-else>
      <RouterLink :to="`/jobs/${vacancyId}`" class="mb-4 inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
        <i class="pi pi-arrow-left mr-1"></i> Back to job details
      </RouterLink>

      <h1 class="mb-1 text-2xl font-bold">Apply for Position</h1>
      <p v-if="vacancy" class="mb-6 text-gray-600">{{ vacancy.title }}</p>

      <p v-if="candidateStore.error" class="mb-4 text-sm text-red-600">
        {{ candidateStore.error }}
      </p>

      <form class="space-y-5" @submit.prevent="handleSubmit">
        <div>
          <label class="mb-1 block text-sm font-medium">Full Name *</label>
          <InputText v-model="name" class="w-full" placeholder="John Doe" :invalid="!!errors.name" />
          <small v-if="errors.name" class="text-red-500">{{ errors.name }}</small>
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium">Email *</label>
          <InputText v-model="email" type="email" class="w-full" placeholder="john@example.com" :invalid="!!errors.email" />
          <small v-if="errors.email" class="text-red-500">{{ errors.email }}</small>
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium">Phone</label>
          <InputText v-model="phone" class="w-full" placeholder="+1 234 567 890" />
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium">CV / Resume</label>
          <FileUpload
            mode="basic"
            accept=".pdf,.docx"
            :max-file-size="10000000"
            choose-label="Choose CV"
            :auto="false"
            @select="onFileSelect"
          />
          <small class="text-gray-400">Accepted formats: PDF, DOCX (max 10MB)</small>
        </div>

        <Button
          type="submit"
          label="Submit Application"
          icon="pi pi-send"
          class="w-full"
          :loading="candidateStore.loading"
        />
      </form>
    </template>
  </div>
</template>
