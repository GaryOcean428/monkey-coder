import { ReactNode } from 'react'
import { Button } from './button'
import { cn } from '@/lib/utils'

interface EmptyStateProps {
  /**
   * Title of the empty state
   */
  title: string
  
  /**
   * Description or additional context
   */
  description?: string
  
  /**
   * Icon or illustration to display
   */
  icon?: ReactNode
  
  /**
   * Primary action button
   */
  action?: {
    label: string
    onClick: () => void
  }
  
  /**
   * Secondary action button
   */
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Empty State Component
 * 
 * Displays when there's no content to show. Provides clear messaging
 * and actionable next steps for users.
 * 
 * @example
 * ```tsx
 * <EmptyState
 *   title="No projects yet"
 *   description="Get started by creating your first project"
 *   icon={<FolderIcon className="w-12 h-12" />}
 *   action={{
 *     label: "Create Project",
 *     onClick: () => router.push('/projects/new')
 *   }}
 * />
 * ```
 */
export function EmptyState({
  title,
  description,
  icon,
  action,
  secondaryAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center p-8 space-y-4',
        'min-h-[400px]',
        className
      )}
    >
      {/* Icon/Illustration */}
      {icon && (
        <div className="text-gray-400 dark:text-gray-600">
          {icon}
        </div>
      )}
      
      {/* Title */}
      <div className="space-y-2">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          {title}
        </h3>
        
        {/* Description */}
        {description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 max-w-sm">
            {description}
          </p>
        )}
      </div>
      
      {/* Actions */}
      {(action || secondaryAction) && (
        <div className="flex gap-3 pt-2">
          {action && (
            <Button onClick={action.onClick}>
              {action.label}
            </Button>
          )}
          
          {secondaryAction && (
            <Button
              variant="outline"
              onClick={secondaryAction.onClick}
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * Common empty state icons using SVG
 */
export const EmptyStateIcons = {
  Folder: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
      />
    </svg>
  ),
  
  Document: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
      />
    </svg>
  ),
  
  Search: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
  ),
  
  Inbox: (
    <svg
      className="w-16 h-16"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
      />
    </svg>
  ),
}
