<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

defineProps<{
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
  submitted: boolean
  errors: {
    firstName: boolean
    lastName: boolean
    email: boolean
    password: boolean
    confirmPassword: boolean
  }
  loading: boolean
}>()

const emit = defineEmits<{
  'update:firstName': [value: string]
  'update:lastName': [value: string]
  'update:email': [value: string]
  'update:password': [value: string]
  'update:confirmPassword': [value: string]
  back: []
  submit: []
}>()

const { t } = useI18n()
</script>

<template>
  <form class="flex flex-col gap-4 pt-4" @submit.prevent="emit('submit')">
    <div class="grid grid-cols-2 gap-4">
      <div class="flex flex-col gap-1">
        <label for="adminFirstName" class="text-sm font-medium text-gray-700">
          {{ t('auth.companyRegister.adminFirstName') }}
        </label>
        <InputText
          id="adminFirstName"
          :model-value="firstName"
          :placeholder="t('auth.companyRegister.adminFirstNamePlaceholder')"
          :invalid="submitted && errors.firstName"
          class="w-full"
          @update:model-value="emit('update:firstName', $event as string)"
        />
        <small v-if="submitted && errors.firstName" class="text-red-500">
          {{ t('auth.companyRegister.firstNameRequired') }}
        </small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="adminLastName" class="text-sm font-medium text-gray-700">
          {{ t('auth.companyRegister.adminLastName') }}
        </label>
        <InputText
          id="adminLastName"
          :model-value="lastName"
          :placeholder="t('auth.companyRegister.adminLastNamePlaceholder')"
          :invalid="submitted && errors.lastName"
          class="w-full"
          @update:model-value="emit('update:lastName', $event as string)"
        />
        <small v-if="submitted && errors.lastName" class="text-red-500">
          {{ t('auth.companyRegister.lastNameRequired') }}
        </small>
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <label for="adminEmail" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.adminEmail') }}
      </label>
      <InputText
        id="adminEmail"
        :model-value="email"
        type="email"
        :placeholder="t('auth.companyRegister.adminEmailPlaceholder')"
        :invalid="submitted && errors.email"
        class="w-full"
        @update:model-value="emit('update:email', $event as string)"
      />
      <small v-if="submitted && errors.email" class="text-red-500">
        {{ t('auth.companyRegister.invalidEmail') }}
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="adminPassword" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.adminPassword') }}
      </label>
      <Password
        :model-value="password"
        input-id="adminPassword"
        :placeholder="t('auth.companyRegister.adminPasswordPlaceholder')"
        toggle-mask
        :invalid="submitted && errors.password"
        class="w-full"
        input-class="w-full"
        @update:model-value="emit('update:password', $event as string)"
      />
      <small v-if="submitted && errors.password" class="text-red-500">
        {{ t('auth.companyRegister.passwordTooShort') }}
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="adminConfirmPassword" class="text-sm font-medium text-gray-700">
        {{ t('auth.companyRegister.confirmPassword') }}
      </label>
      <Password
        :model-value="confirmPassword"
        input-id="adminConfirmPassword"
        :placeholder="t('auth.companyRegister.confirmPasswordPlaceholder')"
        :feedback="false"
        toggle-mask
        :invalid="submitted && errors.confirmPassword"
        class="w-full"
        input-class="w-full"
        @update:model-value="emit('update:confirmPassword', $event as string)"
      />
      <small v-if="submitted && errors.confirmPassword" class="text-red-500">
        {{ t('auth.companyRegister.passwordMismatch') }}
      </small>
    </div>

    <div class="flex justify-between pt-2">
      <Button
        type="button"
        :label="t('auth.companyRegister.back')"
        severity="secondary"
        icon="pi pi-arrow-left"
        @click="emit('back')"
      />
      <Button type="submit" :label="t('auth.companyRegister.submit')" :loading="loading" />
    </div>
  </form>
</template>
