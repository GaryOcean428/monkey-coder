/**
 * Accessibility Utilities
 * 
 * Helper functions and hooks for improving accessibility
 */

import { useEffect, useRef, useState } from 'react'

/**
 * Generate a unique ID for accessibility attributes
 */
export function useId(prefix = 'id'): string {
  const [id] = useState(() => `${prefix}-${Math.random().toString(36).substr(2, 9)}`)
  return id
}

/**
 * Manage focus trap within a container
 * 
 * @example
 * ```tsx
 * const modalRef = useFocusTrap<HTMLDivElement>()
 * return <div ref={modalRef}>...</div>
 * ```
 */
export function useFocusTrap<T extends HTMLElement>() {
  const ref = useRef<T>(null)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const focusableElements = element.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    function handleTabKey(e: KeyboardEvent) {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus()
          e.preventDefault()
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus()
          e.preventDefault()
        }
      }
    }

    element.addEventListener('keydown', handleTabKey)
    firstElement?.focus()

    return () => {
      element.removeEventListener('keydown', handleTabKey)
    }
  }, [])

  return ref
}

/**
 * Announce message to screen readers
 * 
 * @example
 * ```tsx
 * const announce = useAnnouncer()
 * announce('Form submitted successfully', 'polite')
 * ```
 */
export function useAnnouncer() {
  const [announcer, setAnnouncer] = useState<HTMLDivElement | null>(null)

  useEffect(() => {
    const div = document.createElement('div')
    div.setAttribute('role', 'status')
    div.setAttribute('aria-live', 'polite')
    div.setAttribute('aria-atomic', 'true')
    div.className = 'sr-only'
    document.body.appendChild(div)
    setAnnouncer(div)

    return () => {
      document.body.removeChild(div)
    }
  }, [])

  return (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (announcer) {
      announcer.setAttribute('aria-live', priority)
      announcer.textContent = message
      
      // Clear after announcement
      setTimeout(() => {
        announcer.textContent = ''
      }, 1000)
    }
  }
}

/**
 * Hook to detect if user prefers reduced motion
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handler = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

  return prefersReducedMotion
}

/**
 * Hook to manage keyboard navigation in a list
 * 
 * @example
 * ```tsx
 * const { activeIndex, handleKeyDown } = useKeyboardNavigation(items.length)
 * ```
 */
export function useKeyboardNavigation(itemCount: number) {
  const [activeIndex, setActiveIndex] = useState(0)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setActiveIndex((prev) => (prev + 1) % itemCount)
        break
      case 'ArrowUp':
        e.preventDefault()
        setActiveIndex((prev) => (prev - 1 + itemCount) % itemCount)
        break
      case 'Home':
        e.preventDefault()
        setActiveIndex(0)
        break
      case 'End':
        e.preventDefault()
        setActiveIndex(itemCount - 1)
        break
    }
  }

  return { activeIndex, setActiveIndex, handleKeyDown }
}

/**
 * Check if element is visible in viewport
 */
export function useIntersectionObserver(
  ref: React.RefObject<HTMLElement>,
  options: IntersectionObserverInit = {}
): boolean {
  const [isIntersecting, setIsIntersecting] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => setIsIntersecting(entry.isIntersecting),
      options
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [ref, options])

  return isIntersecting
}

/**
 * ARIA label utilities
 */
export const aria = {
  /**
   * Create ARIA attributes for a combobox
   */
  combobox: (options: {
    expanded: boolean
    hasPopup?: boolean
    controls?: string
    activeDescendant?: string
  }) => ({
    role: 'combobox',
    'aria-expanded': options.expanded,
    'aria-haspopup': options.hasPopup !== false ? 'listbox' : undefined,
    'aria-controls': options.controls,
    'aria-activedescendant': options.activeDescendant,
  }),

  /**
   * Create ARIA attributes for a dialog
   */
  dialog: (options: {
    labelledBy?: string
    describedBy?: string
    modal?: boolean
  }) => ({
    role: 'dialog',
    'aria-labelledby': options.labelledBy,
    'aria-describedby': options.describedBy,
    'aria-modal': options.modal !== false,
  }),

  /**
   * Create ARIA attributes for a tab panel
   */
  tabPanel: (options: {
    labelledBy: string
    hidden?: boolean
  }) => ({
    role: 'tabpanel',
    'aria-labelledby': options.labelledBy,
    'aria-hidden': options.hidden,
    tabIndex: options.hidden ? -1 : 0,
  }),

  /**
   * Create ARIA attributes for a tab
   */
  tab: (options: {
    selected: boolean
    controls: string
  }) => ({
    role: 'tab',
    'aria-selected': options.selected,
    'aria-controls': options.controls,
    tabIndex: options.selected ? 0 : -1,
  }),
}

/**
 * Screen reader only styles
 */
export const srOnly = {
  position: 'absolute' as const,
  width: '1px',
  height: '1px',
  padding: '0',
  margin: '-1px',
  overflow: 'hidden',
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap' as const,
  borderWidth: '0',
}

/**
 * Get contrast ratio between two colors
 */
export function getContrastRatio(color1: string, color2: string): number {
  const getLuminance = (color: string): number => {
    // Simple RGB extraction (for hex colors)
    const hex = color.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16) / 255
    const g = parseInt(hex.substr(2, 2), 16) / 255
    const b = parseInt(hex.substr(4, 2), 16) / 255

    const [rs, gs, bs] = [r, g, b].map(c => 
      c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    )

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }

  const lum1 = getLuminance(color1)
  const lum2 = getLuminance(color2)

  const lighter = Math.max(lum1, lum2)
  const darker = Math.min(lum1, lum2)

  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Check if contrast meets WCAG standards
 */
export function meetsWCAGContrast(
  color1: string,
  color2: string,
  level: 'AA' | 'AAA' = 'AA',
  size: 'normal' | 'large' = 'normal'
): boolean {
  const ratio = getContrastRatio(color1, color2)

  const requirements = {
    AA: { normal: 4.5, large: 3 },
    AAA: { normal: 7, large: 4.5 },
  }

  return ratio >= requirements[level][size]
}
