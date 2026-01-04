import { cn } from '@/lib/utils'

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Variant of the skeleton
   * - text: For text content
   * - circular: For avatars/icons
   * - rectangular: For images/cards (default)
   */
  variant?: 'text' | 'circular' | 'rectangular'
  
  /**
   * Width of the skeleton (CSS value)
   */
  width?: string | number
  
  /**
   * Height of the skeleton (CSS value)
   */
  height?: string | number
  
  /**
   * Animation type
   */
  animation?: 'pulse' | 'wave' | 'none'
}

/**
 * Skeleton Component
 * 
 * Loading placeholder that mimics the shape of content.
 * Provides visual feedback during data fetching.
 * 
 * @example
 * ```tsx
 * <Skeleton variant="text" width="200px" height="20px" />
 * <Skeleton variant="circular" width="40px" height="40px" />
 * <Skeleton width="100%" height="200px" />
 * ```
 */
export function Skeleton({
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
  className,
  style,
  ...props
}: SkeletonProps) {
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  }

  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-wave',
    none: '',
  }

  return (
    <div
      className={cn(
        'bg-gray-200 dark:bg-gray-700',
        variantClasses[variant],
        animationClasses[animation],
        className
      )}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        ...style,
      }}
      {...props}
    />
  )
}

/**
 * Card Skeleton
 * 
 * Pre-built skeleton for card-like content
 */
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-3 p-4 border rounded-lg', className)}>
      <Skeleton height="20px" width="60%" />
      <Skeleton height="16px" width="100%" />
      <Skeleton height="16px" width="80%" />
      <div className="flex gap-2 mt-4">
        <Skeleton height="32px" width="80px" />
        <Skeleton height="32px" width="80px" />
      </div>
    </div>
  )
}

/**
 * List Skeleton
 * 
 * Pre-built skeleton for list items
 */
export function ListSkeleton({ 
  count = 3,
  className 
}: { 
  count?: number
  className?: string 
}) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton variant="circular" width="40px" height="40px" />
          <div className="flex-1 space-y-2">
            <Skeleton height="16px" width="60%" />
            <Skeleton height="14px" width="40%" />
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * Table Skeleton
 * 
 * Pre-built skeleton for table content
 */
export function TableSkeleton({
  rows = 5,
  columns = 4,
  className
}: {
  rows?: number
  columns?: number
  className?: string
}) {
  return (
    <div className={cn('space-y-2', className)}>
      {/* Header */}
      <div className="flex gap-4 border-b pb-2">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} height="20px" className="flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 py-3">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} height="16px" className="flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}
