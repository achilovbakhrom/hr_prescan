<script setup lang="ts">
import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/features/auth/stores/auth.store'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import ThemeToggle from '@/shared/components/ThemeToggle.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import AccountModeSwitcher from './AccountModeSwitcher.vue'
import CompanySwitcher from './CompanySwitcher.vue'
import MobileNavItems from './MobileNavItems.vue'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()
const showCompanyContext = computed(
  () =>
    authStore.activeMode === 'hr' &&
    (authStore.companies.length > 0 || Boolean(authStore.user?.company)),
)

watch(
  () => route.path,
  () => {
    if (props.open) emit('close')
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-40 bg-black/50 lg:hidden"
        aria-hidden="true"
        @click="emit('close')"
      ></div>
    </Transition>

    <Transition
      enter-active-class="transition-transform duration-300 ease-out"
      enter-from-class="-translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-300 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="-translate-x-full"
    >
      <div
        v-if="open"
        class="fixed inset-y-0 left-0 z-50 flex w-[86vw] max-w-80 flex-col bg-white shadow-xl dark:bg-gray-900 lg:hidden"
        role="dialog"
        aria-modal="true"
        :aria-label="t('common.aria.mobileNavigation')"
      >
        <div
          class="flex h-16 items-center justify-between border-b border-gray-200 dark:border-gray-700 px-4"
        >
          <div class="flex items-center gap-2">
            <AppLogo size="sm" />
          </div>
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 dark:text-gray-400 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700"
            :aria-label="t('common.aria.closeNavigationMenu')"
            @click="emit('close')"
          >
            <i class="pi pi-times text-base"></i>
          </button>
        </div>

        <div
          v-if="authStore.user"
          class="space-y-2 border-b border-gray-200 px-4 py-3 dark:border-gray-700"
        >
          <CompanySwitcher v-if="showCompanyContext" class="w-full" />
          <AccountModeSwitcher class="w-full" />
        </div>

        <MobileNavItems />

        <div
          class="flex items-center justify-between border-t border-gray-200 px-4 py-3 dark:border-gray-700"
        >
          <LanguageSwitcher />
          <ThemeToggle />
        </div>

        <div v-if="authStore.user" class="border-t border-gray-200 dark:border-gray-700 px-4 py-3">
          <div class="flex items-center gap-3">
            <div
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[color:var(--color-accent-soft)] text-sm font-medium text-[color:var(--color-accent)]"
            >
              {{ authStore.user.firstName?.charAt(0) ?? ''
              }}{{ authStore.user.lastName?.charAt(0) ?? '' }}
            </div>
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ authStore.user.firstName }} {{ authStore.user.lastName }}
              </p>
              <p class="truncate text-xs text-gray-500 dark:text-gray-400">
                {{ authStore.user.email }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
