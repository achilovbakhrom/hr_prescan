<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Select from 'primevue/select'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const activeCompanyId = computed(() => authStore.user?.company?.id ?? 'personal')

const companyOptions = computed(() => {
  const options: { label: string; value: string }[] = []
  if (authStore.companies.length > 0)
    options.push({ label: t('common.personal'), value: 'personal' })
  for (const m of authStore.companies) options.push({ label: m.company.name, value: m.company.id })
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
  <Select
    v-if="showSwitcher"
    :model-value="activeCompanyId"
    :options="companyOptions"
    option-label="label"
    option-value="value"
    class="hidden !text-xs sm:inline-flex"
    :pt="{ root: { class: '!py-1 !px-2 !min-w-0 max-w-48' }, label: { class: '!text-xs !py-0' } }"
    @update:model-value="handleCompanySwitch"
  />
  <span
    v-else-if="authStore.user?.company"
    class="hidden rounded-md bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600 sm:inline"
  >
    {{ authStore.user.company.name }}
  </span>
</template>
