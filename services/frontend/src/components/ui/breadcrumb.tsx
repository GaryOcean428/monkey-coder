import { ReactNode } from 'react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: ReactNode
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[]
  separator?: ReactNode
  className?: string
}

/**
 * Breadcrumb Component
 * 
 * Navigation breadcrumbs for deep page hierarchies
 * 
 * @example
 * ```tsx
 * <Breadcrumb
 *   items={[
 *     { label: 'Home', href: '/' },
 *     { label: 'Projects', href: '/projects' },
 *     { label: 'Project Name' }
 *   ]}
 * />
 * ```
 */
export function Breadcrumb({ 
  items, 
  separator = '/', 
  className 
}: BreadcrumbProps) {
  if (items.length === 0) return null

  return (
    <nav
      aria-label="Breadcrumb"
      className={cn('flex items-center space-x-2 text-sm', className)}
    >
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => {
          const isLast = index === items.length - 1

          return (
            <li
              key={`${item.label}-${index}`}
              className="flex items-center space-x-2"
            >
              {/* Item */}
              {item.href && !isLast ? (
                <Link
                  href={item.href}
                  className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
                >
                  {item.icon && <span className="w-4 h-4">{item.icon}</span>}
                  <span>{item.label}</span>
                </Link>
              ) : (
                <span
                  className={cn(
                    'flex items-center space-x-1',
                    isLast
                      ? 'text-gray-900 dark:text-gray-100 font-medium'
                      : 'text-gray-600 dark:text-gray-400'
                  )}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {item.icon && <span className="w-4 h-4">{item.icon}</span>}
                  <span>{item.label}</span>
                </span>
              )}

              {/* Separator */}
              {!isLast && (
                <span
                  className="text-gray-400 dark:text-gray-600"
                  aria-hidden="true"
                >
                  {separator}
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

/**
 * Generate breadcrumb items from pathname
 * 
 * @example
 * ```tsx
 * const pathname = '/projects/123/settings'
 * const items = generateBreadcrumbs(pathname, {
 *   projects: 'Projects',
 *   settings: 'Settings'
 * })
 * ```
 */
export function generateBreadcrumbs(
  pathname: string,
  labels: Record<string, string> = {}
): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean)

  return [
    { label: 'Home', href: '/' },
    ...segments.map((segment, index) => {
      const href = '/' + segments.slice(0, index + 1).join('/')
      const label = labels[segment] || segment.charAt(0).toUpperCase() + segment.slice(1)

      return {
        label,
        href: index < segments.length - 1 ? href : undefined,
      }
    }),
  ]
}
