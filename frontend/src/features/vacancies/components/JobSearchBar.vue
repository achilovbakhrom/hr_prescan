<script setup lang="ts">
/**
 * JobSearchBar — glass hero for the public job board.
 *
 * T13: sits on top of the ambient background, using glass tokens so the
 * Aurora/Mesh/Constellation bleeds through.
 */
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
  <div class="relative border-b border-[color:var(--color-border-soft)]">
    <div class="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-10">
      <div class="mb-5 flex items-center gap-2">
        <span
          class="bg-glass-1 border-glass shadow-glass inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-medium text-[color:var(--color-accent-ai)]"
        >
          <i class="pi pi-briefcase text-[10px]"></i>
          {{ t('jobBoard.openPositions', { count: jobCount }) }}
        </span>
      </div>

      <h1 class="mb-1 text-2xl font-semibold text-[color:var(--color-text-primary)] sm:text-3xl">
        {{ t('jobBoard.title') }}
      </h1>
      <p class="mb-5 text-sm text-[color:var(--color-text-secondary)]">
        {{ t('jobBoard.openPositions', { count: jobCount }) }}
      </p>

      <div
        class="bg-glass-1 border-glass shadow-glass flex flex-col gap-2 rounded-lg p-2 sm:flex-row sm:gap-3 sm:p-3"
      >
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
