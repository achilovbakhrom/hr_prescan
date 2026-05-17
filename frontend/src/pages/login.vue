<script setup lang="ts">
import { onMounted, ref } from 'vue'
import LoginPage from '@/features/auth/pages/LoginPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({ name: ROUTE_NAMES.LOGIN, layout: 'auth', requiresAuth: false })

const ready = ref(false)

onMounted(() => {
  ready.value = true
})
</script>

<template>
  <LoginPage v-if="ready" />
</template>
