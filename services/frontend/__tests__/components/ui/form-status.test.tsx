import { render, screen } from '@testing-library/react'
import { FormStatus, useFormStatus } from '../../../src/components/ui/form-status'
import { renderHook, act } from '@testing-library/react'

describe('FormStatus Component', () => {
  it('does not render when status is idle', () => {
    render(<FormStatus status="idle" />)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('renders submitting state correctly', () => {
    render(<FormStatus status="submitting" message="Processing..." />)
    
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByText('Processing...')).toBeInTheDocument()
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
  })

  it('renders success state correctly', () => {
    render(<FormStatus status="success" message="Success!" />)
    
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByText('Success!')).toBeInTheDocument()
    expect(screen.getByTestId('success-icon')).toBeInTheDocument()
  })

  it('renders error state correctly', () => {
    render(<FormStatus status="error" message="Error occurred" />)
    
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByText('Error occurred')).toBeInTheDocument()
    expect(screen.getByTestId('error-icon')).toBeInTheDocument()
  })

  it('shows default message when no message provided', () => {
    render(<FormStatus status="submitting" />)
    expect(screen.getByText('Processing your request...')).toBeInTheDocument()
  })

  it('shows details when provided', () => {
    render(
      <FormStatus 
        status="success" 
        message="Success!" 
        details="Your request was completed successfully."
      />
    )
    
    expect(screen.getByText('Success!')).toBeInTheDocument()
    expect(screen.getByText('Your request was completed successfully.')).toBeInTheDocument()
  })

  it('auto-hides success message after delay', async () => {
    const mockOnStatusChange = jest.fn()
    
    render(
      <FormStatus 
        status="success" 
        message="Success!" 
        autoHideSuccess={100}
        onStatusChange={mockOnStatusChange}
      />
    )
    
    expect(screen.getByText('Success!')).toBeInTheDocument()
    
    // Wait for auto-hide
    await new Promise(resolve => setTimeout(resolve, 150))
    
    expect(mockOnStatusChange).toHaveBeenCalledWith('idle')
  })

  it('applies custom className', () => {
    render(<FormStatus status="success" className="custom-class" />)
    expect(screen.getByRole('status')).toHaveClass('custom-class')
  })
})

describe('useFormStatus Hook', () => {
  it('initializes with idle status', () => {
    const { result } = renderHook(() => useFormStatus())
    
    expect(result.current.status).toBe('idle')
    expect(result.current.message).toBeUndefined()
    expect(result.current.details).toBeUndefined()
  })

  it('updates status with setSubmitting', () => {
    const { result } = renderHook(() => useFormStatus())
    
    act(() => {
      result.current.setSubmitting('Processing...')
    })
    
    expect(result.current.status).toBe('submitting')
    expect(result.current.message).toBe('Processing...')
  })

  it('updates status with setSuccess', () => {
    const { result } = renderHook(() => useFormStatus())
    
    act(() => {
      result.current.setSuccess('Success!', 'Details here')
    })
    
    expect(result.current.status).toBe('success')
    expect(result.current.message).toBe('Success!')
    expect(result.current.details).toBe('Details here')
  })

  it('updates status with setError', () => {
    const { result } = renderHook(() => useFormStatus())
    
    act(() => {
      result.current.setError('Error!', 'Error details')
    })
    
    expect(result.current.status).toBe('error')
    expect(result.current.message).toBe('Error!')
    expect(result.current.details).toBe('Error details')
  })

  it('resets status with reset', () => {
    const { result } = renderHook(() => useFormStatus())
    
    act(() => {
      result.current.setError('Error!')
    })
    
    expect(result.current.status).toBe('error')
    
    act(() => {
      result.current.reset()
    })
    
    expect(result.current.status).toBe('idle')
    expect(result.current.message).toBeUndefined()
    expect(result.current.details).toBeUndefined()
  })

  it('updates status with updateStatus', () => {
    const { result } = renderHook(() => useFormStatus())
    
    act(() => {
      result.current.updateStatus('success', 'Custom message', 'Custom details')
    })
    
    expect(result.current.status).toBe('success')
    expect(result.current.message).toBe('Custom message')
    expect(result.current.details).toBe('Custom details')
  })
})
