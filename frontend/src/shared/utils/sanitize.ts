import DOMPurify from 'dompurify'

/**
 * Sanitize HTML content to prevent XSS attacks.
 * Use this whenever rendering user-provided or AI-generated HTML via v-html.
 */
export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'b',
      'i',
      'em',
      'strong',
      'a',
      'p',
      'br',
      'ul',
      'ol',
      'li',
      'h1',
      'h2',
      'h3',
      'h4',
      'h5',
      'h6',
      'blockquote',
      'code',
      'pre',
      'span',
      'div',
      'table',
      'thead',
      'tbody',
      'tr',
      'th',
      'td',
      'hr',
      'img',
      'sub',
      'sup',
      'mark',
      's',
      'u',
    ],
    ALLOWED_ATTR: [
      'href',
      'target',
      'rel',
      'class',
      'src',
      'alt',
      'width',
      'height',
      'title',
      'style',
    ],
    ALLOW_DATA_ATTR: false,
  })
}
