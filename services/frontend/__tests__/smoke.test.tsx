import { render, screen } from '@testing-library/react';
import React from 'react';

describe('web workspace smoke', () => {
  it('renders a simple element', () => {
    render(<button>Click me</button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('renders multiple components without errors', () => {
    render(
      <div>
        <h1>Test Header</h1>
        <button>Test Button</button>
        <p>Test paragraph</p>
      </div>
    );
    
    expect(screen.getByText('Test Header')).toBeInTheDocument();
    expect(screen.getByText('Test Button')).toBeInTheDocument();
    expect(screen.getByText('Test paragraph')).toBeInTheDocument();
  });

  it('handles basic props and state', () => {
    const TestComponent = ({ title }: { title: string }) => {
      const [count, setCount] = React.useState(0);
      return (
        <div>
          <h2>{title}</h2>
          <p>Count: {count}</p>
          <button onClick={() => setCount(count + 1)}>Increment</button>
        </div>
      );
    };

    render(<TestComponent title="Smoke Test" />);
    
    expect(screen.getByText('Smoke Test')).toBeInTheDocument();
    expect(screen.getByText('Count: 0')).toBeInTheDocument();
    expect(screen.getByText('Increment')).toBeInTheDocument();
  });
});
