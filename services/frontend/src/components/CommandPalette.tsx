'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from './ui/input'
import { cn } from '@/lib/utils'

export interface CommandItem {
  id: string
  label: string
  description?: string
  icon?: React.ReactNode
  keywords?: string[]
  onSelect: () => void
  shortcut?: string
}

export interface CommandPaletteProps {
  items: CommandItem[]
  placeholder?: string
  onClose?: () => void
}

/**
 * Command Palette Component (CMD+K / CTRL+K)
 * 
 * Quick actions menu for power users
 * 
 * @example
 * ```tsx
 * const commands: CommandItem[] = [
 *   {
 *     id: 'new-project',
 *     label: 'New Project',
 *     description: 'Create a new project',
 *     onSelect: () => router.push('/projects/new')
 *   }
 * ]
 * 
 * <CommandPalette items={commands} />
 * ```
 */
export function CommandPalette({ items, placeholder = 'Type a command...', onClose }: CommandPaletteProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  // Filter items based on search
  const filteredItems = items.filter(item => {
    const searchLower = search.toLowerCase()
    return (
      item.label.toLowerCase().includes(searchLower) ||
      item.description?.toLowerCase().includes(searchLower) ||
      item.keywords?.some(k => k.toLowerCase().includes(searchLower))
    )
  })

  // Open/close handlers
  const handleOpen = useCallback(() => {
    setIsOpen(true)
    setSearch('')
    setSelectedIndex(0)
    setTimeout(() => inputRef.current?.focus(), 100)
  }, [])

  const handleClose = useCallback(() => {
    setIsOpen(false)
    onClose?.()
  }, [onClose])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // CMD+K / CTRL+K to open
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        handleOpen()
        return
      }

      if (!isOpen) return

      // ESC to close
      if (e.key === 'Escape') {
        e.preventDefault()
        handleClose()
        return
      }

      // Arrow navigation
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(prev => (prev + 1) % filteredItems.length)
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(prev => (prev - 1 + filteredItems.length) % filteredItems.length)
      }

      // Enter to select
      if (e.key === 'Enter' && filteredItems[selectedIndex]) {
        e.preventDefault()
        filteredItems[selectedIndex].onSelect()
        handleClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredItems, selectedIndex, handleOpen, handleClose])

  // Click outside to close
  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('[data-command-palette]')) {
        handleClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, handleClose])

  if (!isOpen) {
    return (
      <button
        onClick={handleOpen}
        className="fixed bottom-4 right-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg shadow-lg hover:shadow-xl transition-shadow z-50"
        aria-label="Open command palette"
      >
        <kbd className="font-mono text-xs">⌘K</kbd>
      </button>
    )
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-start justify-center pt-20">
      <div
        data-command-palette
        className="w-full max-w-2xl bg-white dark:bg-gray-800 rounded-lg shadow-2xl overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
      >
        {/* Search Input */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-4">
          <Input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setSelectedIndex(0)
            }}
            placeholder={placeholder}
            className="w-full text-lg border-0 focus:ring-0"
            autoComplete="off"
            role="combobox"
            aria-expanded="true"
            aria-controls="command-list"
            aria-activedescendant={filteredItems[selectedIndex]?.id}
          />
        </div>

        {/* Results List */}
        <div
          id="command-list"
          role="listbox"
          className="max-h-96 overflow-y-auto p-2"
        >
          {filteredItems.length === 0 ? (
            <div className="py-8 text-center text-gray-500">
              No results found
            </div>
          ) : (
            filteredItems.map((item, index) => (
              <button
                key={item.id}
                id={item.id}
                role="option"
                aria-selected={index === selectedIndex}
                onClick={() => {
                  item.onSelect()
                  handleClose()
                }}
                onMouseEnter={() => setSelectedIndex(index)}
                className={cn(
                  'w-full text-left px-4 py-3 rounded-md flex items-center gap-3 transition-colors',
                  index === selectedIndex
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                )}
              >
                {/* Icon */}
                {item.icon && (
                  <span className="flex-shrink-0 w-5 h-5">
                    {item.icon}
                  </span>
                )}

                {/* Label & Description */}
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{item.label}</div>
                  {item.description && (
                    <div className="text-sm opacity-70 truncate">
                      {item.description}
                    </div>
                  )}
                </div>

                {/* Shortcut */}
                {item.shortcut && (
                  <kbd className="flex-shrink-0 px-2 py-1 text-xs font-mono bg-gray-200 dark:bg-gray-600 rounded">
                    {item.shortcut}
                  </kbd>
                )}
              </button>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-2 text-xs text-gray-500 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span>
              <kbd className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">↑↓</kbd> Navigate
            </span>
            <span>
              <kbd className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">Enter</kbd> Select
            </span>
            <span>
              <kbd className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">Esc</kbd> Close
            </span>
          </div>
          <span>{filteredItems.length} results</span>
        </div>
      </div>
    </div>
  )
}

/**
 * Hook to use command palette
 */
export function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false)

  const open = useCallback(() => setIsOpen(true), [])
  const close = useCallback(() => setIsOpen(false), [])
  const toggle = useCallback(() => setIsOpen(prev => !prev), [])

  return { isOpen, open, close, toggle }
}
