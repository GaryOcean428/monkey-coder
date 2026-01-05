/**
 * @jest-environment jsdom
 */

import { describe, it, expect } from '@jest/globals'
import { renderHook, act, waitFor } from '@testing-library/react'
import { 
  useDebounce, 
  useThrottle,
  useLazyLoad,
  useIdle,
  debounce,
  throttle,
  memoize
} from '@/lib/performance'

describe('Performance Utilities', () => {
  describe('debounce', () => {
    jest.useFakeTimers()

    it('should delay function execution', () => {
      const fn = jest.fn()
      const debouncedFn = debounce(fn, 500)

      debouncedFn()
      expect(fn).not.toHaveBeenCalled()

      jest.advanceTimersByTime(500)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should cancel previous calls', () => {
      const fn = jest.fn()
      const debouncedFn = debounce(fn, 500)

      debouncedFn()
      debouncedFn()
      debouncedFn()

      jest.advanceTimersByTime(500)
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })

  describe('throttle', () => {
    jest.useFakeTimers()

    it('should limit function execution', () => {
      const fn = jest.fn()
      const throttledFn = throttle(fn, 1000)

      throttledFn()
      throttledFn()
      throttledFn()

      expect(fn).toHaveBeenCalledTimes(1)

      jest.advanceTimersByTime(1000)
      throttledFn()
      expect(fn).toHaveBeenCalledTimes(2)
    })
  })

  describe('useDebounce', () => {
    jest.useFakeTimers()

    it('should debounce value changes', () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 500 } }
      )

      expect(result.current).toBe('initial')

      rerender({ value: 'updated', delay: 500 })
      expect(result.current).toBe('initial')

      act(() => {
        jest.advanceTimersByTime(500)
      })

      expect(result.current).toBe('updated')
    })
  })

  describe('memoize', () => {
    it('should cache function results', () => {
      const expensiveFn = jest.fn((n: number) => n * 2)
      const memoized = memoize(expensiveFn)

      expect(memoized(5)).toBe(10)
      expect(memoized(5)).toBe(10)
      expect(expensiveFn).toHaveBeenCalledTimes(1)

      expect(memoized(10)).toBe(20)
      expect(expensiveFn).toHaveBeenCalledTimes(2)
    })

    it('should handle multiple arguments', () => {
      const fn = jest.fn((a: number, b: number) => a + b)
      const memoized = memoize(fn)

      expect(memoized(1, 2)).toBe(3)
      expect(memoized(1, 2)).toBe(3)
      expect(fn).toHaveBeenCalledTimes(1)

      expect(memoized(2, 3)).toBe(5)
      expect(fn).toHaveBeenCalledTimes(2)
    })
  })

  describe('useIdle', () => {
    jest.useFakeTimers()

    it('should detect idle state', () => {
      const { result } = renderHook(() => useIdle(1000))

      expect(result.current).toBe(false)

      act(() => {
        jest.advanceTimersByTime(1000)
      })

      expect(result.current).toBe(true)
    })
  })
})
