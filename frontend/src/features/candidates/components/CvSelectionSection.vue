<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import RadioButton from 'primevue/radiobutton'
import FileUpload from 'primevue/fileupload'
import type { FileUploadSelectEvent } from 'primevue/fileupload'
import { cvBuilderService } from '@/features/cv-builder/services/cv-builder.service'
import type { CvFile } from '@/features/cv-builder/types/cv-builder.types'

defineProps<{
  cvRequired: boolean
}>()

const emit = defineEmits<{
  'update:cvFile': [file: File | null]
  'update:cvId': [id: string | null]
}>()

const { t } = useI18n()

const cvs = ref<CvFile[]>([])
const loading = ref(false)
const cvMode = ref<'active' | 'upload'>('active')

const activeCv = computed(() => cvs.value.find((cv) => cv.isActive) ?? cvs.value[0] ?? null)

onMounted(async () => {
  loading.value = true
  try {
    cvs.value = await cvBuilderService.listCvs()
    if (activeCv.value) {
      cvMode.value = 'active'
      emit('update:cvId', activeCv.value.id)
    } else {
      cvMode.value = 'upload'
    }
  } catch {
    cvs.value = []
    cvMode.value = 'upload'
  } finally {
    loading.value = false
  }
})

function onModeChange(mode: 'active' | 'upload'): void {
  cvMode.value = mode
  if (mode === 'active' && activeCv.value) {
    emit('update:cvId', activeCv.value.id)
    emit('update:cvFile', null)
  } else {
    emit('update:cvId', null)
  }
}

function onFileSelect(event: FileUploadSelectEvent): void {
  emit('update:cvFile', event.files[0] as File)
  emit('update:cvId', null)
}
</script>

<template>
  <div>
    <label class="mb-1 block text-sm font-medium">
      {{ t('candidates.application.uploadCv') }}
      <span v-if="cvRequired" class="text-red-500">*</span>
    </label>

    <div v-if="loading" class="py-2 text-sm text-gray-400">
      <i class="pi pi-spinner pi-spin mr-1"></i>
    </div>

    <template v-else-if="activeCv">
      <div class="flex flex-col gap-3">
        <div class="flex items-center gap-2">
          <RadioButton
            v-model="cvMode"
            inputId="cv-active"
            value="active"
            @update:model-value="onModeChange"
          />
          <label for="cv-active" class="cursor-pointer text-sm">
            {{ t('candidates.application.useActiveCv', { name: activeCv.name }) }}
          </label>
        </div>
        <div class="flex items-center gap-2">
          <RadioButton
            v-model="cvMode"
            inputId="cv-upload"
            value="upload"
            @update:model-value="onModeChange"
          />
          <label for="cv-upload" class="cursor-pointer text-sm">
            {{ t('candidates.application.uploadNewCv') }}
          </label>
        </div>
        <div v-if="cvMode === 'upload'" class="pl-6">
          <FileUpload
            mode="basic"
            accept=".pdf,.docx"
            :max-file-size="10000000"
            :choose-label="t('candidates.application.chooseCv')"
            :auto="false"
            @select="onFileSelect"
          />
          <small class="text-gray-400">{{ t('candidates.application.acceptedFormats') }}</small>
        </div>
      </div>
    </template>

    <template v-else>
      <FileUpload
        mode="basic"
        accept=".pdf,.docx"
        :max-file-size="10000000"
        :choose-label="t('candidates.application.chooseCv')"
        :auto="false"
        @select="onFileSelect"
      />
      <small class="text-gray-400">{{ t('candidates.application.acceptedFormats') }}</small>
    </template>
  </div>
</template>
