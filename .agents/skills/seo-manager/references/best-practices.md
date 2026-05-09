# SEO Best Practices Reference

Primary sources:

- Google Search Central: JavaScript SEO basics
  https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Google Search Central: canonical URLs
  https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Google Search Central: JobPosting structured data
  https://developers.google.com/search/docs/appearance/structured-data/job-posting
- Sitemaps protocol
  https://www.sitemaps.org/protocol.html

## JavaScript SEO

- Google can render JavaScript, but rendering is a second phase after crawling and can be delayed.
- Server-side rendering or prerendering is still useful because the first HTML response already contains meaningful content and metadata.
- If JavaScript sets canonical URLs, keep them consistent with the original HTML and sitemap.
- Use meaningful HTTP status codes; avoid SPA soft-404 behavior for missing public pages when possible.

## Canonicals

- Use one canonical URL per page and keep it consistent across tags, sitemaps, and internal links.
- Do not use `robots.txt` as a canonicalization tool.
- Do not canonicalize to URL fragments.
- Link internally to canonical URLs, not share-token or duplicate URLs.

## Robots And Sitemaps

- `robots.txt` prevents crawling; `noindex` prevents indexing after a crawler can access the page.
- Do not include URLs in sitemaps if they are blocked by `robots.txt`, require login, are non-canonical, or intentionally noindexed.
- Use accurate `<lastmod>` values for job URLs when possible.
- Keep listing/search pages out of job-specific sitemaps unless there is a deliberate SEO strategy for those pages.

## JobPosting Structured Data

- Add `JobPosting` only to the specific page for one job.
- Do not add `JobPosting` to job board/search result pages.
- Required Google properties include `datePosted`, `description`, `hiringOrganization`, `jobLocation` or remote-job equivalents, and `title`.
- Remote jobs should use `jobLocationType: TELECOMMUTE`; include applicant location requirements when the job is restricted by country or region.
- `description` should represent the full job content shown to users.
- Markup must match visible page content. Do not add hidden salary, company, location, expiry, or apply data.
- Expired or closed jobs should be removed, return 404/410, have `validThrough` in the past, or have `JobPosting` removed.
- For job posting URLs, Google recommends the Indexing API for faster crawl notification, while still keeping a sitemap for coverage.
