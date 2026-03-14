import { onBeforeUnmount, onMounted, type Ref } from 'vue'

const FOCUSABLE_SELECTORS = [
  'a[href]',
  'area[href]',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  'button:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
  'details > summary',
].join(', ')

function getFocusableElements(container: HTMLElement): HTMLElement[] {
  return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTORS)).filter(
    (el) => !el.closest('[hidden]') && !el.closest('[aria-hidden="true"]'),
  )
}

export function useFocusTrap(containerRef: Ref<HTMLElement | null>, active: Ref<boolean>) {
  let previouslyFocused: HTMLElement | null = null

  function trapFocus(event: KeyboardEvent): void {
    if (!active.value || !containerRef.value) return
    if (event.key !== 'Tab') return

    const focusable = getFocusableElements(containerRef.value)
    if (focusable.length === 0) return

    const first = focusable[0]
    const last = focusable[focusable.length - 1]

    if (event.shiftKey) {
      if (document.activeElement === first) {
        event.preventDefault()
        last.focus()
      }
    } else {
      if (document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
  }

  function trapEscape(event: KeyboardEvent): void {
    if (!active.value) return
    if (event.key === 'Escape') {
      releaseFocus()
    }
  }

  function captureFocus(): void {
    previouslyFocused = document.activeElement as HTMLElement | null
    if (containerRef.value) {
      const focusable = getFocusableElements(containerRef.value)
      if (focusable.length > 0) {
        focusable[0].focus()
      } else {
        containerRef.value.focus()
      }
    }
  }

  function releaseFocus(): void {
    if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
      previouslyFocused.focus()
    }
    previouslyFocused = null
  }

  onMounted(() => {
    document.addEventListener('keydown', trapFocus)
    document.addEventListener('keydown', trapEscape)
  })

  onBeforeUnmount(() => {
    document.removeEventListener('keydown', trapFocus)
    document.removeEventListener('keydown', trapEscape)
    releaseFocus()
  })

  return { captureFocus, releaseFocus }
}
