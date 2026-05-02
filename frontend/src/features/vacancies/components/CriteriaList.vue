<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import { getLocale } from '@/shared/i18n'
import type { VacancyCriteria } from '../types/vacancy.types'

const props = defineProps<{ criteria: VacancyCriteria[]; loading?: boolean }>()

const emit = defineEmits<{
  add: [data: { name: string; description?: string; weight?: number }]
  update: [criteriaId: string, data: Partial<VacancyCriteria>]
  delete: [criteriaId: string]
  translateAll: []
}>()

const { t } = useI18n()

const currentLocale = computed(() => getLocale())

const showTranslateAll = computed(() => {
  if (!props.criteria.length) return false
  return props.criteria.some((c) => !c.translations?.[currentLocale.value])
})

function getTranslatedName(c: VacancyCriteria): string {
  return c.translations?.[currentLocale.value]?.split(': ')?.[0] ?? c.name
}

function getTranslatedDescription(c: VacancyCriteria): string {
  const translated = c.translations?.[currentLocale.value]
  if (!translated) return c.description
  const parts = translated.split(': ')
  return parts.length > 1 ? parts.slice(1).join(': ') : c.description
}

const showDialog = ref(false)
const isEditing = ref(false)
const editId = ref('')
const formName = ref('')
const formDescription = ref('')
const formWeight = ref<number>(1)

function openAdd(): void {
  isEditing.value = false
  editId.value = ''
  formName.value = ''
  formDescription.value = ''
  formWeight.value = 1
  showDialog.value = true
}

function openEdit(c: VacancyCriteria): void {
  isEditing.value = true
  editId.value = c.id
  formName.value = c.name
  formDescription.value = c.description
  formWeight.value = c.weight
  showDialog.value = true
}

function handleSubmit(): void {
  if (!formName.value.trim()) return
  const data = {
    name: formName.value.trim(),
    description: formDescription.value.trim(),
    weight: formWeight.value,
  }
  if (isEditing.value) {
    emit('update', editId.value, data)
  } else {
    emit('add', { ...data, description: data.description || undefined })
  }
  showDialog.value = false
}
</script>

<template>
  <div>
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold">{{ t('vacancies.criteria') }}</h3>
      <div class="flex gap-2">
        <Button
          v-if="showTranslateAll"
          :label="t('common.translate')"
          icon="pi pi-language"
          severity="secondary"
          size="small"
          :loading="loading"
          :disabled="loading"
          @click="emit('translateAll')"
        />
        <Button
          :label="t('vacancies.addCriteria')"
          icon="pi pi-plus"
          size="small"
          @click="openAdd"
        />
      </div>
    </div>
    <DataTable :value="criteria" :loading="loading" striped-rows>
      <Column field="order" header="#" style="width: 50px" />
      <Column field="name" :header="t('common.name')">
        <template #body="{ data }">{{ getTranslatedName(data) }}</template>
      </Column>
      <Column field="description" :header="t('common.description')">
        <template #body="{ data }">{{ getTranslatedDescription(data) }}</template>
      </Column>
      <Column field="weight" :header="t('vacancies.weight')" style="width: 100px" />
      <Column :header="t('vacancies.default')" style="width: 100px">
        <template #body="{ data }">
          <Tag v-if="data.isDefault" :value="t('vacancies.default')" severity="info" />
        </template>
      </Column>
      <Column :header="t('common.actions')" style="width: 120px">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button
              icon="pi pi-pencil"
              severity="secondary"
              text
              size="small"
              @click="openEdit(data)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              size="small"
              :disabled="data.isDefault"
              @click="emit('delete', data.id)"
            />
          </div>
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          {{ t('vacancies.noCriteria') }}
        </div>
      </template>
    </DataTable>
    <Dialog
      v-model:visible="showDialog"
      :header="isEditing ? t('vacancies.editCriteria') : t('vacancies.addCriteria')"
      :style="{ width: '500px' }"
      modal
    >
      <div class="space-y-4">
        <div>
          <label class="mb-1 block text-sm font-medium"
            >{{ t('vacancies.criteriaForm.name') }} *</label
          >
          <InputText
            v-model="formName"
            class="w-full"
            :placeholder="t('vacancies.criteriaForm.namePlaceholder')"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('common.description') }}</label>
          <InputText
            v-model="formDescription"
            class="w-full"
            :placeholder="t('vacancies.criteriaForm.descriptionPlaceholder')"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('vacancies.weight') }}</label>
          <InputNumber v-model="formWeight" class="w-full" :min="1" :max="10" />
        </div>
      </div>
      <template #footer>
        <Button :label="t('common.cancel')" severity="secondary" text @click="showDialog = false" />
        <Button
          :label="isEditing ? t('common.save') : t('common.add')"
          :disabled="!formName.trim()"
          @click="handleSubmit"
        />
      </template>
    </Dialog>
  </div>
</template>
