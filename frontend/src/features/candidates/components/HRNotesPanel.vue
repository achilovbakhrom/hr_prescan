<script setup lang="ts">
import { ref, watch } from 'vue'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'

const props = defineProps<{
  notes: string
  loading: boolean
}>()

const emit = defineEmits<{
  save: [note: string]
}>()

const localNotes = ref(props.notes)

watch(
  () => props.notes,
  (val) => {
    localNotes.value = val
  },
)

function handleSave(): void {
  emit('save', localNotes.value)
}
</script>

<template>
  <div class="space-y-3">
    <h3 class="text-sm font-semibold text-gray-600">HR Notes</h3>
    <Textarea
      v-model="localNotes"
      rows="6"
      class="w-full"
      placeholder="Add notes about this candidate..."
      :disabled="props.loading"
    />
    <div class="flex justify-end">
      <Button
        label="Save Notes"
        icon="pi pi-save"
        size="small"
        :loading="props.loading"
        @click="handleSave"
      />
    </div>
  </div>
</template>
