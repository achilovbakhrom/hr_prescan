<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AppLogo from './AppLogo.vue'

const visible = ref(true)
const { t } = useI18n()

onMounted(() => {
  window.setTimeout(() => {
    visible.value = false
  }, 450)
})
</script>

<template>
  <Transition name="app-preloader">
    <div v-if="visible" class="app-preloader" role="status" :aria-label="t('common.loading')">
      <div class="app-preloader__surface">
        <div class="app-preloader__mark" aria-hidden="true">
          <span class="app-preloader__glow" />
          <AppLogo class="app-preloader__logo" size="lg" :linked="false" variant="glyph" />
          <span class="app-preloader__beam" />
          <span class="app-preloader__spark app-preloader__spark--one" />
          <span class="app-preloader__spark app-preloader__spark--two" />
          <span class="app-preloader__spark app-preloader__spark--three" />
        </div>
        <span class="app-preloader__brand">PreScreen AI</span>
        <span class="app-preloader__bar" aria-hidden="true">
          <span />
        </span>
        <span class="sr-only">{{ t('common.loading') }}</span>
      </div>
    </div>
  </Transition>
</template>
