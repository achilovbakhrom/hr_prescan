<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Select from '@/shared/components/AppSelect.vue'
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

interface CompanyOption {
  label: string
  value: string
  logo?: string | null
  isPersonal?: boolean
}

const companyOptions = computed(() => {
  const options: CompanyOption[] = []
  if (authStore.companies.length > 0)
    options.push({ label: t('common.personal'), value: 'personal', isPersonal: true })
  for (const m of authStore.companies)
    options.push({
      label: `${accountPrefix.value}${m.company.name}`,
      value: m.company.id,
      logo: m.company.logo,
    })
  return options
})

const showSwitcher = computed(() => companyOptions.value.length > 1)
const activeCompanyOption = computed(
  () => companyOptions.value.find((option) => option.value === activeCompanyId.value) ?? null,
)

async function handleCompanySwitch(value: string): Promise<void> {
  if (value === activeCompanyId.value) return
  if (value === 'personal') await authStore.switchToPersonal()
  else await authStore.switchCompany(value)
  router.push({ name: ROUTE_NAMES.DASHBOARD })
}
</script>

<template>
  <div v-if="showSwitcher" class="hidden items-center gap-2 sm:inline-flex">
    <Select
      :model-value="activeCompanyId"
      :options="companyOptions"
      option-label="label"
      option-value="value"
      class="max-w-56 min-w-44 text-xs"
      size="small"
      @update:model-value="handleCompanySwitch"
    >
      <template #value="{ placeholder }">
        <div
          v-if="activeCompanyOption"
          class="flex min-w-0 items-center gap-2 py-0.5 text-left text-xs font-medium"
        >
          <span
            v-if="activeCompanyOption.isPersonal"
            class="flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
          >
            <i class="pi pi-user text-[10px]"></i>
          </span>
          <CompanyLogo
            v-else
            :logo="activeCompanyOption.logo"
            :name="activeCompanyOption.label"
            size="xs"
            rounded="md"
          />
          <span class="truncate">{{ activeCompanyOption.label }}</span>
        </div>
        <span v-else class="text-xs text-[color:var(--color-text-muted)]">{{ placeholder }}</span>
      </template>
      <template #option="{ option }">
        <div class="flex min-w-0 items-center gap-2 py-0.5 text-sm">
          <span
            v-if="option.isPersonal"
            class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
          >
            <i class="pi pi-user text-xs"></i>
          </span>
          <CompanyLogo v-else :logo="option.logo" :name="option.label" size="xs" rounded="md" />
          <span class="truncate">{{ option.label }}</span>
        </div>
      </template>
    </Select>
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
