<script setup lang="ts">
import { onMounted, ref } from 'vue'
import RegisterPage from '@/features/auth/pages/RegisterPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.REGISTER, layout: 'auth', requiresAuth: false })

const ready = ref(false)

onMounted(() => {
  ready.value = true
})
</script>

<template>
  <RegisterPage v-if="ready" />
</template>
