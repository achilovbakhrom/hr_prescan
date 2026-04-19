<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import { useCompanyStore } from '@/features/companies/stores/company.store'
import { ALL_HR_PERMISSIONS, type HRPermission } from '@/shared/types/auth.types'

const props = defineProps<{
  visible: boolean
  loading: boolean
}>()

const emit = defineEmits<{
  hide: []
  invite: [payload: { email: string; permissions: HRPermission[]; companyIds: string[] }]
}>()

const { t } = useI18n()
const companyStore = useCompanyStore()

const email = ref('')
const selectedPermissions = ref<HRPermission[]>([...ALL_HR_PERMISSIONS])
const selectedCompanyIds = ref<string[]>([])
const submitted = ref(false)
const emailInvalid = ref(false)
const companyInvalid = ref(false)

const liveCompanies = computed(() =>
  companyStore.companies.filter((c) => !c.isDeleted).map((m) => ({ id: m.id, name: m.name })),
)

const permissionOptions: { value: HRPermission; labelKey: string; descKey: string }[] = [
  { value: 'manage_vacancies', labelKey: 'permissions.manageVacancies', descKey: 'permissions.manageVacanciesDesc' },
  { value: 'manage_candidates', labelKey: 'permissions.manageCandidates', descKey: 'permissions.manageCandidatesDesc' },
  { value: 'manage_interviews', labelKey: 'permissions.manageInterviews', descKey: 'permissions.manageInterviewsDesc' },
  { value: 'manage_team', labelKey: 'permissions.manageTeam', descKey: 'permissions.manageTeamDesc' },
  { value: 'view_analytics', labelKey: 'permissions.viewAnalytics', descKey: 'permissions.viewAnalyticsDesc' },
  { value: 'manage_settings', labelKey: 'permissions.manageSettings', descKey: 'permissions.manageSettingsDesc' },
]

watch(
  () => props.visible,
  async (val) => {
    if (!val) return
    email.value = ''
    selectedPermissions.value = [...ALL_HR_PERMISSIONS]
    submitted.value = false
    emailInvalid.value = false
    companyInvalid.value = false
    if (!companyStore.companies.length) await companyStore.fetchCompanies()
    selectedCompanyIds.value = liveCompanies.value.map((c) => c.id)
  },
)

function validate(): boolean {
  emailInvalid.value = !email.value || !email.value.includes('@')
  companyInvalid.value = selectedCompanyIds.value.length === 0
  return !emailInvalid.value && !companyInvalid.value
}

function handleSubmit(): void {
  submitted.value = true
  if (!validate()) return
  const allSelected = selectedCompanyIds.value.length === liveCompanies.value.length
  emit('invite', {
    email: email.value,
    permissions: selectedPermissions.value,
    companyIds: allSelected ? [] : selectedCompanyIds.value,
  })
}
</script>

<template>
  <Dialog
    :visible="visible"
    :header="t('settings.team.invite')"
    :modal="true"
    :style="{ width: '520px' }"
    @update:visible="!$event && emit('hide')"
  >
    <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
      <div class="flex flex-col gap-1">
        <label for="inviteEmail" class="text-sm font-medium text-gray-700">
          {{ t('settings.team.email') }}
        </label>
        <InputText
          id="inviteEmail"
          v-model="email"
          type="email"
          placeholder="Enter email address"
          :invalid="submitted && emailInvalid"
          class="w-full"
        />
        <small v-if="submitted && emailInvalid" class="text-red-500">
          Please enter a valid email address.
        </small>
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-gray-700">
          {{ t('settings.team.companies') }}
        </label>
        <p class="text-xs text-gray-500">{{ t('settings.team.companiesHelp') }}</p>
        <div class="flex flex-col gap-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-3 max-h-48 overflow-auto">
          <label
            v-for="c in liveCompanies"
            :key="c.id"
            class="flex cursor-pointer items-center gap-3 rounded-md px-2 py-1.5 transition-colors hover:bg-white"
          >
            <Checkbox v-model="selectedCompanyIds" :value="c.id" />
            <span class="text-sm text-gray-800">{{ c.name }}</span>
          </label>
          <p v-if="!liveCompanies.length" class="px-2 py-1 text-xs text-gray-500">
            {{ t('settings.team.noCompanies') }}
          </p>
        </div>
        <small v-if="submitted && companyInvalid" class="text-red-500">
          {{ t('settings.team.selectAtLeastOneCompany') }}
        </small>
      </div>

      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-gray-700">
          {{ t('permissions.title') }}
        </label>
        <p class="text-xs text-gray-500">{{ t('permissions.selectPermissions') }}</p>
        <div class="flex flex-col gap-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-3">
          <label
            v-for="opt in permissionOptions"
            :key="opt.value"
            class="flex cursor-pointer items-start gap-3 rounded-md px-2 py-1.5 transition-colors hover:bg-white"
          >
            <Checkbox v-model="selectedPermissions" :value="opt.value" class="mt-0.5" />
            <div class="min-w-0">
              <span class="text-sm font-medium text-gray-800">{{ t(opt.labelKey) }}</span>
              <p class="text-xs text-gray-500">{{ t(opt.descKey) }}</p>
            </div>
          </label>
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <Button
          type="button"
          :label="t('common.cancel')"
          severity="secondary"
          @click="emit('hide')"
        />
        <Button type="submit" :label="t('settings.team.send')" :loading="loading" />
      </div>
    </form>
  </Dialog>
</template>
