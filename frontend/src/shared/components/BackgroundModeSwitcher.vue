<script setup lang="ts">
/**
 * DEPRECATED — kept as a back-compat shim during the UI redesign migration.
 * The real implementation lives in FloatingBackgroundPicker.vue.
 *
 * Existing usages in AppNavbar / PublicHeader / LandingNav continue to work
 * but now render the floating picker. Once PageShell is wired into the
 * layouts (T10/T12), these call-sites should be removed in favor of a single
 * mount inside PageShell.
 */
import FloatingBackgroundPicker from './FloatingBackgroundPicker.vue'
</script>

<template>
  <FloatingBackgroundPicker />
</template>
