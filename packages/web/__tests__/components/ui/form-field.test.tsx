import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormField } from '../../src/components/ui/form-field'

describe('FormField Component', () => {
  it('renders label and input correctly', () => {
    render(
      <FormField
        id="test-field"
        label="Test Label"
        placeholder="Test placeholder"
      />
    )

    expect(screen.getByLabelText('Test Label')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Test placeholder')).toBeInTheDocument()
  })

  it('shows required asterisk when required prop is true', () => {
    render(
      <FormField
        id="test-field"
        label="Test Label"
        required
      />
    )

    expect(screen.getByText('*')).toBeInTheDocument()
  })

  it('displays error message when error prop is provided', () => {
    const errorMessage = 'This field is required'
    render(
      <FormField
        id="test-field"
        label="Test Label"
        error={errorMessage}
      />
    )

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveClass('border-destructive')
  })

  it('shows success state when success prop is true', () => {
    render(
      <FormField
        id="test-field"
        label="Test Label"
        success={true}
      />
    )

    expect(screen.getByRole('textbox')).toHaveClass('border-green-500')
    expect(screen.getByTestId('success-icon')).toBeInTheDocument()
  })

  it('displays helper text when provided', () => {
    const helperText = 'This is a helpful tip'
    render(
      <FormField
        id="test-field"
        label="Test Label"
        helperText={helperText}
      />
    )

    expect(screen.getByText(helperText)).toBeInTheDocument()
  })

  it('shows password toggle button when showPasswordToggle is true', () => {
    render(
      <FormField
        id="test-field"
        label="Password"
        type="password"
        showPasswordToggle={true}
      />
    )

    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('toggles password visibility when toggle button is clicked', async () => {
    const user = userEvent.setup()
    render(
      <FormField
        id="test-field"
        label="Password"
        type="password"
        showPasswordToggle={true}
      />
    )

    const input = screen.getByLabelText('Password')
    const toggleButton = screen.getByRole('button')

    expect(input).toHaveAttribute('type', 'password')

    await user.click(toggleButton)
    expect(input).toHaveAttribute('type', 'text')

    await user.click(toggleButton)
    expect(input).toHaveAttribute('type', 'password')
  })

  it('calls onValidation after debounce delay', async () => {
    const mockValidation = jest.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()

    render(
      <FormField
        id="test-field"
        label="Test Label"
        onValidation={mockValidation}
      />
    )

    const input = screen.getByLabelText('Test Label')
    await user.type(input, 'test value')

    // Validation should be debounced, so it shouldn't be called immediately
    expect(mockValidation).not.toHaveBeenCalled()

    // Wait for debounce delay
    await waitFor(() => {
      expect(mockValidation).toHaveBeenCalledWith('test value')
    }, { timeout: 1000 })
  })

  it('shows validation loading state', async () => {
    const slowValidation = () => new Promise(resolve => setTimeout(() => resolve(undefined), 1000))
    const user = userEvent.setup()

    render(
      <FormField
        id="test-field"
        label="Test Label"
        onValidation={slowValidation}
      />
    )

    const input = screen.getByLabelText('Test Label')
    await user.type(input, 'test')

    await waitFor(() => {
      expect(screen.getByTestId('validation-spinner')).toBeInTheDocument()
    })
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(
      <FormField
        ref={ref}
        id="test-field"
        label="Test Label"
      />
    )

    expect(ref.current).toBeInstanceOf(HTMLInputElement)
  })

  it('spreads additional props to input element', () => {
    render(
      <FormField
        id="test-field"
        label="Test Label"
        data-testid="custom-input"
        maxLength={10}
      />
    )

    const input = screen.getByTestId('custom-input')
    expect(input).toHaveAttribute('maxLength', '10')
  })
})