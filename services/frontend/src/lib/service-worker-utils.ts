/**
 * Service Worker Registration Utility
 * 
 * Registers and manages the service worker for PWA functionality
 */

export interface ServiceWorkerConfig {
  /**
   * Path to the service worker file
   */
  swPath?: string
  
  /**
   * Scope for the service worker
   */
  scope?: string
  
  /**
   * Callback when SW is registered
   */
  onSuccess?: (registration: ServiceWorkerRegistration) => void
  
  /**
   * Callback when SW update is available
   */
  onUpdate?: (registration: ServiceWorkerRegistration) => void
  
  /**
   * Callback on error
   */
  onError?: (error: Error) => void
}

/**
 * Register service worker
 * 
 * @example
 * ```ts
 * // In your app initialization (e.g., _app.tsx or layout.tsx)
 * useEffect(() => {
 *   registerServiceWorker({
 *     onSuccess: () => console.log('SW registered'),
 *     onUpdate: () => console.log('SW update available'),
 *   })
 * }, [])
 * ```
 */
export function registerServiceWorker(config: ServiceWorkerConfig = {}): void {
  const {
    swPath = '/service-worker.js',
    scope = '/',
    onSuccess,
    onUpdate,
    onError,
  } = config
  
  // Check if service workers are supported
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    console.warn('Service workers are not supported in this browser')
    return
  }
  
  // Only register in production or when explicitly enabled
  if (process.env.NODE_ENV !== 'production' && !process.env.NEXT_PUBLIC_ENABLE_SW) {
    console.log('Service worker disabled in development')
    return
  }
  
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register(swPath, { scope })
      
      console.log('Service Worker registered:', registration)
      
      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing
        
        if (!newWorker) return
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New service worker available
            console.log('New service worker available')
            onUpdate?.(registration)
          }
        })
      })
      
      onSuccess?.(registration)
    } catch (error) {
      console.error('Service Worker registration failed:', error)
      onError?.(error as Error)
    }
  })
}

/**
 * Unregister service worker
 */
export async function unregisterServiceWorker(): Promise<boolean> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return false
  }
  
  const registration = await navigator.serviceWorker.getRegistration()
  
  if (registration) {
    return await registration.unregister()
  }
  
  return false
}

/**
 * Update service worker
 * 
 * Forces an update check for the service worker
 */
export async function updateServiceWorker(): Promise<void> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return
  }
  
  const registration = await navigator.serviceWorker.getRegistration()
  
  if (registration) {
    await registration.update()
  }
}

/**
 * Skip waiting and activate new service worker immediately
 */
export function skipWaiting(): void {
  if (typeof window === 'undefined' || !navigator.serviceWorker.controller) {
    return
  }
  
  navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' })
}

/**
 * Request persistent storage permission
 */
export async function requestPersistentStorage(): Promise<boolean> {
  if (typeof window === 'undefined' || !navigator.storage || !navigator.storage.persist) {
    return false
  }
  
  const isPersisted = await navigator.storage.persisted()
  
  if (isPersisted) {
    return true
  }
  
  return await navigator.storage.persist()
}

/**
 * Get storage estimate
 */
export async function getStorageEstimate(): Promise<{
  usage: number
  quota: number
  usagePercent: number
} | null> {
  if (typeof window === 'undefined' || !navigator.storage || !navigator.storage.estimate) {
    return null
  }
  
  const estimate = await navigator.storage.estimate()
  
  return {
    usage: estimate.usage || 0,
    quota: estimate.quota || 0,
    usagePercent: estimate.quota ? ((estimate.usage || 0) / estimate.quota) * 100 : 0,
  }
}

/**
 * Show update notification
 * 
 * Helper to show a notification when a service worker update is available
 */
export function showUpdateNotification(callback?: () => void): void {
  const message = 'A new version is available!'
  const action = 'Update'
  
  // Create a simple notification
  if (typeof window !== 'undefined' && window.confirm(`${message}\n\nClick OK to ${action.toLowerCase()}.`)) {
    callback?.()
    window.location.reload()
  }
}

/**
 * Hook for React components to use service worker
 */
export function useServiceWorker(config: ServiceWorkerConfig = {}) {
  if (typeof window === 'undefined') {
    return {
      isSupported: false,
      isRegistered: false,
      updateAvailable: false,
    }
  }
  
  const [isSupported] = React.useState('serviceWorker' in navigator)
  const [isRegistered, setIsRegistered] = React.useState(false)
  const [updateAvailable, setUpdateAvailable] = React.useState(false)
  
  React.useEffect(() => {
    if (!isSupported) return
    
    registerServiceWorker({
      ...config,
      onSuccess: (registration) => {
        setIsRegistered(true)
        config.onSuccess?.(registration)
      },
      onUpdate: (registration) => {
        setUpdateAvailable(true)
        config.onUpdate?.(registration)
      },
    })
  }, [isSupported])
  
  return {
    isSupported,
    isRegistered,
    updateAvailable,
    update: updateServiceWorker,
    skipWaiting,
  }
}

// Note: Import React at the top if using the hook
import React from 'react'
