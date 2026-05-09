import type { Router } from 'vue-router'
import { setJsonLd, setSeoMeta, type SeoMetaInput } from './meta'

export interface RouteSeoMeta extends SeoMetaInput {
  noindex?: boolean
}

export function installSeoRouterGuards(router: Router): void {
  router.afterEach((to) => {
    setJsonLd('job-posting', null)

    const seo = to.meta.seo
    if (seo) {
      setSeoMeta({
        ...seo,
        path: seo.path ?? to.path,
        robots: seo.robots ?? (seo.noindex ? 'noindex, nofollow' : 'index, follow'),
      })
      return
    }

    setSeoMeta({
      path: to.path,
      robots: to.meta.requiresAuth === false ? 'noindex, follow' : 'noindex, nofollow',
    })
  })
}
