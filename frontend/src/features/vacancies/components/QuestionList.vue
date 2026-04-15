<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import Select from 'primevue/select'
import { getLocale } from '@/shared/i18n'
import type { InterviewQuestion } from '../types/vacancy.types'

const props = defineProps<{ questions: InterviewQuestion[]; loading?: boolean }>()

const emit = defineEmits<{
  add: [data: { text: string; category?: string }]
  update: [questionId: string, data: Partial<InterviewQuestion>]
  delete: [questionId: string]
  generate: []
  translateAll: []
}>()

const { t } = useI18n()

const currentLocale = computed(() => getLocale())

const showTranslateAll = computed(() => {
  if (!props.questions.length) return false
  return props.questions.some((q) => !q.translations?.[currentLocale.value])
})

function getTranslatedText(q: InterviewQuestion): string {
  return q.translations?.[currentLocale.value] ?? q.text
}

const showDialog = ref(false)
const isEditing = ref(false)
const editId = ref('')
const formText = ref('')
const formCategory = ref('')

const categoryOptions = [
  { label: 'Hard Skill', value: 'Hard Skill' },
  { label: 'Soft Skill', value: 'Soft Skill' },
  { label: 'Domain Knowledge', value: 'Domain Knowledge' },
  { label: 'Cultural Fit', value: 'Cultural Fit' },
]

function openAdd(): void {
  isEditing.value = false
  editId.value = ''
  formText.value = ''
  formCategory.value = ''
  showDialog.value = true
}

function openEdit(q: InterviewQuestion): void {
  isEditing.value = true
  editId.value = q.id
  formText.value = q.text
  formCategory.value = q.category
  showDialog.value = true
}

function handleSubmit(): void {
  if (!formText.value.trim()) return
  if (isEditing.value) {
    emit('update', editId.value, {
      text: formText.value.trim(),
      category: formCategory.value.trim(),
    })
  } else {
    emit('add', { text: formText.value.trim(), category: formCategory.value.trim() || undefined })
  }
  showDialog.value = false
}
</script>

<template>
  <div>
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold">{{ t('vacancies.questions') }}</h3>
      <div class="flex gap-2">
        <Button
          v-if="showTranslateAll"
          :label="t('common.translate')"
          icon="pi pi-language"
          severity="secondary"
          size="small"
          @click="emit('translateAll')"
        />
        <Button
          :label="t('vacancies.generateQuestions')"
          icon="pi pi-sparkles"
          severity="info"
          size="small"
          :loading="loading"
          @click="emit('generate')"
        />
        <Button
          :label="t('vacancies.addQuestion')"
          icon="pi pi-plus"
          size="small"
          @click="openAdd"
        />
      </div>
    </div>
    <DataTable :value="questions" :loading="loading" striped-rows>
      <Column field="order" header="#" style="width: 50px" />
      <Column field="text" :header="t('vacancies.competency')">
        <template #body="{ data }">
          <span class="text-sm">{{ getTranslatedText(data) }}</span>
        </template>
      </Column>
      <Column field="category" header="Category" style="width: 160px">
        <template #body="{ data }">
          <Tag v-if="data.category" :value="data.category" severity="secondary" />
        </template>
      </Column>
      <Column field="source" header="Source" style="width: 120px">
        <template #body="{ data }">
          <Tag
            :value="data.source === 'ai_generated' ? 'AI' : 'Manual'"
            :severity="data.source === 'ai_generated' ? 'info' : 'secondary'"
          />
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
              @click="emit('delete', data.id)"
            />
          </div>
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">
          No competencies yet. Add manually or generate with AI.
        </div>
      </template>
    </DataTable>
    <Dialog
      v-model:visible="showDialog"
      :header="isEditing ? 'Edit Competency' : t('vacancies.addQuestion')"
      :style="{ width: '500px' }"
      modal
    >
      <div class="space-y-4">
        <div>
          <label class="mb-1 block text-sm font-medium">Competency *</label>
          <Textarea
            v-model="formText"
            class="w-full"
            rows="3"
            placeholder="e.g. Candidate should demonstrate proficiency with React hooks"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Category</label>
          <Select
            v-model="formCategory"
            :options="categoryOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            placeholder="Select category"
          />
        </div>
      </div>
      <template #footer>
        <Button :label="t('common.cancel')" severity="secondary" text @click="showDialog = false" />
        <Button
          :label="isEditing ? t('common.save') : 'Add'"
          :disabled="!formText.trim()"
          @click="handleSubmit"
        />
      </template>
    </Dialog>
  </div>
</template>
