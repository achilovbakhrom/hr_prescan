/**
 * useBackgroundPickerKeys — keyboard + click-outside handlers for the
 * FloatingBackgroundPicker. Extracted to keep the component file under the
 * 200-line limit.
 *
 * Shortcuts:
 *   - `?` or `Alt+B` → toggle
 *   - `Esc` → close (when open)
 *
 * Typing in inputs/textareas is never hijacked.
 */
import { onBeforeUnmount, onMounted, type Ref } from 'vue'

interface Options {
  rootRef: Ref<HTMLElement | null>
  isOpen: Ref<boolean>
  toggle: () => void
  close: () => void
}

function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  return target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable
}

export function useBackgroundPickerKeys(opts: Options): void {
  const { rootRef, isOpen, toggle, close } = opts

  function onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape' && isOpen.value) {
      event.preventDefault()
      close()
      return
    }

    if (isTypingTarget(event.target)) return

    const isQuestion = event.key === '?'
    const isAltB = event.altKey && (event.key === 'b' || event.key === 'B')
    if (isQuestion || isAltB) {
      event.preventDefault()
      toggle()
    }
  }

  function onClickOutside(event: MouseEvent): void {
    if (!isOpen.value) return
    const target = event.target as Node | null
    if (rootRef.value && target && !rootRef.value.contains(target)) {
      close()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', onKeydown)
    document.addEventListener('mousedown', onClickOutside)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', onKeydown)
    document.removeEventListener('mousedown', onClickOutside)
  })
}
