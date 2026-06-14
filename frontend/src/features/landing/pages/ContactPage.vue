<script setup lang="ts">
/** ContactPage — public "Contact us" form; emails the support inbox. */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import { contactService } from '@/shared/services/contact.service'

const { t } = useI18n()

const name = ref('')
const email = ref('')
const subject = ref('')
const message = ref('')
const loading = ref(false)
const sent = ref(false)
const errorMsg = ref('')

const emailValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim()))
const canSubmit = computed(
  () => name.value.trim() && emailValid.value && message.value.trim().length >= 5,
)

async function submit(): Promise<void> {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    await contactService.send({
      name: name.value.trim(),
      email: email.value.trim(),
      subject: subject.value.trim() || undefined,
      message: message.value.trim(),
    })
    sent.value = true
  } catch {
    errorMsg.value = t('contact.error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="mx-auto w-full max-w-xl px-4 py-12 sm:py-16">
    <div class="mb-8 text-center">
      <h1
        class="text-3xl font-bold tracking-tight text-[color:var(--color-text-primary)] sm:text-4xl"
      >
        {{ t('contact.title') }}
      </h1>
      <p class="mx-auto mt-3 max-w-md text-base text-[color:var(--color-text-secondary)]">
        {{ t('contact.subtitle') }}
      </p>
    </div>

    <GlassCard>
      <div v-if="sent" class="py-8 text-center">
        <span
          class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
        >
          <i class="pi pi-check text-2xl"></i>
        </span>
        <h2 class="mt-4 text-xl font-semibold text-[color:var(--color-text-primary)]">
          {{ t('contact.successTitle') }}
        </h2>
        <p class="mx-auto mt-2 max-w-sm text-sm text-[color:var(--color-text-secondary)]">
          {{ t('contact.successBody') }}
        </p>
      </div>

      <form v-else class="space-y-4" @submit.prevent="submit">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('contact.name') }} *</label>
            <InputText v-model="name" class="w-full" :placeholder="t('contact.namePlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('contact.email') }} *</label>
            <InputText v-model="email" type="email" class="w-full" placeholder="john@example.com" />
          </div>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('contact.subject') }}</label>
          <InputText
            v-model="subject"
            class="w-full"
            :placeholder="t('contact.subjectPlaceholder')"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('contact.message') }} *</label>
          <Textarea
            v-model="message"
            class="w-full"
            rows="5"
            :placeholder="t('contact.messagePlaceholder')"
          />
        </div>

        <p v-if="errorMsg" class="text-sm text-[color:var(--color-danger)]">{{ errorMsg }}</p>

        <Button
          type="submit"
          :label="loading ? t('contact.sending') : t('contact.send')"
          icon="pi pi-send"
          class="w-full"
          :loading="loading"
          :disabled="!canSubmit"
        />
      </form>
    </GlassCard>
  </div>
</template>
