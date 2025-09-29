import { render, screen } from '@testing-library/react'
import { PasswordStrengthIndicator, getPasswordStrength } from '../../../src/components/ui/password-strength'

describe('PasswordStrengthIndicator Component', () => {
  it('does not render when password is empty', () => {
    render(<PasswordStrengthIndicator password="" />)
    expect(screen.queryByText('Password strength')).not.toBeInTheDocument()
  })

  it('renders strength indicator for weak password', () => {
    render(<PasswordStrengthIndicator password="123" />)
    
    expect(screen.getByText('Password strength')).toBeInTheDocument()
    expect(screen.getByText('Weak')).toBeInTheDocument()
  })

  it('renders strength indicator for strong password', () => {
    render(<PasswordStrengthIndicator password="StrongP@ssw0rd!" />)
    
    expect(screen.getByText('Password strength')).toBeInTheDocument()
    expect(screen.getByText('Strong')).toBeInTheDocument()
  })

  it('shows criteria list when showCriteria is true', () => {
    render(<PasswordStrengthIndicator password="test123" showCriteria={true} />)
    
    expect(screen.getByText('Requirements:')).toBeInTheDocument()
    expect(screen.getByText('At least 8 characters')).toBeInTheDocument()
    expect(screen.getByText('Contains uppercase letter')).toBeInTheDocument()
    expect(screen.getByText('Contains lowercase letter')).toBeInTheDocument()
    expect(screen.getByText('Contains number')).toBeInTheDocument()
    expect(screen.getByText('Contains special character')).toBeInTheDocument()
  })

  it('hides criteria list when showCriteria is false', () => {
    render(<PasswordStrengthIndicator password="test123" showCriteria={false} />)
    
    expect(screen.queryByText('Requirements:')).not.toBeInTheDocument()
  })

  it('marks met criteria with check icons', () => {
    render(<PasswordStrengthIndicator password="Test123!" showCriteria={true} />)
    
    // All criteria should be met for this password
    const checkIcons = screen.getAllByTestId('check-icon')
    expect(checkIcons).toHaveLength(5)
  })

  it('marks unmet criteria with X icons', () => {
    render(<PasswordStrengthIndicator password="weak" showCriteria={true} />)
    
    // Most criteria should be unmet for this password
    const xIcons = screen.getAllByTestId('x-icon')
    expect(xIcons.length).toBeGreaterThan(0)
  })
})

describe('getPasswordStrength Function', () => {
  it('returns correct strength for empty password', () => {
    const result = getPasswordStrength('')
    expect(result).toEqual({
      score: 0,
      level: 'weak',
      percentage: 0
    })
  })

  it('returns correct strength for weak password', () => {
    const result = getPasswordStrength('123')
    expect(result.level).toBe('weak')
    expect(result.score).toBeLessThanOrEqual(40)
  })

  it('returns correct strength for fair password', () => {
    const result = getPasswordStrength('test123')
    expect(result.level).toBe('fair')
    expect(result.score).toBeGreaterThan(40)
    expect(result.score).toBeLessThanOrEqual(60)
  })

  it('returns correct strength for good password', () => {
    const result = getPasswordStrength('Test123')
    expect(result.level).toBe('good')
    expect(result.score).toBeGreaterThan(60)
    expect(result.score).toBeLessThanOrEqual(80)
  })

  it('returns correct strength for strong password', () => {
    const result = getPasswordStrength('Test123!')
    expect(result.level).toBe('strong')
    expect(result.score).toBeGreaterThan(80)
  })

  it('caps percentage at 100', () => {
    const result = getPasswordStrength('VeryStrong123!@#$%')
    expect(result.percentage).toBeLessThanOrEqual(100)
  })

  it('correctly identifies all criteria for complex password', () => {
    const password = 'ComplexP@ssw0rd!'
    const result = getPasswordStrength(password)
    
    // This password should meet all criteria
    expect(result.score).toBe(100)
    expect(result.level).toBe('strong')
    expect(result.percentage).toBe(100)
  })

  it('handles special characters correctly', () => {
    const passwordWithSpecial = 'Test123!'
    const passwordWithoutSpecial = 'Test123'
    
    const resultWith = getPasswordStrength(passwordWithSpecial)
    const resultWithout = getPasswordStrength(passwordWithoutSpecial)
    
    expect(resultWith.score).toBeGreaterThan(resultWithout.score)
  })
})
