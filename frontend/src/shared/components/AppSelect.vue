<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import PrimeSelect from 'primevue/select'

defineOptions({ inheritAttrs: false })

const attrs = useAttrs()

const rootClass = computed(() => ['app-select', attrs.class])
const forwardedAttrs = computed(() => {
  const { class: _class, ...rest } = attrs
  return {
    dropdownIcon:
      typeof attrs.dropdownIcon === 'string' ? attrs.dropdownIcon : 'pi pi-chevron-down',
    ...rest,
  }
})
</script>

<template>
  <PrimeSelect v-bind="forwardedAttrs" :class="rootClass">
    <template v-if="$slots.value" #value="slotProps">
      <slot name="value" v-bind="slotProps" />
    </template>
    <template v-if="$slots.option" #option="slotProps">
      <slot name="option" v-bind="slotProps" />
    </template>
    <template v-if="$slots.header" #header="slotProps">
      <slot name="header" v-bind="slotProps" />
    </template>
    <template v-if="$slots.footer" #footer="slotProps">
      <slot name="footer" v-bind="slotProps" />
    </template>
    <template v-if="$slots.empty" #empty>
      <slot name="empty" />
    </template>
    <template v-if="$slots.emptyfilter" #emptyfilter>
      <slot name="emptyfilter" />
    </template>
    <template v-if="$slots.dropdownicon" #dropdownicon>
      <slot name="dropdownicon" />
    </template>
  </PrimeSelect>
</template>
