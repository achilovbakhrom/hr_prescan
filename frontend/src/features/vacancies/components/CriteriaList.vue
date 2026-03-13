<script setup lang="ts">
import { ref } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import type { VacancyCriteria } from '../types/vacancy.types'

defineProps<{ criteria: VacancyCriteria[]; loading?: boolean }>()
const emit = defineEmits<{
  add: [data: { name: string; description?: string; weight?: number }]
  update: [criteriaId: string, data: Partial<VacancyCriteria>]
  delete: [criteriaId: string]
}>()

const showDialog = ref(false)
const isEditing = ref(false)
const editId = ref('')
const formName = ref('')
const formDescription = ref('')
const formWeight = ref<number>(1)

function openAdd(): void {
  isEditing.value = false; editId.value = ''
  formName.value = ''; formDescription.value = ''; formWeight.value = 1
  showDialog.value = true
}

function openEdit(c: VacancyCriteria): void {
  isEditing.value = true; editId.value = c.id
  formName.value = c.name; formDescription.value = c.description; formWeight.value = c.weight
  showDialog.value = true
}

function handleSubmit(): void {
  if (!formName.value.trim()) return
  const data = { name: formName.value.trim(), description: formDescription.value.trim(), weight: formWeight.value }
  if (isEditing.value) { emit('update', editId.value, data) }
  else { emit('add', { ...data, description: data.description || undefined }) }
  showDialog.value = false
}
</script>

<template>
  <div>
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold">Evaluation Criteria</h3>
      <Button label="Add Criteria" icon="pi pi-plus" size="small" @click="openAdd" />
    </div>
    <DataTable :value="criteria" :loading="loading" striped-rows>
      <Column field="order" header="#" style="width: 50px" />
      <Column field="name" header="Name" />
      <Column field="description" header="Description" />
      <Column field="weight" header="Weight" style="width: 100px" />
      <Column header="Default" style="width: 100px">
        <template #body="{ data }">
          <Tag v-if="data.isDefault" value="Default" severity="info" />
        </template>
      </Column>
      <Column header="Actions" style="width: 120px">
        <template #body="{ data }">
          <div class="flex gap-1">
            <Button icon="pi pi-pencil" severity="secondary" text size="small" @click="openEdit(data)" />
            <Button icon="pi pi-trash" severity="danger" text size="small" :disabled="data.isDefault" @click="emit('delete', data.id)" />
          </div>
        </template>
      </Column>
      <template #empty>
        <div class="py-8 text-center text-gray-500">No criteria defined yet. Add evaluation criteria for this vacancy.</div>
      </template>
    </DataTable>
    <Dialog v-model:visible="showDialog" :header="isEditing ? 'Edit Criteria' : 'Add Criteria'" :style="{ width: '500px' }" modal>
      <div class="space-y-4">
        <div><label class="mb-1 block text-sm font-medium">Name *</label>
          <InputText v-model="formName" class="w-full" placeholder="e.g. Communication Skills" /></div>
        <div><label class="mb-1 block text-sm font-medium">Description</label>
          <InputText v-model="formDescription" class="w-full" placeholder="Brief description" /></div>
        <div><label class="mb-1 block text-sm font-medium">Weight</label>
          <InputNumber v-model="formWeight" class="w-full" :min="1" :max="10" /></div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" text @click="showDialog = false" />
        <Button :label="isEditing ? 'Save' : 'Add'" :disabled="!formName.trim()" @click="handleSubmit" />
      </template>
    </Dialog>
  </div>
</template>
