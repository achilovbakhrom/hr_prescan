<script setup lang="ts">
/**
 * ApplicationBackgroundChoice — the candidate picks ONE way to share their
 * background: upload a CV (parsed and used by the AI prescreen) OR provide a
 * LinkedIn / portfolio link (a reference link for the recruiter — NOT analyzed
 * by the AI). When the vacancy requires a CV, only the CV option is shown.
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import FileUpload from 'primevue/fileupload'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import CvSelectionSection from './CvSelectionSection.vue'

defineProps<{
  isLoggedIn: boolean
  cvRequired: boolean
  linkedinUrl: string
}>()

const emit = defineEmits<{
  'update:cvFile': [value: File | null]
  'update:cvId': [value: string | null]
  'update:linkedinUrl': [value: string]
}>()

const { t } = useI18n()
type Method = 'cv' | 'linkedin'
const method = ref<Method>('cv')

function pick(m: Method): void {
  if (m === method.value) return
  method.value = m
  // keep only the chosen input populated
  if (m === 'cv') {
    emit('update:linkedinUrl', '')
  } else {
    emit('update:cvFile', null)
    emit('update:cvId', null)
  }
}

function onFileSelect(event: FileUploadSelectEvent): void {
  emit('update:cvFile', (event.files[0] as File) ?? null)
}
</script>

<template>
  <div>
    <label class="mb-2 block text-sm font-medium">
      {{ t('candidates.application.backgroundLabel') }}
      <span v-if="cvRequired" class="text-[color:var(--color-danger)]">*</span>
    </label>

    <!-- Toggle (hidden when the vacancy requires a CV) -->
    <div
      v-if="!cvRequired"
      class="mb-3 inline-flex rounded-lg border border-[color:var(--color-border-soft)] p-1"
    >
      <button
        type="button"
        class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
        :class="
          method === 'cv'
            ? 'bg-[color:var(--color-accent)] text-white'
            : 'text-[color:var(--color-text-secondary)]'
        "
        @click="pick('cv')"
      >
        {{ t('candidates.application.uploadCv') }}
      </button>
      <button
        type="button"
        class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors"
        :class="
          method === 'linkedin'
            ? 'bg-[color:var(--color-accent)] text-white'
            : 'text-[color:var(--color-text-secondary)]'
        "
        @click="pick('linkedin')"
      >
        {{ t('candidates.application.linkedin') }}
      </button>
    </div>

    <!-- CV -->
    <div v-if="method === 'cv' || cvRequired">
      <CvSelectionSection
        v-if="isLoggedIn"
        :cv-required="cvRequired"
        @update:cv-file="emit('update:cvFile', $event)"
        @update:cv-id="emit('update:cvId', $event)"
      />
      <template v-else>
        <FileUpload
          mode="basic"
          accept=".pdf,.docx"
          :max-file-size="10000000"
          :choose-label="t('candidates.application.chooseCv')"
          :auto="false"
          @select="onFileSelect"
        />
        <small class="mt-1 block text-[color:var(--color-text-muted)]">
          {{ t('candidates.application.acceptedFormats') }}
        </small>
      </template>
    </div>

    <!-- LinkedIn / portfolio (reference only) -->
    <div v-else>
      <InputText
        :model-value="linkedinUrl"
        class="w-full"
        placeholder="https://linkedin.com/in/…"
        @update:model-value="emit('update:linkedinUrl', ($event as string) ?? '')"
      />
      <small class="mt-1 block text-[color:var(--color-text-muted)]">
        {{ t('candidates.application.linkedinRefHint') }}
      </small>
    </div>
  </div>
</template>
