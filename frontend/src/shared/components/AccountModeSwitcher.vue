<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { AccountMode } from '@/shared/types/auth.types'

const authStore = useAuthStore()
const router = useRouter()

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
const label = computed(() => (currentMode.value === 'hr' ? 'HR' : 'Candidate'))
const targetLabel = computed(() => (targetMode.value === 'hr' ? 'HR' : 'Candidate'))

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
  if (targetAvailable.value) {
    await authStore.switchMode(targetMode.value)
    await goAfterSwitch(targetMode.value)
    return
  }
  if (targetMode.value === 'hr' && canCreateHr.value) {
    showHrDialog.value = true
  } else if (targetMode.value === 'candidate' && canCreateCandidate.value) {
    showCandidateDialog.value = true
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
  <Button
    severity="secondary"
    outlined
    size="small"
    :icon="currentMode === 'hr' ? 'pi pi-briefcase' : 'pi pi-user'"
    :label="label"
    class="!hidden sm:!inline-flex"
    @click="switchMode"
  />
  <Button
    severity="secondary"
    outlined
    size="small"
    :icon="currentMode === 'hr' ? 'pi pi-briefcase' : 'pi pi-user'"
    class="sm:!hidden"
    :aria-label="label"
    @click="switchMode"
  />

  <Dialog
    v-model:visible="showHrDialog"
    modal
    header="Create HR Space"
    :style="{ width: 'min(92vw, 460px)' }"
  >
    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Company name
        <InputText v-model="hrForm.companyName" class="mt-1 w-full" />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Company size
        <Select
          v-model="hrForm.size"
          :options="sizeOptions"
          option-label="label"
          option-value="value"
          class="mt-1 w-full"
        />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Country
        <InputText v-model="hrForm.country" class="mt-1 w-full" />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Website
        <InputText v-model="hrForm.website" class="mt-1 w-full" />
      </label>
    </div>
    <template #footer>
      <Button label="Cancel" severity="secondary" text @click="showHrDialog = false" />
      <Button
        label="Create"
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
    header="Create Candidate Space"
    :style="{ width: 'min(92vw, 460px)' }"
  >
    <div class="space-y-3">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        First name
        <InputText v-model="candidateForm.firstName" class="mt-1 w-full" />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Last name
        <InputText v-model="candidateForm.lastName" class="mt-1 w-full" />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Phone
        <InputText v-model="candidateForm.phone" class="mt-1 w-full" />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Headline
        <InputText v-model="candidateForm.headline" class="mt-1 w-full" />
      </label>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">
        Location
        <InputText v-model="candidateForm.location" class="mt-1 w-full" />
      </label>
    </div>
    <template #footer>
      <Button label="Cancel" severity="secondary" text @click="showCandidateDialog = false" />
      <Button
        :label="`Create ${targetLabel}`"
        icon="pi pi-check"
        :loading="authStore.loading"
        :disabled="!candidateForm.firstName.trim() || !candidateForm.lastName.trim()"
        @click="createCandidateSpace"
      />
    </template>
  </Dialog>
</template>
