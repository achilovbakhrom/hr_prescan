import { GUIDE_STRUCTURE } from './guide.structure'
import type { Guide, GuideText } from './guide.types'
import en from './text/en'
import ru from './text/ru'
import uz from './text/uz'
import kk from './text/kk'
import tr from './text/tr'
import ar from './text/ar'
import es from './text/es'
import fr from './text/fr'
import de from './text/de'
import uk from './text/uk'

const TEXT: Record<string, GuideText> = { en, ru, uz, kk, tr, ar, es, fr, de, uk }

/**
 * Merge the language-independent structure with the text for `locale` (falling
 * back to English per-field), producing a ready-to-render guide. Screenshots
 * are served per locale from /guide/<locale>/<base>.png.
 */
export function getGuide(locale: string): Guide {
  const text = TEXT[locale] ?? en
  const flows = GUIDE_STRUCTURE.map((s) => {
    const ft = text.flows[s.id] ?? en.flows[s.id]
    return {
      id: s.id,
      icon: s.icon,
      audience: s.audience,
      title: ft.title,
      summary: ft.summary,
      steps: s.steps.map((st, i) => {
        const t = ft.steps[i] ?? en.flows[s.id].steps[i]
        return {
          title: t.title,
          description: t.description,
          image: `/guide/${locale}/${st.image}.png`,
          imageFallback: `/guide/en/${st.image}.png`,
          imageAlt: t.alt,
        }
      }),
    }
  })
  return {
    page: {
      title: text.title,
      subtitle: text.subtitle,
      onThisPage: text.onThisPage,
      forHr: text.forHr,
      forCandidates: text.forCandidates,
    },
    flows,
  }
}
