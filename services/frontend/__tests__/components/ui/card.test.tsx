import { render, screen } from '@testing-library/react';
import React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../../../src/components/ui/card';

describe('Card Components', () => {
  describe('Card', () => {
    it('renders with children', () => {
      render(
        <Card>
          <div>Card content</div>
        </Card>
      );
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <Card className="custom-card" data-testid="card">
          Content
        </Card>
      );
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('custom-card');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(<Card ref={ref}>Card</Card>);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it('applies base styles', () => {
      render(
        <Card data-testid="styled-card">
          Content
        </Card>
      );
      const card = screen.getByTestId('styled-card');
      expect(card).toHaveClass('rounded-lg');
      expect(card).toHaveClass('border');
    });
  });

  describe('CardHeader', () => {
    it('renders with children', () => {
      render(
        <CardHeader>
          <div>Header content</div>
        </CardHeader>
      );
      expect(screen.getByText('Header content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <CardHeader className="custom-header" data-testid="header">
          Header
        </CardHeader>
      );
      const header = screen.getByTestId('header');
      expect(header).toHaveClass('custom-header');
    });

    it('applies spacing styles', () => {
      render(
        <CardHeader data-testid="header">
          Header
        </CardHeader>
      );
      const header = screen.getByTestId('header');
      expect(header).toHaveClass('flex');
      expect(header).toHaveClass('flex-col');
    });
  });

  describe('CardTitle', () => {
    it('renders with children', () => {
      render(<CardTitle>Card Title</CardTitle>);
      expect(screen.getByText('Card Title')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <CardTitle className="custom-title">
          Title
        </CardTitle>
      );
      const title = screen.getByText('Title');
      expect(title).toHaveClass('custom-title');
    });

    it('renders as h3 element by default', () => {
      render(<CardTitle>Title Text</CardTitle>);
      const title = screen.getByText('Title Text');
      expect(title.tagName).toBe('H3');
    });

    it('applies typography styles', () => {
      render(<CardTitle>Styled Title</CardTitle>);
      const title = screen.getByText('Styled Title');
      expect(title).toHaveClass('text-2xl');
      expect(title).toHaveClass('font-semibold');
    });
  });

  describe('CardDescription', () => {
    it('renders with children', () => {
      render(<CardDescription>Card description text</CardDescription>);
      expect(screen.getByText('Card description text')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <CardDescription className="custom-description">
          Description
        </CardDescription>
      );
      const description = screen.getByText('Description');
      expect(description).toHaveClass('custom-description');
    });

    it('renders as p element', () => {
      render(<CardDescription>Description Text</CardDescription>);
      const description = screen.getByText('Description Text');
      expect(description.tagName).toBe('P');
    });

    it('applies muted text styles', () => {
      render(<CardDescription>Styled Description</CardDescription>);
      const description = screen.getByText('Styled Description');
      expect(description).toHaveClass('text-sm');
      expect(description).toHaveClass('text-muted-foreground');
    });
  });

  describe('CardContent', () => {
    it('renders with children', () => {
      render(
        <CardContent>
          <div>Content area</div>
        </CardContent>
      );
      expect(screen.getByText('Content area')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <CardContent className="custom-content" data-testid="content">
          Content
        </CardContent>
      );
      const content = screen.getByTestId('content');
      expect(content).toHaveClass('custom-content');
    });

    it('applies padding styles', () => {
      render(
        <CardContent data-testid="content">
          Content
        </CardContent>
      );
      const content = screen.getByTestId('content');
      expect(content).toHaveClass('p-6');
    });
  });

  describe('CardFooter', () => {
    it('renders with children', () => {
      render(
        <CardFooter>
          <button>Action</button>
        </CardFooter>
      );
      expect(screen.getByText('Action')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <CardFooter className="custom-footer" data-testid="footer">
          Footer
        </CardFooter>
      );
      const footer = screen.getByTestId('footer');
      expect(footer).toHaveClass('custom-footer');
    });

    it('applies flex layout styles', () => {
      render(
        <CardFooter data-testid="footer">
          Footer
        </CardFooter>
      );
      const footer = screen.getByTestId('footer');
      expect(footer).toHaveClass('flex');
      expect(footer).toHaveClass('items-center');
    });
  });

  describe('Card composition', () => {
    it('renders complete card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Card</CardTitle>
            <CardDescription>This is a test card</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Card body content</p>
          </CardContent>
          <CardFooter>
            <button>Save</button>
            <button>Cancel</button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByText('Test Card')).toBeInTheDocument();
      expect(screen.getByText('This is a test card')).toBeInTheDocument();
      expect(screen.getByText('Card body content')).toBeInTheDocument();
      expect(screen.getByText('Save')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it('works with partial composition', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Simple Card</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Just content, no footer</p>
          </CardContent>
        </Card>
      );

      expect(screen.getByText('Simple Card')).toBeInTheDocument();
      expect(screen.getByText('Just content, no footer')).toBeInTheDocument();
    });
  });
});
