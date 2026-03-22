<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useEmployerStore } from '../stores/employer.store'
import type { EmployerCompany } from '../types/employer.types'

const { t } = useI18n()
const router = useRouter()
const confirm = useConfirm()
const employerStore = useEmployerStore()

onMounted(() => {
  employerStore.fetchEmployers()
})

function sourceSeverity(source: EmployerCompany['source']): 'info' | 'success' | 'warn' {
  if (source === 'manual') return 'info'
  if (source === 'file') return 'warn'
  return 'success'
}

function sourceLabel(source: EmployerCompany['source']): string {
  if (source === 'manual') return t('employers.manual')
  if (source === 'file') return t('employers.file')
  return t('employers.fromWebsite')
}

function handleDelete(employer: EmployerCompany): void {
  confirm.require({
    message: t('employers.deleteConfirm'),
    header: t('employers.deleteConfirmHeader'),
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await employerStore.deleteEmployer(employer.id)
      } catch {
        // error is displayed via store
      }
    },
  })
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6">
    <ConfirmDialog />

    <!-- Header -->
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ t('employers.title') }}</h1>
      </div>
      <Button
        :label="t('employers.create')"
        icon="pi pi-plus"
        @click="router.push({ name: ROUTE_NAMES.EMPLOYER_CREATE })"
      />
    </div>

    <!-- Loading -->
    <div v-if="employerStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <!-- Error -->
    <div v-else-if="employerStore.error" class="py-12 text-center text-red-600">
      <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
      <p>{{ employerStore.error }}</p>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="employerStore.employers.length === 0"
      class="rounded-xl border-2 border-dashed border-gray-200 px-6 py-16 text-center"
    >
      <i class="pi pi-building mb-4 text-5xl text-gray-300"></i>
      <h3 class="text-lg font-semibold text-gray-700">{{ t('employers.noEmployers') }}</h3>
      <p class="mt-1 text-sm text-gray-500">{{ t('employers.noEmployersHint') }}</p>
      <Button
        :label="t('employers.create')"
        icon="pi pi-plus"
        class="mt-4"
        @click="router.push({ name: ROUTE_NAMES.EMPLOYER_CREATE })"
      />
    </div>

    <!-- Employer cards -->
    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="employer in employerStore.employers"
        :key="employer.id"
        class="group relative cursor-pointer rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
        @click="router.push({ name: ROUTE_NAMES.EMPLOYER_DETAIL, params: { id: employer.id } })"
      >
        <!-- Top row: logo + name -->
        <div class="mb-3 flex items-start gap-3">
          <div
            v-if="employer.logo"
            class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-gray-100"
          >
            <img :src="employer.logo" :alt="employer.name" class="h-full w-full object-contain" />
          </div>
          <div
            v-else
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600"
          >
            <i class="pi pi-building text-lg"></i>
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="truncate text-base font-semibold text-gray-900">{{ employer.name }}</h3>
            <p v-if="employer.industry" class="truncate text-sm text-gray-500">{{ employer.industry }}</p>
          </div>
        </div>

        <!-- Website -->
        <p v-if="employer.website" class="mb-2 truncate text-sm text-blue-600">
          <i class="pi pi-globe mr-1 text-xs"></i>{{ employer.website }}
        </p>

        <!-- Footer: source badge + delete -->
        <div class="mt-3 flex items-center justify-between border-t border-gray-100 pt-3">
          <Tag :value="sourceLabel(employer.source)" :severity="sourceSeverity(employer.source)" />
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            class="opacity-0 transition-opacity group-hover:opacity-100"
            @click.stop="handleDelete(employer)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
