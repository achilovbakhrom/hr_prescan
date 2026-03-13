<script setup lang="ts">
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const props = defineProps<{
  visible: boolean
  loading: boolean
}>()

const emit = defineEmits<{
  hide: []
  invite: [email: string]
}>()

const email = ref('')
const submitted = ref(false)
const emailInvalid = ref(false)

watch(
  () => props.visible,
  (val) => {
    if (val) {
      email.value = ''
      submitted.value = false
      emailInvalid.value = false
    }
  },
)

function validate(): boolean {
  emailInvalid.value = !email.value || !email.value.includes('@')
  return !emailInvalid.value
}

function handleSubmit(): void {
  submitted.value = true
  if (!validate()) return
  emit('invite', email.value)
}
</script>

<template>
  <Dialog
    :visible="visible"
    header="Invite HR Member"
    :modal="true"
    :style="{ width: '450px' }"
    @update:visible="!$event && emit('hide')"
  >
    <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
      <div class="flex flex-col gap-1">
        <label for="inviteEmail" class="text-sm font-medium text-gray-700">
          Email Address
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

      <div class="flex justify-end gap-2">
        <Button
          type="button"
          label="Cancel"
          severity="secondary"
          @click="emit('hide')"
        />
        <Button
          type="submit"
          label="Send Invitation"
          :loading="loading"
        />
      </div>
    </form>
  </Dialog>
</template>
