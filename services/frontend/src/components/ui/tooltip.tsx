'use client'

import { ReactNode, useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { createPortal } from 'react-dom'

export interface TooltipProps {
  children: ReactNode
  content: ReactNode
  side?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
  className?: string
}

/**
 * Tooltip Component
 * 
 * Contextual information on hover/focus
 * 
 * @example
 * ```tsx
 * <Tooltip content="This is a helpful tip">
 *   <button>Hover me</button>
 * </Tooltip>
 * ```
 */
export function Tooltip({ 
  children, 
  content, 
  side = 'top',
  delay = 200,
  className 
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const triggerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const timeoutRef = useRef<NodeJS.Timeout>()

  const showTooltip = () => {
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)
    }, delay)
  }

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setIsVisible(false)
  }

  // Calculate position
  useEffect(() => {
    if (!isVisible || !triggerRef.current || !tooltipRef.current) return

    const trigger = triggerRef.current.getBoundingClientRect()
    const tooltip = tooltipRef.current.getBoundingClientRect()

    let top = 0
    let left = 0

    switch (side) {
      case 'top':
        top = trigger.top - tooltip.height - 8
        left = trigger.left + (trigger.width - tooltip.width) / 2
        break
      case 'bottom':
        top = trigger.bottom + 8
        left = trigger.left + (trigger.width - tooltip.width) / 2
        break
      case 'left':
        top = trigger.top + (trigger.height - tooltip.height) / 2
        left = trigger.left - tooltip.width - 8
        break
      case 'right':
        top = trigger.top + (trigger.height - tooltip.height) / 2
        left = trigger.right + 8
        break
    }

    // Keep tooltip in viewport
    const padding = 8
    top = Math.max(padding, Math.min(top, window.innerHeight - tooltip.height - padding))
    left = Math.max(padding, Math.min(left, window.innerWidth - tooltip.width - padding))

    setPosition({ top, left })
  }, [isVisible, side])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        className="inline-block"
      >
        {children}
      </div>

      {isVisible && typeof document !== 'undefined' && createPortal(
        <div
          ref={tooltipRef}
          role="tooltip"
          className={cn(
            'fixed z-50 px-3 py-2 text-sm text-white bg-gray-900 dark:bg-gray-700 rounded-md shadow-lg pointer-events-none',
            'animate-in fade-in-0 zoom-in-95',
            className
          )}
          style={{
            top: `${position.top}px`,
            left: `${position.left}px`,
          }}
        >
          {content}
          
          {/* Arrow */}
          <div
            className={cn(
              'absolute w-2 h-2 bg-gray-900 dark:bg-gray-700 transform rotate-45',
              {
                'top-full left-1/2 -translate-x-1/2 -mt-1': side === 'top',
                'bottom-full left-1/2 -translate-x-1/2 -mb-1': side === 'bottom',
                'top-1/2 left-full -translate-y-1/2 -ml-1': side === 'left',
                'top-1/2 right-full -translate-y-1/2 -mr-1': side === 'right',
              }
            )}
          />
        </div>,
        document.body
      )}
    </>
  )
}

/**
 * Simple Tooltip with title attribute
 * Use for basic tooltips without portal rendering
 */
export function SimpleTooltip({ 
  children, 
  title 
}: { 
  children: ReactNode
  title: string 
}) {
  return (
    <div title={title} className="inline-block">
      {children}
    </div>
  )
}
