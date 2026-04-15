<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useEmployerStore } from '../stores/employer.store'
import TranslatableText from '@/shared/components/TranslatableText.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const employerStore = useEmployerStore()
const editing = ref(false)
const saving = ref(false)

const name = ref('')
const industry = ref('')
const website = ref('')
const description = ref('')

function syncFormFromStore(): void {
  const e = employerStore.currentEmployer
  if (!e) return
  name.value = e.name
  industry.value = e.industry
  website.value = e.website
  description.value = e.description
}

onMounted(async () => {
  await employerStore.fetchEmployerDetail(route.params.id as string)
  syncFormFromStore()
})

watch(
  () => employerStore.currentEmployer,
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
    await employerStore.updateEmployer(id, {
      name: name.value,
      industry: industry.value,
      website: website.value,
      description: description.value,
    })
    editing.value = false
  } catch {
    // error is displayed via store
  } finally {
    saving.value = false
  }
}

function sourceLabel(source: string): string {
  if (source === 'manual') return t('employers.manual')
  if (source === 'file') return t('employers.file')
  return t('employers.fromWebsite')
}
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <!-- Back -->
    <button
      class="mb-4 flex items-center gap-1.5 text-sm text-gray-500 transition-colors hover:text-gray-900"
      @click="router.push({ name: ROUTE_NAMES.EMPLOYER_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <!-- Loading -->
    <div v-if="employerStore.loading && !employerStore.currentEmployer" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-gray-400"></i>
    </div>

    <!-- Error -->
    <div
      v-else-if="employerStore.error && !employerStore.currentEmployer"
      class="py-12 text-center text-red-600"
    >
      <i class="pi pi-exclamation-circle mb-3 text-4xl"></i>
      <p>{{ employerStore.error }}</p>
    </div>

    <!-- Detail -->
    <template v-else-if="employerStore.currentEmployer">
      <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <div
            v-if="employerStore.currentEmployer.logo"
            class="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-gray-100"
          >
            <img
              :src="employerStore.currentEmployer.logo"
              :alt="employerStore.currentEmployer.name"
              class="h-full w-full object-contain"
            />
          </div>
          <div
            v-else
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600"
          >
            <i class="pi pi-building text-xl"></i>
          </div>
          <div>
            <h1 v-if="!editing" class="text-2xl font-bold text-gray-900">
              {{ employerStore.currentEmployer.name }}
            </h1>
            <Tag :value="sourceLabel(employerStore.currentEmployer.source)" severity="info" />
          </div>
        </div>
        <Button
          v-if="!editing"
          :label="t('common.edit')"
          icon="pi pi-pencil"
          severity="secondary"
          @click="startEdit"
        />
      </div>

      <!-- Error banner -->
      <div
        v-if="employerStore.error"
        class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600"
      >
        {{ employerStore.error }}
      </div>

      <!-- View mode -->
      <div v-if="!editing" class="space-y-4 rounded-xl border border-gray-200 bg-white p-6">
        <div v-if="employerStore.currentEmployer.industry">
          <p class="text-sm text-gray-500">{{ t('employers.industry') }}</p>
          <p class="font-medium">{{ employerStore.currentEmployer.industry }}</p>
        </div>
        <div v-if="employerStore.currentEmployer.website">
          <p class="text-sm text-gray-500">{{ t('employers.website') }}</p>
          <a
            :href="employerStore.currentEmployer.website"
            target="_blank"
            rel="noopener noreferrer"
            class="font-medium text-blue-600 hover:underline"
          >
            {{ employerStore.currentEmployer.website }}
          </a>
        </div>
        <div v-if="employerStore.currentEmployer.description">
          <p class="text-sm text-gray-500">{{ t('employers.description') }}</p>
          <TranslatableText
            :text="employerStore.currentEmployer.description"
            :translations="employerStore.currentEmployer.descriptionTranslations || {}"
            model="employer"
            :object-id="employerStore.currentEmployer.id"
            field="description"
            @translated="
              (tr) => {
                if (employerStore.currentEmployer)
                  employerStore.currentEmployer.descriptionTranslations = tr
              }
            "
          >
            <template #default="{ text }">
              <p class="whitespace-pre-line text-gray-700">{{ text }}</p>
            </template>
          </TranslatableText>
        </div>
      </div>

      <!-- Edit mode -->
      <form
        v-else
        class="space-y-4 rounded-xl border border-gray-200 bg-white p-6"
        @submit.prevent="handleSave"
      >
        <div>
          <label class="mb-1 block text-sm font-medium"
            >{{ t('employers.name') }} <span class="text-red-500">*</span></label
          >
          <InputText v-model="name" class="w-full" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.industry') }}</label>
          <InputText v-model="industry" class="w-full" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.website') }}</label>
          <InputText v-model="website" class="w-full" placeholder="https://..." />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.description') }}</label>
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
