/**
 * Performance Optimization Utilities
 * 
 * Helper functions for debouncing, throttling, and lazy loading
 */

import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Debounce function - delays execution until after wait time
 * 
 * @example
 * ```ts
 * const debouncedSearch = debounce((query: string) => {
 *   fetchResults(query)
 * }, 500)
 * ```
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  return function debounced(...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

/**
 * Throttle function - limits execution to once per wait time
 * 
 * @example
 * ```ts
 * const throttledScroll = throttle(() => {
 *   handleScroll()
 * }, 100)
 * ```
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  let lastRan: number = 0

  return function throttled(...args: Parameters<T>) {
    const now = Date.now()

    if (!lastRan || now - lastRan >= wait) {
      func(...args)
      lastRan = now
    } else {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }

      timeoutId = setTimeout(() => {
        func(...args)
        lastRan = Date.now()
      }, wait - (now - lastRan))
    }
  }
}

/**
 * React hook for debounced value
 * 
 * @example
 * ```tsx
 * const [search, setSearch] = useState('')
 * const debouncedSearch = useDebounce(search, 500)
 * 
 * useEffect(() => {
 *   // This only runs 500ms after user stops typing
 *   fetchResults(debouncedSearch)
 * }, [debouncedSearch])
 * ```
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * React hook for throttled callback
 * 
 * @example
 * ```tsx
 * const handleScroll = useThrottle(() => {
 *   console.log('Scrolled!')
 * }, 100)
 * 
 * <div onScroll={handleScroll}>...</div>
 * ```
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const callbackRef = useRef(callback)
  const lastRan = useRef(Date.now())

  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now()

      if (now - lastRan.current >= delay) {
        callbackRef.current(...args)
        lastRan.current = now
      }
    },
    [delay]
  )
}

/**
 * Hook for lazy loading with Intersection Observer
 * 
 * @example
 * ```tsx
 * const { ref, isVisible } = useLazyLoad()
 * 
 * return (
 *   <div ref={ref}>
 *     {isVisible && <ExpensiveComponent />}
 *   </div>
 * )
 * ```
 */
export function useLazyLoad<T extends HTMLElement = HTMLDivElement>(
  options: IntersectionObserverInit = {}
) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<T>(null)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      {
        threshold: 0.1,
        ...options,
      }
    )

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [options])

  return { ref, isVisible }
}

/**
 * Hook for detecting idle state
 * 
 * @example
 * ```tsx
 * const isIdle = useIdle(5000) // 5 seconds of inactivity
 * 
 * if (isIdle) {
 *   // User is idle, maybe pause expensive operations
 * }
 * ```
 */
export function useIdle(timeout: number = 60000): boolean {
  const [isIdle, setIsIdle] = useState(false)

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>

    const handleActivity = () => {
      setIsIdle(false)
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => setIsIdle(true), timeout)
    }

    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']

    events.forEach((event) => {
      document.addEventListener(event, handleActivity)
    })

    timeoutId = setTimeout(() => setIsIdle(true), timeout)

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity)
      })
      clearTimeout(timeoutId)
    }
  }, [timeout])

  return isIdle
}

/**
 * Hook for measuring render performance
 * 
 * @example
 * ```tsx
 * const renderTime = useRenderTime('MyComponent')
 * console.log(`Rendered in ${renderTime}ms`)
 * ```
 */
export function useRenderTime(componentName: string): number | null {
  const [renderTime, setRenderTime] = useState<number | null>(null)
  const startTimeRef = useRef<number>(performance.now())

  useEffect(() => {
    const endTime = performance.now()
    const duration = endTime - startTimeRef.current
    setRenderTime(duration)

    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${componentName} rendered in ${duration.toFixed(2)}ms`)
    }

    // Reset for next render
    startTimeRef.current = performance.now()
  })

  return renderTime
}

/**
 * Memoize expensive computations
 * 
 * @example
 * ```ts
 * const fibonacci = memoize((n: number): number => {
 *   if (n <= 1) return n
 *   return fibonacci(n - 1) + fibonacci(n - 2)
 * })
 * ```
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T
): T {
  const cache = new Map<string, ReturnType<T>>()

  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args)

    if (cache.has(key)) {
      return cache.get(key)!
    }

    const result = fn(...args)
    cache.set(key, result)

    return result
  }) as T
}

/**
 * Batch multiple state updates together
 * 
 * @example
 * ```tsx
 * const [updates, batchUpdate] = useBatchUpdate()
 * 
 * batchUpdate(() => {
 *   setName('John')
 *   setAge(30)
 *   setEmail('john@example.com')
 * })
 * ```
 */
export function useBatchUpdate() {
  const [updateCount, setUpdateCount] = useState(0)

  const batchUpdate = useCallback((callback: () => void) => {
    // React 18 automatically batches updates
    callback()
    setUpdateCount((c) => c + 1)
  }, [])

  return [updateCount, batchUpdate] as const
}

/**
 * Measure Web Vitals
 */
export interface WebVitals {
  CLS?: number // Cumulative Layout Shift
  FID?: number // First Input Delay
  FCP?: number // First Contentful Paint
  LCP?: number // Largest Contentful Paint
  TTFB?: number // Time to First Byte
}

export function reportWebVitals(onPerfEntry?: (metric: WebVitals) => void) {
  if (onPerfEntry && typeof window !== 'undefined') {
    // TODO: Install web-vitals package to enable this functionality
    // import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
    //   getCLS(metric => onPerfEntry({ CLS: metric.value }))
    //   getFID(metric => onPerfEntry({ FID: metric.value }))
    //   getFCP(metric => onPerfEntry({ FCP: metric.value }))
    //   getLCP(metric => onPerfEntry({ LCP: metric.value }))
    //   getTTFB(metric => onPerfEntry({ TTFB: metric.value }))
    // }).catch(() => {
    //   // web-vitals not available
    // })
    console.warn('Web Vitals reporting is currently disabled. Install web-vitals package to enable.')
  }
}
