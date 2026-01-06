/* eslint-env serviceworker */
/**
 * Service Worker for Progressive Web App
 * 
 * Provides offline support, caching strategies, and background sync
 */

const CACHE_NAME = 'monkey-coder-v1'
const RUNTIME_CACHE = 'runtime-cache-v1'

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/offline',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
]

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS)
    })
  )
  
  // Activate immediately
  self.skipWaiting()
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
          .map((name) => caches.delete(name))
      )
    })
  )
  
  // Claim all clients immediately
  self.clients.claim()
})

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return
  }
  
  // API requests - network first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request))
    return
  }
  
  // Static assets - cache first, network fallback
  if (
    request.destination === 'script' ||
    request.destination === 'style' ||
    request.destination === 'image' ||
    request.destination === 'font'
  ) {
    event.respondWith(cacheFirst(request))
    return
  }
  
  // HTML pages - network first, cache fallback
  if (request.destination === 'document') {
    event.respondWith(networkFirst(request))
    return
  }
  
  // Default: network first
  event.respondWith(networkFirst(request))
})

/**
 * Cache First Strategy
 * Serve from cache, fallback to network, then cache the response
 */
async function cacheFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE)
  const cached = await cache.match(request)
  
  if (cached) {
    return cached
  }
  
  try {
    const response = await fetch(request)
    
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return caches.match('/offline')
    }
    
    throw error
  }
}

/**
 * Network First Strategy
 * Try network, fallback to cache
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request)
    
    // Cache successful responses
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE)
      cache.put(request, response.clone())
    }
    
    return response
  } catch (error) {
    // Try cache
    const cache = await caches.open(RUNTIME_CACHE)
    const cached = await cache.match(request)
    
    if (cached) {
      return cached
    }
    
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return caches.match('/offline')
    }
    
    throw error
  }
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData())
  }
})

async function syncData() {
  // Implement your data sync logic here
  console.log('Background sync triggered')
}

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {}
  
  const options = {
    body: data.body || 'New notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    data: data.url,
    actions: [
      {
        action: 'open',
        title: 'Open',
      },
      {
        action: 'close',
        title: 'Close',
      },
    ],
  }
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'Monkey Coder', options)
  )
})

// Notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  
  if (event.action === 'open' || !event.action) {
    const url = event.notification.data || '/'
    
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // Focus existing window if available
        for (const client of clientList) {
          if (client.url === url && 'focus' in client) {
            return client.focus()
          }
        }
        
        // Open new window
        if (clients.openWindow) {
          return clients.openWindow(url)
        }
      })
    )
  }
})
