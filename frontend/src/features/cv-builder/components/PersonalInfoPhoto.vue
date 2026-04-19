<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useCvBuilderStore } from '../stores/cv-builder.store'

const emit = defineEmits<{
  success: [message: string]
  error: [message: string]
}>()

const { t } = useI18n()
const store = useCvBuilderStore()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const removing = ref(false)

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_SIZE = 5 * 1024 * 1024

const photoUrl = computed(() => store.profile?.photoUrl || null)
const hasPhoto = computed(() => Boolean(photoUrl.value))

function openPicker(): void {
  fileInput.value?.click()
}

async function onFileChange(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  target.value = ''
  if (!file) return

  if (!ALLOWED_TYPES.includes(file.type)) {
    emit('error', t('cvBuilder.personal.photoInvalidType'))
    return
  }
  if (file.size > MAX_SIZE) {
    emit('error', t('cvBuilder.personal.photoTooLarge'))
    return
  }

  uploading.value = true
  try {
    await store.uploadPhoto(file)
    emit('success', t('cvBuilder.personal.photoUploadSuccess'))
  } catch (err: unknown) {
    emit('error', err instanceof Error ? err.message : t('common.error'))
  } finally {
    uploading.value = false
  }
}

async function removePhoto(): Promise<void> {
  removing.value = true
  try {
    await store.deletePhoto()
    emit('success', t('cvBuilder.personal.photoRemoveSuccess'))
  } catch (err: unknown) {
    emit('error', err instanceof Error ? err.message : t('common.error'))
  } finally {
    removing.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <label class="text-sm font-medium text-gray-700">
      {{ t('cvBuilder.personal.photo') }}
    </label>
    <div class="flex flex-col items-start gap-3 sm:flex-row sm:items-center">
      <div
        class="flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-full border border-gray-200 bg-gray-50"
      >
        <img
          v-if="hasPhoto"
          :src="photoUrl!"
          :alt="t('cvBuilder.personal.photo')"
          class="h-full w-full object-cover"
        />
        <i v-else class="pi pi-user text-3xl text-gray-400" />
      </div>
      <div class="flex flex-col gap-2">
        <div class="flex flex-wrap items-center gap-2">
          <Button
            :label="
              hasPhoto ? t('cvBuilder.personal.changePhoto') : t('cvBuilder.personal.uploadPhoto')
            "
            icon="pi pi-upload"
            size="small"
            :loading="uploading"
            @click="openPicker"
          />
          <Button
            v-if="hasPhoto"
            :label="t('cvBuilder.personal.removePhoto')"
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            :loading="removing"
            @click="removePhoto"
          />
        </div>
        <p class="text-xs text-gray-500">{{ t('cvBuilder.personal.photoHint') }}</p>
      </div>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="hidden"
      @change="onFileChange"
    />
  </div>
</template>
