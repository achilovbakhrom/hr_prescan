<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import { candidateService } from '../services/candidate.service'

const props = defineProps<{
  visible: boolean
  candidateId: string
  candidateEmail: string
}>()

const emit = defineEmits<{
  close: []
}>()

const { t } = useI18n()

const subject = ref('')
const body = ref('')
const sending = ref(false)
const sent = ref(false)

watch(
  () => props.visible,
  (val) => {
    if (val) {
      subject.value = ''
      body.value = ''
      sent.value = false
    }
  },
)

async function handleSend(): Promise<void> {
  if (!subject.value.trim() || !body.value.trim()) return

  sending.value = true
  try {
    await candidateService.sendEmail(props.candidateId, {
      subject: subject.value,
      body: body.value,
    })
    sent.value = true
    setTimeout(() => emit('close'), 1500)
  } catch {
    // Silently fail
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <Dialog
    :visible="props.visible"
    :header="t('candidates.actions.sendEmail')"
    :modal="true"
    :closable="true"
    :style="{ width: '500px' }"
    @update:visible="emit('close')"
  >
    <div v-if="sent" class="py-4 text-center">
      <i class="pi pi-check-circle mb-2 text-3xl text-green-500"></i>
      <p class="text-sm text-gray-700">Email sent successfully</p>
    </div>

    <div v-else class="space-y-4">
      <p class="text-sm text-gray-500">To: {{ props.candidateEmail }}</p>

      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700"> Subject </label>
        <InputText v-model="subject" class="w-full" placeholder="Email subject" />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700"> Body </label>
        <Textarea v-model="body" class="w-full" rows="6" placeholder="Email body" />
      </div>
    </div>

    <template #footer>
      <div v-if="!sent" class="flex justify-end gap-2">
        <Button :label="t('common.cancel')" severity="secondary" text @click="emit('close')" />
        <Button
          :label="t('interviews.chat.send')"
          icon="pi pi-send"
          :loading="sending"
          :disabled="!subject.trim() || !body.trim()"
          @click="handleSend"
        />
      </div>
    </template>
  </Dialog>
</template>
