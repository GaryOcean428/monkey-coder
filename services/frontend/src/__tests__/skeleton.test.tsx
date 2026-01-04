/**
 * @jest-environment jsdom
 */

import { describe, it, expect } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import { Skeleton, CardSkeleton, ListSkeleton, TableSkeleton } from '@/components/ui/skeleton'

describe('Skeleton Component', () => {
  it('should render with default variant', () => {
    const { container } = render(<Skeleton />)
    
    expect(container.firstChild).toHaveClass('rounded-md')
    expect(container.firstChild).toHaveClass('animate-pulse')
  })

  it('should render with text variant', () => {
    const { container } = render(<Skeleton variant="text" />)
    
    expect(container.firstChild).toHaveClass('rounded')
  })

  it('should render with circular variant', () => {
    const { container } = render(<Skeleton variant="circular" />)
    
    expect(container.firstChild).toHaveClass('rounded-full')
  })

  it('should apply custom width and height', () => {
    const { container } = render(
      <Skeleton width="100px" height="50px" />
    )
    
    const element = container.firstChild as HTMLElement
    expect(element.style.width).toBe('100px')
    expect(element.style.height).toBe('50px')
  })

  it('should apply numeric width and height', () => {
    const { container } = render(
      <Skeleton width={100} height={50} />
    )
    
    const element = container.firstChild as HTMLElement
    expect(element.style.width).toBe('100px')
    expect(element.style.height).toBe('50px')
  })

  it('should use wave animation when specified', () => {
    const { container } = render(<Skeleton animation="wave" />)
    
    expect(container.firstChild).toHaveClass('animate-wave')
  })

  it('should have no animation when specified', () => {
    const { container } = render(<Skeleton animation="none" />)
    
    expect(container.firstChild).not.toHaveClass('animate-pulse')
    expect(container.firstChild).not.toHaveClass('animate-wave')
  })
})

describe('CardSkeleton Component', () => {
  it('should render card skeleton structure', () => {
    const { container } = render(<CardSkeleton />)
    
    // Should have border and padding
    expect(container.firstChild).toHaveClass('border')
    expect(container.firstChild).toHaveClass('p-4')
    
    // Should have multiple skeleton elements
    const skeletons = container.querySelectorAll('div[class*="bg-gray"]')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('should apply custom className', () => {
    const { container } = render(<CardSkeleton className="custom-class" />)
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
})

describe('ListSkeleton Component', () => {
  it('should render default number of items', () => {
    const { container } = render(<ListSkeleton />)
    
    // Default is 3 items
    const items = container.querySelectorAll('.flex.items-center')
    expect(items.length).toBe(3)
  })

  it('should render custom number of items', () => {
    const { container } = render(<ListSkeleton count={5} />)
    
    const items = container.querySelectorAll('.flex.items-center')
    expect(items.length).toBe(5)
  })

  it('should have circular avatars', () => {
    const { container } = render(<ListSkeleton />)
    
    const circularElements = container.querySelectorAll('[class*="rounded-full"]')
    expect(circularElements.length).toBeGreaterThan(0)
  })
})

describe('TableSkeleton Component', () => {
  it('should render default number of rows and columns', () => {
    const { container } = render(<TableSkeleton />)
    
    // Default is 5 rows (plus header)
    const rows = container.querySelectorAll('.flex.gap-4.py-3')
    expect(rows.length).toBe(5)
  })

  it('should render custom number of rows', () => {
    const { container } = render(<TableSkeleton rows={3} />)
    
    const rows = container.querySelectorAll('.flex.gap-4.py-3')
    expect(rows.length).toBe(3)
  })

  it('should render header row', () => {
    const { container } = render(<TableSkeleton />)
    
    const header = container.querySelector('.border-b')
    expect(header).toBeInTheDocument()
  })
})
