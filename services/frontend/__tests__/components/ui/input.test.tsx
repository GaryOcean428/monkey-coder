import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { Input } from '../../../src/components/ui/input';

describe('Input Component', () => {
  it('renders correctly', () => {
    render(<Input placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('accepts and displays typed text', () => {
    render(<Input placeholder="Type here" />);
    const input = screen.getByPlaceholderText('Type here') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'Test input' } });
    expect(input.value).toBe('Test input');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} placeholder="Ref test" />);

    expect(ref.current).toBeInstanceOf(HTMLInputElement);
    expect(ref.current?.placeholder).toBe('Ref test');
  });

  it('applies custom className', () => {
    render(<Input className="custom-input" placeholder="Custom" />);
    const input = screen.getByPlaceholderText('Custom');
    expect(input).toHaveClass('custom-input');
  });

  it('can be disabled', () => {
    render(<Input disabled placeholder="Disabled input" />);
    const input = screen.getByPlaceholderText('Disabled input');
    expect(input).toBeDisabled();
  });

  it('supports different input types', () => {
    const { rerender } = render(<Input type="email" placeholder="Email" />);
    expect(screen.getByPlaceholderText('Email')).toHaveAttribute('type', 'email');

    rerender(<Input type="password" placeholder="Password" />);
    expect(screen.getByPlaceholderText('Password')).toHaveAttribute('type', 'password');

    rerender(<Input type="number" placeholder="Number" />);
    expect(screen.getByPlaceholderText('Number')).toHaveAttribute('type', 'number');
  });

  it('handles onChange event', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} placeholder="Change test" />);

    const input = screen.getByPlaceholderText('Change test');
    fireEvent.change(input, { target: { value: 'New value' } });

    expect(handleChange).toHaveBeenCalled();
    expect(handleChange.mock.calls[0][0].target.value).toBe('New value');
  });

  it('handles onFocus and onBlur events', () => {
    const handleFocus = jest.fn();
    const handleBlur = jest.fn();

    render(
      <Input
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder="Focus test"
      />
    );

    const input = screen.getByPlaceholderText('Focus test');

    fireEvent.focus(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);

    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('accepts required attribute', () => {
    render(<Input required placeholder="Required input" />);
    const input = screen.getByPlaceholderText('Required input');
    expect(input).toBeRequired();
  });

  it('accepts readOnly attribute', () => {
    render(<Input readOnly value="Read only text" />);
    const input = screen.getByDisplayValue('Read only text');
    expect(input).toHaveAttribute('readOnly');
  });

  it('supports maxLength attribute', () => {
    render(<Input maxLength={10} placeholder="Max length" />);
    const input = screen.getByPlaceholderText('Max length');
    expect(input).toHaveAttribute('maxLength', '10');
  });

  it('supports pattern attribute for validation', () => {
    render(<Input pattern="[0-9]*" placeholder="Numbers only" />);
    const input = screen.getByPlaceholderText('Numbers only');
    expect(input).toHaveAttribute('pattern', '[0-9]*');
  });

  it('applies base styles correctly', () => {
    render(<Input placeholder="Styled input" />);
    const input = screen.getByPlaceholderText('Styled input');
    expect(input).toHaveClass('flex');
  });

  it('spreads additional props', () => {
    render(
      <Input
        data-testid="custom-input"
        aria-label="Custom Input"
        placeholder="Props test"
      />
    );

    const input = screen.getByTestId('custom-input');
    expect(input).toHaveAttribute('aria-label', 'Custom Input');
  });
});
