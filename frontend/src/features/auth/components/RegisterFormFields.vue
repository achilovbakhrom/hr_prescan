<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

const { t } = useI18n()

defineProps<{
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
  submitted: boolean
  errors: Record<string, boolean>
  loading: boolean
}>()

const emit = defineEmits<{
  'update:firstName': [v: string]
  'update:lastName': [v: string]
  'update:email': [v: string]
  'update:password': [v: string]
  'update:confirmPassword': [v: string]
  submit: []
}>()
</script>

<template>
  <form class="flex flex-col gap-4" @submit.prevent="emit('submit')">
    <div class="grid grid-cols-2 gap-4">
      <div class="flex flex-col gap-1">
        <label for="firstName" class="text-sm font-medium text-gray-700">{{ t('auth.register.firstName') }}</label>
        <InputText id="firstName" :model-value="firstName" placeholder="First name" :invalid="submitted && errors.firstName" class="w-full" @update:model-value="emit('update:firstName', $event as string)" />
        <small v-if="submitted && errors.firstName" class="text-red-500">First name is required.</small>
      </div>
      <div class="flex flex-col gap-1">
        <label for="lastName" class="text-sm font-medium text-gray-700">{{ t('auth.register.lastName') }}</label>
        <InputText id="lastName" :model-value="lastName" placeholder="Last name" :invalid="submitted && errors.lastName" class="w-full" @update:model-value="emit('update:lastName', $event as string)" />
        <small v-if="submitted && errors.lastName" class="text-red-500">Last name is required.</small>
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <label for="email" class="text-sm font-medium text-gray-700">{{ t('auth.register.email') }}</label>
      <InputText id="email" :model-value="email" type="email" placeholder="Enter your email" :invalid="submitted && errors.email" class="w-full" @update:model-value="emit('update:email', $event as string)" />
      <small v-if="submitted && errors.email" class="text-red-500">Please enter a valid email address.</small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="password" class="text-sm font-medium text-gray-700">{{ t('auth.register.password') }}</label>
      <Password :model-value="password" input-id="password" placeholder="Minimum 8 characters" toggle-mask :invalid="submitted && errors.password" class="w-full" input-class="w-full" @update:model-value="emit('update:password', $event)" />
      <small v-if="submitted && errors.password" class="text-red-500">{{ t('auth.register.passwordTooShort') }}</small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="confirmPassword" class="text-sm font-medium text-gray-700">{{ t('auth.register.confirmPassword') }}</label>
      <Password :model-value="confirmPassword" input-id="confirmPassword" placeholder="Confirm your password" :feedback="false" toggle-mask :invalid="submitted && errors.confirmPassword" class="w-full" input-class="w-full" @update:model-value="emit('update:confirmPassword', $event)" />
      <small v-if="submitted && errors.confirmPassword" class="text-red-500">{{ t('auth.register.passwordMismatch') }}</small>
    </div>

    <Button type="submit" :label="t('auth.register.submit')" :loading="loading" class="mt-2 w-full" />
  </form>
</template>
