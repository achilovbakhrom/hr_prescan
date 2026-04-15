<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type { GoogleAuthRole } from '../types/auth.types'

const props = defineProps<{
  visible: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  pick: [role: GoogleAuthRole]
}>()

const { t } = useI18n()

const dialogVisible = computed<boolean>({
  get: () => props.visible,
  set: (value: boolean) => emit('update:visible', value),
})

function pick(role: GoogleAuthRole): void {
  if (props.loading) return
  emit('pick', role)
}
</script>

<template>
  <Dialog
    v-model:visible="dialogVisible"
    :header="t('auth.rolePicker.title')"
    modal
    :closable="!loading"
    :close-on-escape="!loading"
    :dismissable-mask="false"
    :style="{ width: '90vw', maxWidth: '560px' }"
  >
    <p class="mb-6 text-sm text-gray-600">{{ t('auth.rolePicker.subtitle') }}</p>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <button
        type="button"
        :disabled="loading"
        class="flex flex-col items-start gap-2 rounded-lg border border-gray-200 bg-white p-5 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        @click="pick('candidate')"
      >
        <div
          class="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600"
        >
          <i class="pi pi-briefcase text-xl"></i>
        </div>
        <h3 class="text-base font-semibold text-gray-900">
          {{ t('auth.rolePicker.candidate.title') }}
        </h3>
        <p class="text-sm text-gray-600">
          {{ t('auth.rolePicker.candidate.description') }}
        </p>
      </button>

      <button
        type="button"
        :disabled="loading"
        class="flex flex-col items-start gap-2 rounded-lg border border-gray-200 bg-white p-5 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        @click="pick('hr')"
      >
        <div
          class="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-green-600"
        >
          <i class="pi pi-building text-xl"></i>
        </div>
        <h3 class="text-base font-semibold text-gray-900">
          {{ t('auth.rolePicker.hr.title') }}
        </h3>
        <p class="text-sm text-gray-600">
          {{ t('auth.rolePicker.hr.description') }}
        </p>
      </button>
    </div>

    <template #footer>
      <Button
        :label="t('auth.rolePicker.cancel')"
        severity="secondary"
        text
        :disabled="loading"
        @click="dialogVisible = false"
      />
    </template>
  </Dialog>
</template>
