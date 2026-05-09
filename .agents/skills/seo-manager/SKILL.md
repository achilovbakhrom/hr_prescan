---
name: seo-manager
description: Audit and improve technical SEO for HR PreScan public pages. Use when Codex needs to review or implement search indexing, SSR/prerender strategy, route metadata, canonical URLs, robots.txt, sitemaps, Open Graph/Twitter cards, hreflang, structured data such as JobPosting, Search Console readiness, or SPA JavaScript SEO best practices.
---

# SEO Manager

Own technical SEO outcomes for public, indexable surfaces while protecting private SaaS, application, interview, and tokenized pages from indexing.

## Workflow

1. Read `docs/BUSINESS_LOGIC.md`, `docs/TECH_ARCHITECTURE.md`, and current route/server config before changing behavior.
2. Classify routes:
   - **Index**: public marketing pages, public job board, canonical public job detail pages.
   - **Noindex/block**: authenticated app pages, auth pages, application flows, interviews, private/share-token URLs, public CV token URLs, admin pages, search/filter result variants unless intentionally canonicalized.
3. Inspect the rendered and raw HTML for public URLs. Do not assume SPA runtime metadata is enough for all crawlers.
4. Verify every indexable page has a unique title, description, canonical URL, Open Graph/Twitter metadata, and meaningful visible content.
5. Verify canonical consistency across HTML, JavaScript updates, sitemap URLs, internal links, and share/duplicate URLs.
6. Use `JobPosting` structured data only on single job detail pages, never on job listing/search pages.
7. Keep structured data truthful and visible on the page. Do not add salary, location, company, expiry, or apply information that the user cannot see.
8. Prefer low-risk improvements in this order:
   - Static metadata, robots, sitemap, canonical fixes.
   - Dynamic sitemap for public vacancies.
   - Prerender public static pages and stable public detail pages when feasible.
   - Full SSR/Nuxt only when route/content needs justify migration cost.
9. Validate with local build, browser inspection, and crawler-facing checks. For production work, verify deployed `/robots.txt`, `/sitemap.xml`, representative public pages, and HTTP status codes.

## HR PreScan Rules

- Public vacancy canonical URL is `/jobs/:id`.
- Share-token vacancy URLs must remain usable but must not be indexed; canonicalize them to `/jobs/:id`.
- Application, interview, dashboard, admin, settings, company management, and tokenized CV routes must not be indexed.
- Public parsed external vacancies can be indexed only if the detail page is complete and truthful; omit apply-related structured data if users cannot apply on PreScreen.
- Multilingual UI does not imply hreflang unless there are stable language-specific URLs. Do not emit fake hreflang for browser-detected language on the same URL.
- Sitemap job URLs must include only canonical, crawlable, published public vacancy URLs.

## Validation Checklist

- `yarn --cwd frontend typecheck`
- `yarn --cwd frontend lint:check`
- `yarn --cwd frontend format:check`
- `yarn --cwd frontend build`
- `curl -I` for `/`, `/jobs`, `/robots.txt`, `/sitemap.xml`, and one public job URL when available.
- Browser inspect `document.title`, `meta[name="description"]`, `meta[name="robots"]`, `link[rel="canonical"]`, `meta[property^="og:"]`, and JSON-LD scripts.
- Check that private/token/auth routes are absent from sitemaps and carry noindex behavior.

## References

Load `references/best-practices.md` when making SEO architecture decisions or structured-data changes.
