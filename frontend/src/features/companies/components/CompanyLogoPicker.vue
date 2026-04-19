<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const MAX_LOGO_BYTES = 2 * 1024 * 1024

const props = defineProps<{
  logo: string | null
  name: string
  uploading: boolean
}>()

const emit = defineEmits<{
  pick: [file: File]
  reject: [reason: string]
}>()

const { t } = useI18n()
const inputRef = ref<HTMLInputElement | null>(null)

function open(): void {
  inputRef.value?.click()
}

function handleChange(event: Event): void {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (!file.type.startsWith('image/')) {
    emit('reject', t('companies.logoInvalidType'))
    return
  }
  if (file.size > MAX_LOGO_BYTES) {
    emit('reject', t('companies.logoTooLarge'))
    return
  }
  emit('pick', file)
}
</script>

<template>
  <button
    type="button"
    class="group relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-gray-100 transition hover:ring-2 hover:ring-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
    :title="t('companies.changeLogo')"
    :disabled="uploading"
    @click="open"
  >
    <img
      v-if="props.logo"
      :src="props.logo"
      :alt="props.name"
      class="h-full w-full object-contain"
    />
    <i v-else class="pi pi-building text-xl text-blue-600"></i>
    <span
      class="pointer-events-none absolute inset-0 flex items-center justify-center bg-black/40 text-white opacity-0 transition-opacity group-hover:opacity-100"
    >
      <i v-if="!uploading" class="pi pi-camera text-sm"></i>
      <i v-else class="pi pi-spinner pi-spin text-sm"></i>
    </span>
    <input
      ref="inputRef"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleChange"
    />
  </button>
</template>
