<script setup lang="ts">
import PublicVacancyDetailPage from '@/features/vacancies/pages/PublicVacancyDetailPage.vue'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import { buildPublicVacancySeoMeta } from '@/features/vacancies/utils/vacancySeo'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { absoluteUrl } from '@/shared/seo/meta'

definePageMeta({
  name: ROUTE_NAMES.JOB_SHARE,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'Shared Job | PreScreen AI',
    description: 'View a shared vacancy on PreScreen AI.',
    path: '/jobs',
    noindex: true,
    robots: 'noindex, follow',
  },
})

const route = useRoute()
const token = String(route.params.token)

const { data: seoVacancy } = await useAsyncData(`job-share-seo-${token}`, async () => {
  try {
    return await vacancyService.getByShareToken(token)
  } catch {
    return null
  }
})

if (seoVacancy.value) {
  const seo = buildPublicVacancySeoMeta(seoVacancy.value, { noindex: true })

  useHead({
    title: seo.title,
    meta: [
      { name: 'description', content: seo.description },
      { name: 'robots', content: seo.robots },
      { property: 'og:type', content: seo.type },
      { property: 'og:url', content: seo.canonicalUrl },
      { property: 'og:title', content: seo.title },
      { property: 'og:description', content: seo.description },
      { property: 'og:image', content: absoluteUrl('/og-image.png') },
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: seo.title },
      { name: 'twitter:description', content: seo.description },
      { name: 'twitter:image', content: absoluteUrl('/og-image.png') },
    ],
    link: [{ rel: 'canonical', href: seo.canonicalUrl }],
  })
}
</script>

<template>
  <PublicVacancyDetailPage />
</template>
