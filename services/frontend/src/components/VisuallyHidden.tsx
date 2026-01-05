import { ReactNode } from 'react'

interface VisuallyHiddenProps {
  children: ReactNode
  /**
   * Whether to use display: none when focusable
   */
  focusable?: boolean
}

/**
 * VisuallyHidden Component
 * 
 * Hides content visually but keeps it accessible to screen readers.
 * Useful for adding context that's only needed for assistive technologies.
 * 
 * @example
 * ```tsx
 * <button>
 *   <Icon />
 *   <VisuallyHidden>Delete item</VisuallyHidden>
 * </button>
 * ```
 */
export function VisuallyHidden({ children, focusable = false }: VisuallyHiddenProps) {
  if (focusable) {
    return (
      <span
        className="sr-only-focusable"
        style={{
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: '0',
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          borderWidth: '0',
        }}
      >
        {children}
      </span>
    )
  }

  return (
    <span className="sr-only">
      {children}
    </span>
  )
}

/**
 * Add to your global CSS:
 * 
 * .sr-only {
 *   position: absolute;
 *   width: 1px;
 *   height: 1px;
 *   padding: 0;
 *   margin: -1px;
 *   overflow: hidden;
 *   clip: rect(0, 0, 0, 0);
 *   white-space: nowrap;
 *   border-width: 0;
 * }
 * 
 * .sr-only-focusable:focus,
 * .sr-only-focusable:active {
 *   position: static;
 *   width: auto;
 *   height: auto;
 *   overflow: visible;
 *   clip: auto;
 *   white-space: normal;
 * }
 */
