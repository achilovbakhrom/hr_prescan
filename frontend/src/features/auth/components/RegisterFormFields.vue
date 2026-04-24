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

const { t } = useI18n()
</script>

<template>
  <form class="flex flex-col gap-4" @submit.prevent="emit('submit')">
    <div class="grid grid-cols-2 gap-4">
      <div class="flex flex-col gap-1.5">
        <label
          for="firstName"
          class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('auth.register.firstName') }}
        </label>
        <InputText
          id="firstName"
          :model-value="firstName"
          :placeholder="t('auth.register.firstNamePlaceholder')"
          :invalid="submitted && errors.firstName"
          class="w-full"
          @update:model-value="emit('update:firstName', $event as string)"
        />
        <small v-if="submitted && errors.firstName" class="text-[color:var(--color-danger)]">
          {{ t('auth.register.firstNameRequired') }}
        </small>
      </div>
      <div class="flex flex-col gap-1.5">
        <label
          for="lastName"
          class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('auth.register.lastName') }}
        </label>
        <InputText
          id="lastName"
          :model-value="lastName"
          :placeholder="t('auth.register.lastNamePlaceholder')"
          :invalid="submitted && errors.lastName"
          class="w-full"
          @update:model-value="emit('update:lastName', $event as string)"
        />
        <small v-if="submitted && errors.lastName" class="text-[color:var(--color-danger)]">
          {{ t('auth.register.lastNameRequired') }}
        </small>
      </div>
    </div>

    <div class="flex flex-col gap-1.5">
      <label
        for="email"
        class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('auth.register.email') }}
      </label>
      <InputText
        id="email"
        :model-value="email"
        type="email"
        :placeholder="t('auth.register.emailPlaceholder')"
        :invalid="submitted && errors.email"
        class="w-full"
        @update:model-value="emit('update:email', $event as string)"
      />
      <small v-if="submitted && errors.email" class="text-[color:var(--color-danger)]">
        {{ t('auth.register.emailInvalid') }}
      </small>
    </div>

    <div class="flex flex-col gap-1.5">
      <label
        for="password"
        class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('auth.register.password') }}
      </label>
      <Password
        :model-value="password"
        input-id="password"
        :placeholder="t('auth.register.passwordPlaceholder')"
        toggle-mask
        :invalid="submitted && errors.password"
        class="w-full"
        input-class="w-full"
        @update:model-value="emit('update:password', $event)"
      />
      <small v-if="submitted && errors.password" class="text-[color:var(--color-danger)]">
        {{ t('auth.register.passwordTooShort') }}
      </small>
    </div>

    <div class="flex flex-col gap-1.5">
      <label
        for="confirmPassword"
        class="text-xs font-medium uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('auth.register.confirmPassword') }}
      </label>
      <Password
        :model-value="confirmPassword"
        input-id="confirmPassword"
        :placeholder="t('auth.register.confirmPasswordPlaceholder')"
        :feedback="false"
        toggle-mask
        :invalid="submitted && errors.confirmPassword"
        class="w-full"
        input-class="w-full"
        @update:model-value="emit('update:confirmPassword', $event)"
      />
      <small v-if="submitted && errors.confirmPassword" class="text-[color:var(--color-danger)]">
        {{ t('auth.register.passwordMismatch') }}
      </small>
    </div>

    <Button
      type="submit"
      :label="t('auth.register.submit')"
      :loading="loading"
      class="auth-primary-button mt-2 w-full"
    />
  </form>
</template>

<style scoped>
:global(html.dark) .auth-primary-button {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28) !important;
}

:global(html.dark) .auth-primary-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
  border-color: #60a5fa !important;
}
</style>
