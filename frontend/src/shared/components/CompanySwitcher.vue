<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Select from 'primevue/select'
import CompanyLogo from '@/shared/components/CompanyLogo.vue'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const activeCompanyId = computed(() => authStore.user?.company?.id ?? 'personal')

// Show the account owner as a prefix only when the current user isn't the owner —
// i.e., they're an invited member operating under someone else's account.
const accountPrefix = computed(() =>
  authStore.user?.isAccountOwner === false && authStore.user.accountOwnerName
    ? `${authStore.user.accountOwnerName} · `
    : '',
)

const companyOptions = computed(() => {
  const options: { label: string; value: string }[] = []
  if (authStore.companies.length > 0)
    options.push({ label: t('common.personal'), value: 'personal' })
  for (const m of authStore.companies)
    options.push({ label: `${accountPrefix.value}${m.company.name}`, value: m.company.id })
  return options
})

const showSwitcher = computed(() => companyOptions.value.length > 1)

async function handleCompanySwitch(value: string): Promise<void> {
  if (value === activeCompanyId.value) return
  if (value === 'personal') await authStore.switchToPersonal()
  else await authStore.switchCompany(value)
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}
</script>

<template>
  <div v-if="showSwitcher" class="hidden items-center gap-2 sm:inline-flex">
    <CompanyLogo
      v-if="authStore.user?.company"
      :logo="authStore.user.company.logo"
      :name="authStore.user.company.name"
      size="xs"
      rounded="md"
    />
    <Select
      :model-value="activeCompanyId"
      :options="companyOptions"
      option-label="label"
      option-value="value"
      class="!text-xs"
      :pt="{ root: { class: '!py-1 !px-2 !min-w-0 max-w-48' }, label: { class: '!text-xs !py-0' } }"
      @update:model-value="handleCompanySwitch"
    />
  </div>
  <div
    v-else-if="authStore.user?.company"
    class="hidden items-center gap-2 rounded-md bg-gray-100 dark:bg-gray-800 px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-400 sm:inline-flex"
  >
    <CompanyLogo
      :logo="authStore.user.company.logo"
      :name="authStore.user.company.name"
      size="xs"
      rounded="md"
    />
    {{ authStore.user.company.name }}
  </div>
</template>
