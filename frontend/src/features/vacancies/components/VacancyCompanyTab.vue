<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import type { EmployerCompany } from '@/features/employers/types/employer.types'

defineProps<{
  employersList: EmployerCompany[]
  loadingEmployers: boolean
  selectedEmployer: EmployerCompany | null
}>()

const emit = defineEmits<{
  openCreateDialog: []
}>()

const employerId = defineModel<string | null>('employerId', { required: true })

const { t } = useI18n()
</script>

<template>
  <div class="space-y-4 py-2">
    <!-- Employer dropdown + Add New -->
    <div>
      <label class="mb-1 block text-sm font-medium">{{ t('employers.selectEmployer') }}</label>
      <div class="flex gap-2">
        <Dropdown
          v-model="employerId"
          :options="employersList"
          option-label="name"
          option-value="id"
          :placeholder="t('employers.selectEmployer')"
          :loading="loadingEmployers"
          show-clear
          filter
          class="flex-1"
        />
        <Button
          type="button"
          icon="pi pi-plus"
          :label="t('employers.createNew')"
          severity="secondary"
          size="small"
          @click="emit('openCreateDialog')"
        />
      </div>
    </div>

    <!-- Selected employer preview -->
    <div v-if="selectedEmployer" class="rounded-xl border border-gray-200 bg-gray-50 p-4">
      <div class="flex items-center gap-3">
        <div
          v-if="selectedEmployer.logo"
          class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white ring-1 ring-gray-200"
        >
          <img
            :src="selectedEmployer.logo"
            :alt="selectedEmployer.name"
            class="h-full w-full object-contain"
          />
        </div>
        <div
          v-else
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600"
        >
          <i class="pi pi-building"></i>
        </div>
        <div class="min-w-0 flex-1">
          <p class="font-semibold text-gray-900">{{ selectedEmployer.name }}</p>
          <p v-if="selectedEmployer.industry" class="text-xs text-gray-500">
            {{ selectedEmployer.industry }}
          </p>
          <a
            v-if="selectedEmployer.website"
            :href="selectedEmployer.website"
            target="_blank"
            class="text-xs text-blue-500 hover:underline"
          >
            {{ selectedEmployer.website }}
          </a>
        </div>
      </div>
      <p
        v-if="selectedEmployer.description"
        class="mt-3 whitespace-pre-line text-sm leading-relaxed text-gray-600"
      >
        {{
          selectedEmployer.description.length > 300
            ? selectedEmployer.description.slice(0, 300) + '...'
            : selectedEmployer.description
        }}
      </p>
    </div>

    <!-- Empty state -->
    <div v-else class="rounded-xl border border-dashed border-gray-200 py-10 text-center">
      <i class="pi pi-building mb-2 text-3xl text-gray-300"></i>
      <p class="text-sm text-gray-500">{{ t('employers.selectEmployer') }}</p>
      <p class="mt-1 text-xs text-gray-400">{{ t('employers.orCreateNew') }}</p>
    </div>
  </div>
</template>
