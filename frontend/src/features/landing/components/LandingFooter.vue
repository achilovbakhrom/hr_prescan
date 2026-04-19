<script setup lang="ts">
/**
 * LandingFooter — multi-column footer inside a GlassSurface level=2.
 * Bottom row: small logo glyph + copyright + language switcher.
 */
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import AppLogo from '@/shared/components/AppLogo.vue'
import LanguageSwitcher from '@/shared/components/LanguageSwitcher.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()

function scrollTo(id: string): void {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <footer class="px-4 pb-10 pt-8 sm:px-6">
    <div class="mx-auto max-w-7xl">
      <GlassSurface level="2" class="px-6 py-10 sm:px-10 sm:py-12 rounded-[--radius-lg]">
        <div class="grid gap-10 sm:grid-cols-2 lg:grid-cols-5">
          <!-- Brand -->
          <div class="lg:col-span-2">
            <AppLogo variant="full" size="md" />
            <p
              class="mt-4 max-w-xs text-sm leading-relaxed text-[color:var(--color-text-secondary)]"
            >
              {{ t('landing.footer.tagline') }}
            </p>
          </div>

          <!-- Product -->
          <div>
            <h4
              class="mb-4 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
            >
              {{ t('landing.footer.product') }}
            </h4>
            <ul class="space-y-2.5">
              <li>
                <button
                  type="button"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                  @click="scrollTo('features')"
                >
                  {{ t('landing.footer.features') }}
                </button>
              </li>
              <li>
                <button
                  type="button"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                  @click="scrollTo('how-it-works')"
                >
                  {{ t('landing.howItWorks.title') }}
                </button>
              </li>
              <li>
                <RouterLink
                  :to="{ name: ROUTE_NAMES.PRICING }"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                >
                  {{ t('landing.footer.pricing') }}
                </RouterLink>
              </li>
            </ul>
          </div>

          <!-- Get Started -->
          <div>
            <h4
              class="mb-4 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
            >
              {{ t('landing.hero.getStarted') }}
            </h4>
            <ul class="space-y-2.5">
              <li>
                <RouterLink
                  :to="{ name: ROUTE_NAMES.LOGIN }"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                >
                  {{ t('nav.signIn') }}
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  :to="{ name: ROUTE_NAMES.REGISTER }"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                >
                  {{ t('auth.register.title') }}
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  :to="{ name: ROUTE_NAMES.JOB_BOARD }"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                >
                  {{ t('nav.browseJobs') }}
                </RouterLink>
              </li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h4
              class="mb-4 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
            >
              {{ t('landing.footer.legal') }}
            </h4>
            <ul class="space-y-2.5">
              <li>
                <RouterLink
                  :to="{ name: ROUTE_NAMES.PRIVACY_POLICY }"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                >
                  {{ t('landing.footer.privacy') }}
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  :to="{ name: ROUTE_NAMES.TERMS_OF_SERVICE }"
                  class="text-sm text-[color:var(--color-text-secondary)] transition-colors hover:text-[color:var(--color-text-primary)]"
                >
                  {{ t('landing.footer.terms') }}
                </RouterLink>
              </li>
            </ul>
          </div>
        </div>

        <!-- Bottom row -->
        <div
          class="mt-10 flex flex-col items-center justify-between gap-4 border-t border-[color:var(--color-border-soft)] pt-6 sm:flex-row"
        >
          <div class="flex items-center gap-3">
            <AppLogo variant="glyph" size="sm" />
            <p class="text-xs text-[color:var(--color-text-muted)]">
              &copy; {{ new Date().getFullYear() }} HR PreScan.
              {{ t('landing.footer.copyright') }}
            </p>
          </div>
          <LanguageSwitcher />
        </div>
      </GlassSurface>
    </div>
  </footer>
</template>
