import { render, screen } from '@testing-library/react';
import React from 'react';

describe('web workspace smoke', () => {
  it('renders a simple element', () => {
    render(<button>Click me</button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
