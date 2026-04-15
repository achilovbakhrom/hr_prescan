<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import type { FieldErrors } from '@/shared/api/errors'

defineProps<{
  name: string
  issuingOrganization: string
  issueDate: Date | null
  expiryDate: Date | null
  credentialUrl: string
  editingId: string | null
  saving: boolean
  fieldErrors: FieldErrors
}>()

const emit = defineEmits<{
  'update:name': [v: string]
  'update:issuingOrganization': [v: string]
  'update:issueDate': [v: Date | null]
  'update:expiryDate': [v: Date | null]
  'update:credentialUrl': [v: string]
  save: []
  cancel: []
}>()

const { t } = useI18n()
</script>

<template>
  <form
    class="mt-4 flex flex-col gap-4 rounded-lg border border-gray-200 p-4"
    @submit.prevent="emit('save')"
  >
    <h3 class="font-semibold text-gray-900">
      {{
        editingId ? t('cvBuilder.certifications.editTitle') : t('cvBuilder.certifications.addTitle')
      }}
    </h3>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="certName" class="text-sm font-medium text-gray-700"
          >{{ t('cvBuilder.certifications.name') }} <span class="text-red-500">*</span></label
        >
        <InputText
          id="certName"
          :model-value="name"
          class="w-full"
          :invalid="'name' in fieldErrors"
          @update:model-value="emit('update:name', $event as string)"
        />
        <small v-if="'name' in fieldErrors" class="text-red-500">{{ fieldErrors.name }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="certOrg" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.certifications.issuingOrganization')
        }}</label>
        <InputText
          id="certOrg"
          :model-value="issuingOrganization"
          class="w-full"
          :invalid="'issuingOrganization' in fieldErrors"
          @update:model-value="emit('update:issuingOrganization', $event as string)"
        />
        <small v-if="'issuingOrganization' in fieldErrors" class="text-red-500">{{
          fieldErrors.issuingOrganization
        }}</small>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="flex flex-col gap-1">
        <label for="certIssueDate" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.certifications.issueDate')
        }}</label>
        <DatePicker
          id="certIssueDate"
          :model-value="issueDate"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :invalid="'issueDate' in fieldErrors"
          @update:model-value="emit('update:issueDate', $event as Date | null)"
        />
        <small v-if="'issueDate' in fieldErrors" class="text-red-500">{{
          fieldErrors.issueDate
        }}</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="certExpiryDate" class="text-sm font-medium text-gray-700">{{
          t('cvBuilder.certifications.expiryDate')
        }}</label>
        <DatePicker
          id="certExpiryDate"
          :model-value="expiryDate"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :invalid="'expiryDate' in fieldErrors"
          @update:model-value="emit('update:expiryDate', $event as Date | null)"
        />
        <small v-if="'expiryDate' in fieldErrors" class="text-red-500">{{
          fieldErrors.expiryDate
        }}</small>
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <label for="certUrl" class="text-sm font-medium text-gray-700">{{
        t('cvBuilder.certifications.credentialUrl')
      }}</label>
      <InputText
        id="certUrl"
        :model-value="credentialUrl"
        placeholder="https://..."
        class="w-full"
        :invalid="'credentialUrl' in fieldErrors"
        @update:model-value="emit('update:credentialUrl', $event as string)"
      />
      <small v-if="'credentialUrl' in fieldErrors" class="text-red-500">{{
        fieldErrors.credentialUrl
      }}</small>
    </div>

    <div class="flex justify-end gap-2">
      <Button :label="t('common.cancel')" severity="secondary" text @click="emit('cancel')" />
      <Button type="submit" :label="t('common.save')" :loading="saving" />
    </div>
  </form>
</template>
