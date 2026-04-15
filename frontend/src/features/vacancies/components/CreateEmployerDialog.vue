<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import SelectButton from 'primevue/selectbutton'
import FileUpload from 'primevue/fileupload'
import { extractErrorMessage } from '@/shared/api/errors'
import { employerService } from '@/features/employers/services/employer.service'
import type { EmployerCompany } from '@/features/employers/types/employer.types'

const emit = defineEmits<{
  created: [employer: EmployerCompany]
}>()

const visible = defineModel<boolean>('visible', { required: true })

const { t } = useI18n()

const createMode = ref<'manual' | 'file' | 'website'>('manual')
const createModeOptions = computed(() => [
  { label: t('employers.manual'), value: 'manual' },
  { label: t('employers.file'), value: 'file' },
  { label: t('employers.fromWebsite'), value: 'website' },
])
const newEmployerName = ref('')
const newEmployerIndustry = ref('')
const newEmployerWebsite = ref('')
const newEmployerDescription = ref('')
const newEmployerUrl = ref('')
const creatingEmployer = ref(false)
const createError = ref('')

function resetForm(): void {
  newEmployerName.value = ''
  newEmployerIndustry.value = ''
  newEmployerWebsite.value = ''
  newEmployerDescription.value = ''
  newEmployerUrl.value = ''
  createMode.value = 'manual'
  createError.value = ''
}

async function handleCreateEmployer(): Promise<void> {
  if (!newEmployerName.value) return
  creatingEmployer.value = true
  createError.value = ''
  try {
    let employer: EmployerCompany
    if (createMode.value === 'file') return
    else if (createMode.value === 'website') {
      employer = await employerService.createFromUrl(newEmployerName.value, newEmployerUrl.value)
    } else {
      employer = await employerService.create({
        name: newEmployerName.value,
        industry: newEmployerIndustry.value,
        website: newEmployerWebsite.value,
        description: newEmployerDescription.value,
      })
    }
    emit('created', employer)
    visible.value = false
  } catch (err: unknown) {
    createError.value = extractErrorMessage(err)
  } finally {
    creatingEmployer.value = false
  }
}

async function handleCreateFromFile(event: { files: File | File[] }): Promise<void> {
  const files = Array.isArray(event.files) ? event.files : [event.files]
  const file = files[0]
  if (!file || !newEmployerName.value) return
  creatingEmployer.value = true
  createError.value = ''
  try {
    const employer = await employerService.createFromFile(newEmployerName.value, file)
    emit('created', employer)
    visible.value = false
  } catch (err: unknown) {
    createError.value = extractErrorMessage(err)
  } finally {
    creatingEmployer.value = false
  }
}
</script>

<template>
  <Dialog
    v-model:visible="visible"
    :header="t('employers.create')"
    modal
    :style="{ width: '500px' }"
    :breakpoints="{ '640px': '95vw' }"
    @show="resetForm"
  >
    <div class="space-y-4">
      <SelectButton
        v-model="createMode"
        :options="createModeOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />

      <div>
        <label class="mb-1 block text-sm font-medium"
          >{{ t('employers.name') }} <span class="text-red-500">*</span></label
        >
        <InputText
          v-model="newEmployerName"
          class="w-full"
          :placeholder="t('employers.namePlaceholder')"
        />
      </div>

      <template v-if="createMode === 'manual'">
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.industry') }}</label>
          <InputText v-model="newEmployerIndustry" class="w-full" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.website') }}</label>
          <InputText v-model="newEmployerWebsite" class="w-full" placeholder="https://" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.description') }}</label>
          <Textarea v-model="newEmployerDescription" class="w-full" rows="4" />
        </div>
      </template>

      <template v-if="createMode === 'website'">
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.websiteUrl') }}</label>
          <InputText
            v-model="newEmployerUrl"
            class="w-full"
            :placeholder="t('employers.urlPlaceholder')"
          />
          <p class="mt-1 text-xs text-gray-400">AI will extract company info from this page</p>
        </div>
      </template>

      <template v-if="createMode === 'file'">
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.uploadFile') }}</label>
          <p class="mb-2 text-xs text-gray-400">PDF, DOCX, or TXT. AI will extract company info.</p>
          <FileUpload
            mode="basic"
            accept=".pdf,.docx,.doc,.txt"
            :max-file-size="10000000"
            :choose-label="t('employers.uploadFile')"
            :auto="true"
            :custom-upload="true"
            :disabled="creatingEmployer"
            @uploader="handleCreateFromFile"
          />
        </div>
      </template>

      <p v-if="createError" class="text-sm text-red-500">{{ createError }}</p>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button :label="t('common.cancel')" severity="secondary" text @click="visible = false" />
        <Button
          v-if="createMode !== 'file'"
          :label="t('common.save')"
          icon="pi pi-check"
          :loading="creatingEmployer"
          :disabled="!newEmployerName"
          @click="handleCreateEmployer"
        />
      </div>
    </template>
  </Dialog>
</template>
