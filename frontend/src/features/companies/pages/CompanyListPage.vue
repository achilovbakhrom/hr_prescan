<script setup lang="ts">
/**
 * CompanyListPage — grid of company cards (GlassCard each).
 * Spec: docs/design/spec.md §9 Companies block.
 */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useConfirm } from 'primevue/useconfirm'
import ConfirmDialog from 'primevue/confirmdialog'
import GlassCard from '@/shared/components/GlassCard.vue'
import CompanyCardItem from '../components/CompanyCardItem.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import CompanyLogo from '@/shared/components/CompanyLogo.vue'
import { useCompanyStore } from '../stores/company.store'
import type { UserCompanyMembership } from '../types/company.types'

const { t } = useI18n()
const router = useRouter()
const confirm = useConfirm()
const companyStore = useCompanyStore()

onMounted(() => companyStore.fetchCompanies())

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
        /* error surfaced via store */
      }
    },
  })
}

async function handleSetDefault(company: UserCompanyMembership): Promise<void> {
  if (company.isDefault) return
  try {
    await companyStore.setDefaultCompany(company.id)
  } catch {
    /* error surfaced via store */
  }
}

function openDetail(company: UserCompanyMembership): void {
  router.push({ name: ROUTE_NAMES.COMPANY_DETAIL, params: { id: company.id } })
}
</script>

<template>
  <div class="space-y-5">
    <ConfirmDialog />

    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
          {{ t('companies.title') }}
        </h1>
        <p class="mt-0.5 text-sm text-[color:var(--color-text-muted)]">
          {{ companyStore.companies.length }} {{ t('companies.title').toLowerCase() }}
        </p>
      </div>
      <Button
        :label="t('companies.create')"
        icon="pi pi-plus"
        @click="router.push({ name: ROUTE_NAMES.COMPANY_CREATE })"
      />
    </div>

    <div v-if="companyStore.loading" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <GlassCard v-else-if="companyStore.error" class="text-center">
      <i class="pi pi-exclamation-circle mb-3 text-4xl text-[color:var(--color-danger)]"></i>
      <p class="text-[color:var(--color-danger)]">{{ companyStore.error }}</p>
    </GlassCard>

    <GlassCard v-else-if="companyStore.companies.length === 0" class="text-center">
      <i class="pi pi-building mb-4 text-5xl text-[color:var(--color-text-muted)]"></i>
      <h3 class="text-lg font-semibold text-[color:var(--color-text-primary)]">
        {{ t('companies.empty') }}
      </h3>
      <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
        {{ t('companies.emptyHint') }}
      </p>
      <Button
        :label="t('companies.create')"
        icon="pi pi-plus"
        class="mt-4"
        @click="router.push({ name: ROUTE_NAMES.COMPANY_CREATE })"
      />
    </GlassCard>

    <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <CompanyCardItem
        v-for="company in companyStore.companies"
        :key="company.id"
        :company="company"
        :can-delete="canDelete"
        @open="openDetail(company)"
        @set-default="handleSetDefault(company)"
        @delete="handleDelete(company)"
      />
    </div>
  </div>
</template>
