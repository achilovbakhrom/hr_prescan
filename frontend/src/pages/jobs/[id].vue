<script setup lang="ts">
import PublicVacancyDetailPage from '@/features/vacancies/pages/PublicVacancyDetailPage.vue'
import { vacancyService } from '@/features/vacancies/services/vacancy.service'
import {
  buildPublicVacancyJsonLd,
  buildPublicVacancySeoMeta,
} from '@/features/vacancies/utils/vacancySeo'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { absoluteUrl } from '@/shared/seo/meta'

definePageMeta({
  name: ROUTE_NAMES.JOB_DETAIL,
  layout: 'public',
  requiresAuth: false,
  seo: {
    title: 'Job Details | PreScreen AI',
    description: 'View vacancy details and apply through PreScreen AI.',
  },
})

const route = useRoute()
const vacancyId = String(route.params.id)

const { data: seoVacancy } = await useAsyncData(`job-seo-${vacancyId}`, async () => {
  try {
    return await vacancyService.getPublicDetail(vacancyId)
  } catch {
    return null
  }
})

if (seoVacancy.value) {
  const seo = buildPublicVacancySeoMeta(seoVacancy.value, { noindex: false })
  const jsonLd = buildPublicVacancyJsonLd(seoVacancy.value)

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
    script: jsonLd
      ? [
          {
            id: 'job-posting',
            type: 'application/ld+json',
            innerHTML: JSON.stringify(jsonLd),
          },
        ]
      : [],
  })
}
</script>

<template>
  <PublicVacancyDetailPage />
</template>
