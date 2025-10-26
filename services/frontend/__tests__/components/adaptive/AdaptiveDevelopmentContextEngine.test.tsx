import { render, screen, waitFor, act } from '@testing-library/react'
import AdaptiveDevelopmentContextEngine from '@/components/adaptive/AdaptiveDevelopmentContextEngine'

// Mock timers
jest.useFakeTimers()

// Mock the icons from lucide-react
jest.mock('lucide-react', () => ({
  Brain: () => <div data-testid="brain-icon" />,
  Zap: () => <div data-testid="zap-icon" />,
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  Settings: () => <div data-testid="settings-icon" />,
  Code: () => <div data-testid="code-icon" />,
  Database: () => <div data-testid="database-icon" />,
  Shield: () => <div data-testid="shield-icon" />,
  Sparkles: () => <div data-testid="sparkles-icon" />,
  Activity: () => <div data-testid="activity-icon" />,
  Target: () => <div data-testid="target-icon" />,
  Layers: () => <div data-testid="layers-icon" />,
  GitBranch: () => <div data-testid="git-branch-icon" />
}))

describe('AdaptiveDevelopmentContextEngine', () => {
  afterEach(() => {
    jest.clearAllTimers()
  })

  afterAll(() => {
    jest.useRealTimers()
  })

  it('should render loading state initially', () => {
    render(<AdaptiveDevelopmentContextEngine />)
    
    // Should show loading spinner
    expect(screen.getByLabelText(/loading/i)).toBeInTheDocument()
  })

  it('should render main title when loaded', async () => {
    render(<AdaptiveDevelopmentContextEngine />)
    
    // Fast-forward timers to skip the loading delay
    act(() => {
      jest.advanceTimersByTime(1000)
    })
    
    // Wait for component to load and render title
    await waitFor(() => {
      expect(screen.getByText('Adaptive Development Context')).toBeInTheDocument()
    })
  })

  it('should render session insights dashboard', async () => {
    render(<AdaptiveDevelopmentContextEngine />)
    
    // Fast-forward timers
    act(() => {
      jest.advanceTimersByTime(1000)
    })
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Adaptive Development Context')).toBeInTheDocument()
    })
    
    // Check for session insights metrics (looking for the first occurrence)
    expect(screen.getAllByText('Productivity')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Focus')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Efficiency')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Satisfaction')[0]).toBeInTheDocument()
  })

  it('should render performance tab content', async () => {
    render(<AdaptiveDevelopmentContextEngine />)
    
    // Fast-forward timers
    act(() => {
      jest.advanceTimersByTime(1000)
    })
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Adaptive Development Context')).toBeInTheDocument()
    })
    
    // Performance tab should be active by default
    expect(screen.getByText('Model Performance Analytics')).toBeInTheDocument()
  })

  it('should show customize button', async () => {
    render(<AdaptiveDevelopmentContextEngine />)
    
    // Fast-forward timers
    act(() => {
      jest.advanceTimersByTime(1000)
    })
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Adaptive Development Context')).toBeInTheDocument()
    })
    
    // Check for customize button
    expect(screen.getByRole('button', { name: /customize/i })).toBeInTheDocument()
  })
})