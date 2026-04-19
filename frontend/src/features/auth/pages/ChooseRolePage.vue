<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Message from 'primevue/message'
import AuthShell from '../components/AuthShell.vue'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import { useAuthStore } from '../stores/auth.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const loading = ref(false)
const errorMessage = ref<string | null>(null)

async function handleRoleSelect(role: 'candidate' | 'hr'): Promise<void> {
  loading.value = true
  errorMessage.value = null
  try {
    await authStore.completeOnboarding(role)
    if (role === 'hr') {
      await router.push({ name: ROUTE_NAMES.COMPANY_SETUP })
    } else {
      await router.push({ name: ROUTE_NAMES.DASHBOARD })
    }
  } catch (err: unknown) {
    errorMessage.value =
      err instanceof Error ? err.message : 'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthShell :title="t('auth.chooseRole.title')" width="lg">
    <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

    <div class="flex flex-col gap-3">
      <GlassSurface
        as="button"
        level="2"
        interactive
        class="role-option group flex w-full items-center gap-4 p-4 text-left sm:p-5"
        :aria-disabled="loading"
        :disabled="loading"
        @click="handleRoleSelect('candidate')"
      >
        <div
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-celebrate-soft)] sm:h-14 sm:w-14"
        >
          <i class="pi pi-user text-xl text-[color:var(--color-accent-celebrate)] sm:text-2xl" />
        </div>
        <div>
          <p class="text-base font-semibold text-[color:var(--color-text-primary)] sm:text-lg">
            {{ t('auth.chooseRole.candidate') }}
          </p>
          <p class="mt-1 text-sm text-[color:var(--color-text-secondary)]">
            {{ t('auth.chooseRole.candidateDescription') }}
          </p>
        </div>
      </GlassSurface>

      <GlassSurface
        as="button"
        level="2"
        interactive
        class="role-option group flex w-full items-center gap-4 p-4 text-left sm:p-5"
        :aria-disabled="loading"
        :disabled="loading"
        @click="handleRoleSelect('hr')"
      >
        <div
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-ai-soft)] sm:h-14 sm:w-14"
        >
          <i class="pi pi-building text-xl text-[color:var(--color-accent-ai)] sm:text-2xl" />
        </div>
        <div>
          <p class="text-base font-semibold text-[color:var(--color-text-primary)] sm:text-lg">
            {{ t('auth.chooseRole.company') }}
          </p>
          <p class="mt-1 text-sm text-[color:var(--color-text-secondary)]">
            {{ t('auth.chooseRole.companyDescription') }}
          </p>
        </div>
      </GlassSurface>
    </div>
  </AuthShell>
</template>

<style scoped>
.role-option[disabled] {
  opacity: 0.6;
  pointer-events: none;
}
</style>
