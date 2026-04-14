<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import AppLogo from '@/shared/components/AppLogo.vue'

const { t } = useI18n()

function scrollTo(id: string): void {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <footer class="border-t border-gray-800 bg-gray-900 px-6 py-14">
    <div class="mx-auto max-w-7xl">
      <div class="grid gap-10 sm:grid-cols-2 lg:grid-cols-5">
        <!-- Brand -->
        <div class="lg:col-span-2">
          <div class="mb-4 flex items-center gap-2.5">
            <AppLogo size="sm" />
            <span class="text-lg font-bold text-white">PreScreen AI</span>
          </div>
          <p class="max-w-xs text-sm leading-relaxed text-gray-400">
            {{ t('landing.footer.tagline') }}
          </p>
        </div>

        <!-- Product -->
        <div>
          <h4 class="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
            {{ t('landing.footer.product') }}
          </h4>
          <ul class="space-y-2.5">
            <li>
              <button
                type="button"
                class="text-sm text-gray-400 transition-colors hover:text-white"
                @click="scrollTo('features')"
              >
                {{ t('landing.footer.features') }}
              </button>
            </li>
            <li>
              <button
                type="button"
                class="text-sm text-gray-400 transition-colors hover:text-white"
                @click="scrollTo('how-it-works')"
              >
                {{ t('landing.howItWorks.title') }}
              </button>
            </li>
            <li>
              <RouterLink
                :to="{ name: ROUTE_NAMES.PRICING }"
                class="text-sm text-gray-400 transition-colors hover:text-white"
              >
                {{ t('landing.footer.pricing') }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Get Started -->
        <div>
          <h4 class="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
            {{ t('landing.hero.getStarted') }}
          </h4>
          <ul class="space-y-2.5">
            <li>
              <RouterLink
                :to="{ name: ROUTE_NAMES.LOGIN }"
                class="text-sm text-gray-400 transition-colors hover:text-white"
              >
                {{ t('nav.signIn') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink
                :to="{ name: ROUTE_NAMES.REGISTER }"
                class="text-sm text-gray-400 transition-colors hover:text-white"
              >
                {{ t('auth.register.title') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink
                :to="{ name: ROUTE_NAMES.JOB_BOARD }"
                class="text-sm text-gray-400 transition-colors hover:text-white"
              >
                {{ t('nav.browseJobs') }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h4 class="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">
            {{ t('landing.footer.legal') }}
          </h4>
          <ul class="space-y-2.5">
            <li>
              <RouterLink
                :to="{ name: ROUTE_NAMES.PRIVACY_POLICY }"
                class="text-sm text-gray-400 transition-colors hover:text-white"
              >
                {{ t('landing.footer.privacy') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink
                :to="{ name: ROUTE_NAMES.TERMS_OF_SERVICE }"
                class="text-sm text-gray-400 transition-colors hover:text-white"
              >
                {{ t('landing.footer.terms') }}
              </RouterLink>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-12 border-t border-gray-800 pt-6 text-center text-sm text-gray-500">
        &copy; {{ new Date().getFullYear() }} PreScreen AI. {{ t('landing.footer.copyright') }}
      </div>
    </div>
  </footer>
</template>
