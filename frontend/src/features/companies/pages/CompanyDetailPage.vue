<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCompanyStore } from '../stores/company.store'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const companyStore = useCompanyStore()
const editing = ref(false)
const saving = ref(false)

const name = ref('')
const customIndustry = ref('')
const website = ref('')
const description = ref('')

function syncFormFromStore(): void {
  const c = companyStore.currentCompany
  if (!c) return
  name.value = c.name
  customIndustry.value = c.customIndustry
  website.value = c.website ?? ''
  description.value = c.description ?? ''
}

onMounted(async () => {
  await companyStore.fetchCompanyDetail(route.params.id as string)
  syncFormFromStore()
})

watch(
  () => companyStore.currentCompany,
  () => {
    if (!editing.value) syncFormFromStore()
  },
)

function startEdit(): void {
  syncFormFromStore()
  editing.value = true
}

function cancelEdit(): void {
  syncFormFromStore()
  editing.value = false
}

async function handleSave(): Promise<void> {
  const id = route.params.id as string
  if (!name.value) return
  saving.value = true
  try {
    await companyStore.updateCompany(id, {
      name: name.value,
      customIndustry: customIndustry.value,
      website: website.value,
      description: description.value,
    })
    editing.value = false
  } catch {
    // error surfaced via store
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <button
      class="mb-4 flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-900"
      @click="router.push({ name: ROUTE_NAMES.COMPANY_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <div v-if="companyStore.loading && !companyStore.currentCompany" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <div
      v-else-if="companyStore.error && !companyStore.currentCompany"
      class="py-12 text-center text-red-600"
    >
      <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
      <p>{{ companyStore.error }}</p>
    </div>

    <template v-else-if="companyStore.currentCompany">
      <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <div
            v-if="companyStore.currentCompany.logo"
            class="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-gray-100"
          >
            <img
              :src="companyStore.currentCompany.logo"
              :alt="companyStore.currentCompany.name"
              class="h-full w-full object-contain"
            />
          </div>
          <div
            v-else
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600"
          >
            <i class="pi pi-building text-xl"></i>
          </div>
          <h1 v-if="!editing" class="text-2xl font-bold text-gray-900">
            {{ companyStore.currentCompany.name }}
          </h1>
        </div>
        <Button
          v-if="!editing"
          :label="t('common.edit')"
          icon="pi pi-pencil"
          severity="secondary"
          @click="startEdit"
        />
      </div>

      <div
        v-if="companyStore.error"
        class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600"
      >
        {{ companyStore.error }}
      </div>

      <div v-if="!editing" class="space-y-4 rounded-xl border border-gray-200 bg-white p-6">
        <div v-if="companyStore.currentCompany.customIndustry">
          <p class="text-sm text-gray-500">{{ t('companies.industry') }}</p>
          <p class="font-medium">{{ companyStore.currentCompany.customIndustry }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">{{ t('companies.country') }}</p>
          <p class="font-medium">{{ companyStore.currentCompany.country }}</p>
        </div>
        <div v-if="companyStore.currentCompany.website">
          <p class="text-sm text-gray-500">{{ t('companies.website') }}</p>
          <a
            :href="companyStore.currentCompany.website"
            target="_blank"
            rel="noopener noreferrer"
            class="font-medium text-blue-600 hover:underline"
          >
            {{ companyStore.currentCompany.website }}
          </a>
        </div>
        <div v-if="companyStore.currentCompany.description">
          <p class="text-sm text-gray-500">{{ t('companies.description') }}</p>
          <p class="whitespace-pre-line text-gray-700">{{ companyStore.currentCompany.description }}</p>
        </div>
      </div>

      <form
        v-else
        class="space-y-4 rounded-xl border border-gray-200 bg-white p-6"
        @submit.prevent="handleSave"
      >
        <div>
          <label class="mb-1 block text-sm font-medium"
            >{{ t('companies.name') }} <span class="text-red-500">*</span></label
          >
          <InputText v-model="name" class="w-full" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('companies.industry') }}</label>
          <InputText v-model="customIndustry" class="w-full" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('companies.website') }}</label>
          <InputText v-model="website" class="w-full" placeholder="https://..." />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('companies.description') }}</label>
          <Textarea v-model="description" class="w-full" rows="6" />
        </div>
        <div class="flex justify-end gap-2">
          <Button
            :label="t('common.cancel')"
            severity="secondary"
            type="button"
            @click="cancelEdit"
          />
          <Button
            :label="t('common.save')"
            icon="pi pi-check"
            type="submit"
            :loading="saving"
            :disabled="!name"
          />
        </div>
      </form>
    </template>
  </div>
</template>
