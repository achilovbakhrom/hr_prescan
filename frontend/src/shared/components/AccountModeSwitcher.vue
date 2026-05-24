<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { AccountMode } from '@/shared/types/auth.types'

const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()
const toast = useToast()

const showHrDialog = ref(false)
const showCandidateDialog = ref(false)
const hrForm = ref({
  companyName: '',
  size: 'small',
  country: '',
  industries: [] as string[],
  customIndustry: '',
  website: '',
  description: '',
})
const candidateForm = ref({
  firstName: authStore.user?.firstName ?? '',
  lastName: authStore.user?.lastName ?? '',
  phone: authStore.user?.phone ?? '',
  headline: '',
  location: '',
})

const currentMode = computed(() => authStore.activeMode as AccountMode)
const availableModes = computed(() => authStore.modes?.availableModes ?? [currentMode.value])
const canCreateHr = computed(() => authStore.modes?.canCreateHrSpace ?? false)
const canCreateCandidate = computed(() => authStore.modes?.canCreateCandidateSpace ?? false)
const targetMode = computed<AccountMode>(() => (currentMode.value === 'hr' ? 'candidate' : 'hr'))
const targetAvailable = computed(() => availableModes.value.includes(targetMode.value))
const targetLabelKey = computed(() =>
  targetMode.value === 'hr' ? 'common.accountMode.hr' : 'common.accountMode.candidate',
)
const compactTargetLabelKey = computed(() =>
  targetMode.value === 'hr' ? 'common.accountMode.hr' : 'common.accountMode.candidateShort',
)
const actionLabel = computed(() =>
  targetMode.value === 'hr'
    ? t('common.accountMode.switchToHr')
    : t('common.accountMode.switchToCandidate'),
)
const currentModeLabel = computed(() =>
  currentMode.value === 'hr' ? t('common.accountMode.hr') : t('common.accountMode.candidate'),
)
const actionTitle = computed(() =>
  t('common.accountMode.currentMode', { mode: currentModeLabel.value }),
)

const sizeOptions = [
  { label: 'Small', value: 'small' },
  { label: 'Medium', value: 'medium' },
  { label: 'Large', value: 'large' },
  { label: 'Enterprise', value: 'enterprise' },
]

async function goAfterSwitch(mode: AccountMode): Promise<void> {
  await router.push({ name: mode === 'hr' ? ROUTE_NAMES.DASHBOARD : ROUTE_NAMES.MY_APPLICATIONS })
}

async function switchMode(): Promise<void> {
  if (!authStore.modes) await authStore.fetchModes()

  const nextMode = targetMode.value
  if (targetAvailable.value) {
    await authStore.switchMode(nextMode)
    await goAfterSwitch(nextMode)
    return
  }
  if (nextMode === 'hr' && canCreateHr.value) {
    showHrDialog.value = true
  } else if (nextMode === 'candidate' && canCreateCandidate.value) {
    showCandidateDialog.value = true
  } else {
    toast.add({
      severity: 'warn',
      summary: t('common.accountMode.unavailable'),
      life: 3500,
    })
  }
}

async function createHrSpace(): Promise<void> {
  await authStore.createHrSpace(hrForm.value)
  showHrDialog.value = false
  await goAfterSwitch('hr')
}

async function createCandidateSpace(): Promise<void> {
  await authStore.createCandidateSpace(candidateForm.value)
  showCandidateDialog.value = false
  await goAfterSwitch('candidate')
}
</script>

<template>
  <div class="flex min-w-0">
    <button
      type="button"
      class="inline-flex h-9 min-w-0 max-w-full items-center justify-center gap-1.5 rounded-xl border border-[color:var(--color-border-glass)] bg-white/78 px-2.5 text-xs font-semibold text-[color:var(--color-text-primary)] shadow-sm transition-colors hover:border-[color:color-mix(in_srgb,var(--color-accent)_35%,var(--color-border-glass))] hover:bg-white disabled:cursor-wait disabled:opacity-70 dark:bg-gray-900/70 dark:hover:bg-gray-900 sm:gap-2 sm:px-3"
      :title="actionTitle"
      :aria-label="actionLabel"
      :disabled="authStore.loading"
      @click="switchMode"
    >
      <i
        :class="targetMode === 'hr' ? 'pi pi-briefcase' : 'pi pi-user'"
        class="shrink-0 text-[12px] text-[color:var(--color-accent)]"
      ></i>
      <span class="hidden truncate sm:inline">{{ actionLabel }}</span>
      <span class="truncate sm:hidden">{{ t(compactTargetLabelKey) }}</span>
      <i
        v-if="authStore.loading"
        class="pi pi-spinner pi-spin shrink-0 text-[10px] text-[color:var(--color-text-muted)]"
      ></i>
    </button>

    <Dialog
      v-model:visible="showHrDialog"
      modal
      :header="t('common.accountMode.createHrSpace')"
      :style="{ width: 'min(92vw, 460px)' }"
    >
      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('auth.companySetup.companyName') }}
          <InputText v-model="hrForm.companyName" class="mt-1 w-full" />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('auth.companySetup.size') }}
          <Select
            v-model="hrForm.size"
            :options="sizeOptions"
            option-label="label"
            option-value="value"
            class="mt-1 w-full"
          />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('auth.companySetup.country') }}
          <InputText v-model="hrForm.country" class="mt-1 w-full" />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('settings.company.website') }}
          <InputText v-model="hrForm.website" class="mt-1 w-full" />
        </label>
      </div>
      <template #footer>
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          text
          @click="showHrDialog = false"
        />
        <Button
          :label="t('common.create')"
          icon="pi pi-check"
          :loading="authStore.loading"
          :disabled="!hrForm.companyName.trim() || !hrForm.country.trim()"
          @click="createHrSpace"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="showCandidateDialog"
      modal
      :header="t('common.accountMode.createCandidateSpace')"
      :style="{ width: 'min(92vw, 460px)' }"
    >
      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('settings.profile.firstName') }}
          <InputText v-model="candidateForm.firstName" class="mt-1 w-full" />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('settings.profile.lastName') }}
          <InputText v-model="candidateForm.lastName" class="mt-1 w-full" />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('settings.profile.phone') }}
          <InputText v-model="candidateForm.phone" class="mt-1 w-full" />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('cvBuilder.personal.headline') }}
          <InputText v-model="candidateForm.headline" class="mt-1 w-full" />
        </label>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
          {{ t('cvBuilder.personal.location') }}
          <InputText v-model="candidateForm.location" class="mt-1 w-full" />
        </label>
      </div>
      <template #footer>
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          text
          @click="showCandidateDialog = false"
        />
        <Button
          :label="`${t('common.create')} ${t(targetLabelKey)}`"
          icon="pi pi-check"
          :loading="authStore.loading"
          :disabled="!candidateForm.firstName.trim() || !candidateForm.lastName.trim()"
          @click="createCandidateSpace"
        />
      </template>
    </Dialog>
  </div>
</template>
