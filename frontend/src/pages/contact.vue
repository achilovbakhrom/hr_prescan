<script setup lang="ts">
import ContactPage from '@/features/landing/pages/ContactPage.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.CONTACT,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'Contact us | PreScreen AI',
    description: 'Get in touch with the PreScreen AI team — questions, feedback, or support.',
    path: '/contact',
  },
})
</script>

<template>
  <ContactPage />
</template>
