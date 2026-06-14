<script setup lang="ts">
/**
 * ApplicationExtraFields — optional extras on the apply form: profile photo,
 * a short "why are you a great fit?" note, and the required AI-prescreening +
 * privacy consent checkbox. (CV vs LinkedIn lives in ApplicationBackgroundChoice.)
 */
import { useI18n } from 'vue-i18n'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import FileUpload from 'primevue/fileupload'
import type { FileUploadSelectEvent } from 'primevue/fileupload'

defineProps<{
  coverNote: string
  prescreenConsent: boolean
  consentError?: string
}>()

const emit = defineEmits<{
  'update:profilePhoto': [value: File | null]
  'update:coverNote': [value: string]
  'update:prescreenConsent': [value: boolean]
}>()

const { t } = useI18n()

function onPhotoSelect(event: FileUploadSelectEvent): void {
  emit('update:profilePhoto', (event.files[0] as File) ?? null)
}
</script>

<template>
  <div>
    <label class="mb-1 block text-sm font-medium">
      {{ t('candidates.application.profilePhoto') }}
    </label>
    <FileUpload
      mode="basic"
      accept="image/*"
      :max-file-size="5000000"
      :choose-label="t('candidates.application.choosePhoto')"
      :auto="false"
      @select="onPhotoSelect"
    />
    <small class="text-[color:var(--color-text-muted)]">
      {{ t('candidates.application.profilePhotoHint') }}
    </small>
  </div>

  <div>
    <label class="mb-1 block text-sm font-medium">
      {{ t('candidates.application.coverNote') }}
    </label>
    <Textarea
      :model-value="coverNote"
      class="w-full"
      rows="3"
      :placeholder="t('candidates.application.coverNotePlaceholder')"
      @update:model-value="emit('update:coverNote', ($event as string) ?? '')"
    />
  </div>

  <div>
    <label class="flex items-start gap-2 text-sm">
      <Checkbox
        :model-value="prescreenConsent"
        binary
        :invalid="!!consentError"
        @update:model-value="emit('update:prescreenConsent', !!$event)"
      />
      <span>{{ t('candidates.application.consent') }}</span>
    </label>
    <small v-if="consentError" class="text-[color:var(--color-danger)]">
      {{ consentError }}
    </small>
  </div>
</template>
