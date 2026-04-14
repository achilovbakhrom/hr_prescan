<script setup lang="ts">
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
</script>

<template>
  <form class="flex flex-col gap-4 pt-4" @submit.prevent="emit('submit')">
    <div class="grid grid-cols-2 gap-4">
      <div class="flex flex-col gap-1">
        <label for="adminFirstName" class="text-sm font-medium text-gray-700"> First Name </label>
        <InputText
          id="adminFirstName"
          :model-value="firstName"
          placeholder="First name"
          :invalid="submitted && errors.firstName"
          class="w-full"
          @update:model-value="emit('update:firstName', $event as string)"
        />
        <small v-if="submitted && errors.firstName" class="text-red-500">
          First name is required.
        </small>
      </div>

      <div class="flex flex-col gap-1">
        <label for="adminLastName" class="text-sm font-medium text-gray-700"> Last Name </label>
        <InputText
          id="adminLastName"
          :model-value="lastName"
          placeholder="Last name"
          :invalid="submitted && errors.lastName"
          class="w-full"
          @update:model-value="emit('update:lastName', $event as string)"
        />
        <small v-if="submitted && errors.lastName" class="text-red-500">
          Last name is required.
        </small>
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <label for="adminEmail" class="text-sm font-medium text-gray-700"> Email </label>
      <InputText
        id="adminEmail"
        :model-value="email"
        type="email"
        placeholder="Enter admin email"
        :invalid="submitted && errors.email"
        class="w-full"
        @update:model-value="emit('update:email', $event as string)"
      />
      <small v-if="submitted && errors.email" class="text-red-500">
        Please enter a valid email address.
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="adminPassword" class="text-sm font-medium text-gray-700"> Password </label>
      <Password
        :model-value="password"
        input-id="adminPassword"
        placeholder="Minimum 8 characters"
        toggle-mask
        :invalid="submitted && errors.password"
        class="w-full"
        input-class="w-full"
        @update:model-value="emit('update:password', $event as string)"
      />
      <small v-if="submitted && errors.password" class="text-red-500">
        Password must be at least 8 characters.
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="adminConfirmPassword" class="text-sm font-medium text-gray-700">
        Confirm Password
      </label>
      <Password
        :model-value="confirmPassword"
        input-id="adminConfirmPassword"
        placeholder="Confirm your password"
        :feedback="false"
        toggle-mask
        :invalid="submitted && errors.confirmPassword"
        class="w-full"
        input-class="w-full"
        @update:model-value="emit('update:confirmPassword', $event as string)"
      />
      <small v-if="submitted && errors.confirmPassword" class="text-red-500">
        Passwords do not match.
      </small>
    </div>

    <div class="flex justify-between pt-2">
      <Button
        type="button"
        label="Back"
        severity="secondary"
        icon="pi pi-arrow-left"
        @click="emit('back')"
      />
      <Button type="submit" label="Register Company" :loading="loading" />
    </div>
  </form>
</template>
