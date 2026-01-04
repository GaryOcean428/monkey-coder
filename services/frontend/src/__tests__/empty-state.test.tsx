/**
 * @jest-environment jsdom
 */

import { describe, it, expect } from '@jest/globals'
import { render, screen } from '@testing-library/react'
import { EmptyState, EmptyStateIcons } from '@/components/ui/empty-state'

describe('EmptyState Component', () => {
  it('should render title', () => {
    render(<EmptyState title="No results found" />)
    
    expect(screen.getByText('No results found')).toBeInTheDocument()
  })

  it('should render description when provided', () => {
    render(
      <EmptyState 
        title="No projects" 
        description="Get started by creating your first project"
      />
    )
    
    expect(screen.getByText('Get started by creating your first project')).toBeInTheDocument()
  })

  it('should render icon when provided', () => {
    render(
      <EmptyState 
        title="Empty"
        icon={<div data-testid="custom-icon">Icon</div>}
      />
    )
    
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
  })

  it('should render primary action button', () => {
    const mockAction = jest.fn()
    
    render(
      <EmptyState 
        title="No data"
        action={{ label: 'Add Data', onClick: mockAction }}
      />
    )
    
    const button = screen.getByRole('button', { name: 'Add Data' })
    expect(button).toBeInTheDocument()
    
    button.click()
    expect(mockAction).toHaveBeenCalledTimes(1)
  })

  it('should render both primary and secondary actions', () => {
    const mockPrimary = jest.fn()
    const mockSecondary = jest.fn()
    
    render(
      <EmptyState 
        title="Empty"
        action={{ label: 'Primary', onClick: mockPrimary }}
        secondaryAction={{ label: 'Secondary', onClick: mockSecondary }}
      />
    )
    
    expect(screen.getByRole('button', { name: 'Primary' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Secondary' })).toBeInTheDocument()
  })

  it('should apply custom className', () => {
    const { container } = render(
      <EmptyState 
        title="Test"
        className="custom-class"
      />
    )
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
})

describe('EmptyStateIcons', () => {
  it('should provide common icons', () => {
    expect(EmptyStateIcons.Folder).toBeDefined()
    expect(EmptyStateIcons.Document).toBeDefined()
    expect(EmptyStateIcons.Search).toBeDefined()
    expect(EmptyStateIcons.Inbox).toBeDefined()
  })
})
