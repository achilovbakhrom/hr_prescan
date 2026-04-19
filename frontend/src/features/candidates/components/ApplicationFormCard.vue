<script setup lang="ts">
/**
 * ApplicationFormCard — the "form" step of ApplicationFormPage.
 *
 * Extracted to keep the page under 200 lines. Owns the input layout only;
 * the parent page holds state, validation, and submission.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import GlassCard from '@/shared/components/GlassCard.vue'
import CvSelectionSection from './CvSelectionSection.vue'

interface VacancyBrief {
  title: string
  companyName?: string | null
  cvRequired?: boolean
  company?: { name?: string | null } | null
}

const props = defineProps<{
  vacancyId: string
  vacancy: VacancyBrief | null
  isLoggedIn: boolean
  fullName: string
  name: string
  email: string
  phone: string
  errors: Record<string, string>
  candidateStoreError: string | null
  candidateStoreLoading: boolean
}>()

const emit = defineEmits<{
  'update:name': [value: string]
  'update:email': [value: string]
  'update:phone': [value: string]
  'update:cvFile': [value: File | null]
  'update:cvId': [value: string | null]
  submit: []
}>()

const { t } = useI18n()

const displayCompany = computed(
  () => props.vacancy?.company?.name || props.vacancy?.companyName || '',
)

function onFileSelect(event: FileUploadSelectEvent): void {
  emit('update:cvFile', (event.files[0] as File) ?? null)
}
</script>

<template>
  <GlassCard>
    <RouterLink
      :to="`/jobs/${vacancyId}`"
      class="mb-4 inline-flex items-center text-sm text-[color:var(--color-text-muted)] hover:text-[color:var(--color-text-primary)]"
    >
      <i class="pi pi-arrow-left mr-1"></i> {{ t('candidates.application.backToJob') }}
    </RouterLink>

    <h1 class="mb-1 text-xl font-semibold sm:text-2xl">{{ t('candidates.application.title') }}</h1>
    <p v-if="vacancy" class="mb-1 text-sm text-[color:var(--color-text-secondary)] sm:text-base">
      {{ vacancy.title }}
    </p>
    <p v-if="displayCompany" class="mb-5 text-xs text-[color:var(--color-text-muted)] sm:text-sm">
      <i class="pi pi-building mr-1"></i>{{ displayCompany }}
    </p>
    <div v-else class="mb-5"></div>

    <div
      v-if="isLoggedIn"
      class="mb-4 inline-flex items-center gap-2 rounded-md bg-[color:var(--color-accent-soft)] px-3 py-2 text-sm text-[color:var(--color-accent)]"
    >
      <i class="pi pi-user"></i>
      {{ t('candidates.application.loggedInAs', { name: fullName }) }}
    </div>

    <p v-if="candidateStoreError" class="mb-4 text-sm text-[color:var(--color-danger)]">
      {{ candidateStoreError }}
    </p>

    <form class="space-y-4 sm:space-y-5" @submit.prevent="emit('submit')">
      <template v-if="isLoggedIn">
        <div
          class="bg-glass-2 grid grid-cols-1 gap-4 rounded-md border border-[color:var(--color-border-soft)] p-4 sm:grid-cols-2"
        >
          <div>
            <label class="block text-xs font-medium text-[color:var(--color-text-muted)]">
              {{ t('candidates.application.name') }}
            </label>
            <p class="text-sm font-medium text-[color:var(--color-text-primary)]">{{ name }}</p>
          </div>
          <div>
            <label class="block text-xs font-medium text-[color:var(--color-text-muted)]">
              {{ t('candidates.application.email') }}
            </label>
            <p class="text-sm font-medium text-[color:var(--color-text-primary)]">{{ email }}</p>
          </div>
        </div>
      </template>
      <template v-else>
        <div>
          <label class="mb-1 block text-sm font-medium">
            {{ t('candidates.application.name') }} *
          </label>
          <InputText
            :model-value="name"
            class="w-full"
            placeholder="John Doe"
            :invalid="!!errors.name"
            @update:model-value="emit('update:name', ($event as string) ?? '')"
          />
          <small v-if="errors.name" class="text-[color:var(--color-danger)]">
            {{ errors.name }}
          </small>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">
            {{ t('candidates.application.email') }} *
          </label>
          <InputText
            :model-value="email"
            type="email"
            class="w-full"
            placeholder="john@example.com"
            :invalid="!!errors.email"
            @update:model-value="emit('update:email', ($event as string) ?? '')"
          />
          <small v-if="errors.email" class="text-[color:var(--color-danger)]">
            {{ errors.email }}
          </small>
        </div>
      </template>

      <div>
        <label class="mb-1 block text-sm font-medium">
          {{ t('candidates.application.phone') }}
        </label>
        <InputText
          :model-value="phone"
          class="w-full"
          placeholder="+1 234 567 890"
          @update:model-value="emit('update:phone', ($event as string) ?? '')"
        />
      </div>

      <CvSelectionSection
        v-if="isLoggedIn"
        :cv-required="vacancy?.cvRequired ?? false"
        @update:cv-file="emit('update:cvFile', $event)"
        @update:cv-id="emit('update:cvId', $event)"
      />
      <div v-else>
        <label class="mb-1 block text-sm font-medium">
          {{ t('candidates.application.uploadCv')
          }}<span v-if="vacancy?.cvRequired" class="text-[color:var(--color-danger)]">*</span>
        </label>
        <FileUpload
          mode="basic"
          accept=".pdf,.docx"
          :max-file-size="10000000"
          :choose-label="t('candidates.application.chooseCv')"
          :auto="false"
          @select="onFileSelect"
        />
        <small class="text-[color:var(--color-text-muted)]">
          {{ t('candidates.application.acceptedFormats') }}
        </small>
      </div>

      <Button
        type="submit"
        :label="t('candidates.application.submit')"
        icon="pi pi-send"
        class="w-full"
        :loading="candidateStoreLoading"
      />
    </form>
  </GlassCard>
</template>
