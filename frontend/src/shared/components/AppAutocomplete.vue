<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import PrimeAutoComplete from 'primevue/autocomplete'

defineOptions({ inheritAttrs: false })

const attrs = useAttrs()

const rootClass = computed(() => ['app-autocomplete', attrs.class])
const forwardedAttrs = computed(() => {
  const rest = { ...attrs }
  delete rest.class
  return {
    dropdownIcon:
      typeof attrs.dropdownIcon === 'string' ? attrs.dropdownIcon : 'pi pi-chevron-down',
    ...rest,
  }
})
</script>

<template>
  <PrimeAutoComplete v-bind="forwardedAttrs" :class="rootClass">
    <template v-if="$slots.option" #option="slotProps">
      <slot name="option" v-bind="slotProps" />
    </template>
    <template v-if="$slots.header" #header="slotProps">
      <slot name="header" v-bind="slotProps" />
    </template>
    <template v-if="$slots.footer" #footer="slotProps">
      <slot name="footer" v-bind="slotProps" />
    </template>
    <template v-if="$slots.chip" #chip="slotProps">
      <slot name="chip" v-bind="slotProps" />
    </template>
    <template v-if="$slots.empty" #empty>
      <slot name="empty" />
    </template>
    <template v-if="$slots.loader" #loader="slotProps">
      <slot name="loader" v-bind="slotProps" />
    </template>
    <template v-if="$slots.dropdownicon" #dropdownicon>
      <slot name="dropdownicon" />
    </template>
  </PrimeAutoComplete>
</template>
