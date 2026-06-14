<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

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
        <div class="app-preloader__orb" aria-hidden="true">
          <span class="app-preloader__ring"></span>
          <span class="app-preloader__dot"></span>
        </div>
        <span class="app-preloader__brand">PreScreen AI</span>
        <span class="sr-only">{{ t('common.loading') }}</span>
      </div>
    </div>
  </Transition>
</template>
