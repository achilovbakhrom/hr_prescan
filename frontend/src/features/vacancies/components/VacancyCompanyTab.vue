<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import CompanyLogo from '@/shared/components/CompanyLogo.vue'
import type { UserCompanyMembership } from '@/features/companies/types/company.types'

defineProps<{
  companiesList: UserCompanyMembership[]
  loadingCompanies: boolean
  selectedCompany: UserCompanyMembership | null
}>()

const emit = defineEmits<{
  openCreateDialog: []
}>()

const companyId = defineModel<string | null>('companyId', { required: true })

const { t } = useI18n()
</script>

<template>
  <div class="space-y-4 py-2">
    <div>
      <label class="mb-1 block text-sm font-medium">{{ t('companies.selectCompany') }}</label>
      <div class="flex gap-2">
        <Dropdown
          v-model="companyId"
          :options="companiesList"
          option-label="name"
          option-value="id"
          :placeholder="t('companies.selectCompany')"
          :loading="loadingCompanies"
          show-clear
          filter
          class="flex-1"
        />
        <Button
          type="button"
          icon="pi pi-plus"
          :label="t('companies.createNew')"
          severity="secondary"
          size="small"
          @click="emit('openCreateDialog')"
        />
      </div>
    </div>

    <div v-if="selectedCompany" class="rounded-xl border border-gray-200 bg-gray-50 p-4">
      <div class="flex items-center gap-3">
        <CompanyLogo :logo="selectedCompany.logo" :name="selectedCompany.name" size="md" />
        <div class="min-w-0 flex-1">
          <p class="font-semibold text-gray-900">
            {{ selectedCompany.name }}
            <Tag
              v-if="selectedCompany.isDefault"
              :value="t('companies.default')"
              severity="success"
              class="ml-1 align-middle"
            />
          </p>
          <p v-if="selectedCompany.customIndustry" class="text-xs text-gray-500">
            {{ selectedCompany.customIndustry }}
          </p>
          <a
            v-if="selectedCompany.website"
            :href="selectedCompany.website"
            target="_blank"
            class="text-xs text-blue-500 hover:underline"
          >
            {{ selectedCompany.website }}
          </a>
        </div>
      </div>
      <p
        v-if="selectedCompany.description"
        class="mt-3 whitespace-pre-line text-sm leading-relaxed text-gray-600"
      >
        {{
          selectedCompany.description.length > 300
            ? selectedCompany.description.slice(0, 300) + '...'
            : selectedCompany.description
        }}
      </p>
    </div>

    <div v-else class="rounded-xl border border-dashed border-gray-200 py-10 text-center">
      <i class="pi pi-building mb-2 text-3xl text-gray-300"></i>
      <p class="text-sm text-gray-500">{{ t('companies.selectCompany') }}</p>
      <p class="mt-1 text-xs text-gray-400">{{ t('companies.orCreateNew') }}</p>
    </div>
  </div>
</template>
