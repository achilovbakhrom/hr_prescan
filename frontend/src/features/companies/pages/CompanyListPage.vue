<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import CompanyLogo from '@/shared/components/CompanyLogo.vue'
import { useCompanyStore } from '../stores/company.store'
import type { UserCompanyMembership } from '../types/company.types'

const { t } = useI18n()
const router = useRouter()
const confirm = useConfirm()
const companyStore = useCompanyStore()

onMounted(() => {
  companyStore.fetchCompanies()
})

const canDelete = computed(() => companyStore.liveCount > 1)

function handleDelete(company: UserCompanyMembership): void {
  if (!canDelete.value) return
  confirm.require({
    message: t('companies.deleteConfirm', { name: company.name }),
    header: t('companies.deleteConfirmHeader'),
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await companyStore.softDeleteCompany(company.id)
      } catch {
        // error surfaced via store.error
      }
    },
  })
}

async function handleSetDefault(company: UserCompanyMembership): Promise<void> {
  if (company.isDefault) return
  try {
    await companyStore.setDefaultCompany(company.id)
  } catch {
    // error surfaced via store.error
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-6">
    <ConfirmDialog />

    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-2xl font-bold text-gray-900">{{ t('companies.title') }}</h1>
      <Button
        :label="t('companies.create')"
        icon="pi pi-plus"
        @click="router.push({ name: ROUTE_NAMES.COMPANY_CREATE })"
      />
    </div>

    <div v-if="companyStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div v-else-if="companyStore.error" class="py-12 text-center text-red-600">
      <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
      <p>{{ companyStore.error }}</p>
    </div>

    <div
      v-else-if="companyStore.companies.length === 0"
      class="rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 px-6 py-16 text-center"
    >
      <i class="pi pi-building mb-4 text-5xl text-gray-300"></i>
      <h3 class="text-lg font-semibold text-gray-700">{{ t('companies.empty') }}</h3>
      <p class="mt-1 text-sm text-gray-500">{{ t('companies.emptyHint') }}</p>
      <Button
        :label="t('companies.create')"
        icon="pi pi-plus"
        class="mt-4"
        @click="router.push({ name: ROUTE_NAMES.COMPANY_CREATE })"
      />
    </div>

    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="company in companyStore.companies"
        :key="company.id"
        class="group relative cursor-pointer rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm transition-shadow hover:shadow-md"
        @click="router.push({ name: ROUTE_NAMES.COMPANY_DETAIL, params: { id: company.id } })"
      >
        <div class="mb-3 flex items-start gap-3">
          <CompanyLogo :logo="company.logo" :name="company.name" size="md" />
          <div class="min-w-0 flex-1">
            <h3 class="truncate text-base font-semibold text-gray-900">{{ company.name }}</h3>
            <p v-if="company.customIndustry" class="truncate text-sm text-gray-500">
              {{ company.customIndustry }}
            </p>
          </div>
        </div>

        <p v-if="company.website" class="mb-2 truncate text-sm text-blue-600">
          <i class="pi pi-globe mr-1 text-xs"></i>{{ company.website }}
        </p>

        <div class="mt-3 flex items-center justify-between border-t border-gray-100 dark:border-gray-800 pt-3">
          <Tag
            v-if="company.isDefault"
            :value="t('companies.default')"
            severity="success"
            icon="pi pi-check"
          />
          <Button
            v-else
            :label="t('companies.setAsDefault')"
            icon="pi pi-star"
            text
            size="small"
            @click.stop="handleSetDefault(company)"
          />
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            :disabled="!canDelete"
            :title="canDelete ? '' : t('companies.cannotDeleteLast')"
            class="opacity-0 transition-opacity group-hover:opacity-100"
            @click.stop="handleDelete(company)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
