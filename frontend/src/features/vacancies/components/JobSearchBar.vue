<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'

defineProps<{
  search: string
  location: string
  loading: boolean
  jobCount: number
}>()

const emit = defineEmits<{
  'update:search': [value: string]
  'update:location': [value: string]
  submit: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="border-b border-gray-100 bg-white">
    <div class="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
      <h1 class="mb-1 text-xl font-bold text-gray-900 sm:text-2xl">{{ t('jobBoard.title') }}</h1>
      <p class="mb-4 text-sm text-gray-500 sm:mb-5">
        {{ t('jobBoard.openPositions', { count: jobCount }) }}
      </p>

      <div class="flex flex-col gap-2 sm:flex-row sm:gap-3">
        <IconField class="flex-1">
          <InputIcon class="pi pi-search" />
          <InputText
            :model-value="search"
            class="w-full"
            :placeholder="t('jobBoard.searchPlaceholder')"
            @update:model-value="emit('update:search', $event as string)"
            @keyup.enter="emit('submit')"
          />
        </IconField>
        <div class="flex gap-2">
          <IconField class="flex-1 sm:w-48 sm:flex-initial">
            <InputIcon class="pi pi-map-marker" />
            <InputText
              :model-value="location"
              class="w-full"
              :placeholder="t('jobBoard.locationPlaceholder')"
              @update:model-value="emit('update:location', $event as string)"
              @keyup.enter="emit('submit')"
            />
          </IconField>
          <span class="shrink-0 sm:hidden">
            <Button icon="pi pi-search" :loading="loading" @click="emit('submit')" />
          </span>
          <span class="hidden shrink-0 sm:inline-flex">
            <Button
              :label="t('common.search')"
              icon="pi pi-search"
              :loading="loading"
              @click="emit('submit')"
            />
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
