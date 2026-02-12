# Monkey Coder Web

Next.js 15.2.3 web interface for the Monkey Coder AI-powered code generation and analysis platform.

## Features

- 🎨 **Modern UI**: Built with Next.js 15, React 18, and Tailwind CSS
- 🔐 **Authentication**: Secure user authentication with JWT tokens
- 🚀 **Real-time Updates**: Server-Sent Events for streaming responses
- 📱 **Responsive Design**: Mobile-first responsive interface
- 🌙 **Dark Mode**: Built-in dark/light theme support
- 🔌 **API Integration**: Full integration with the Monkey Coder backend API

## Tech Stack

- **Framework**: Next.js 15.2.3 (App Router)
- **React**: React 18
- **Styling**: Tailwind CSS 3.4
- **UI Components**: Custom component library with shadcn/ui
- **Type Safety**: TypeScript with strict mode
- **Testing**: Jest + React Testing Library
- **State Management**: React Context + hooks

## Getting Started

### Prerequisites

- Node.js 20 or later
- Yarn 4.9.2 (managed via Corepack)

### Installation

```bash
# From repository root
corepack enable
corepack prepare yarn@4.9.2 --activate
yarn install
```

### Development

```bash
# Start the development server
yarn workspace @monkey-coder/web dev

# Or from the web package directory
cd packages/web
yarn dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

### Building

```bash
# Build for production
yarn workspace @monkey-coder/web build

# Start production server
yarn workspace @monkey-coder/web start
```

### Testing

```bash
# Run all tests
yarn workspace @monkey-coder/web test

# Run tests in watch mode
yarn workspace @monkey-coder/web test:watch

# Run tests with coverage
yarn workspace @monkey-coder/web test:coverage
```

## Project Structure

```
packages/web/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── (auth)/       # Authentication pages
│   │   ├── (dashboard)/  # Dashboard pages
│   │   └── api/          # API routes
│   ├── components/       # React components
│   │   ├── ui/          # Base UI components
│   │   └── features/    # Feature-specific components
│   ├── lib/             # Utility libraries
│   │   ├── api/         # API client
│   │   ├── auth/        # Authentication helpers
│   │   └── utils/       # General utilities
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   └── styles/          # Global styles
├── public/              # Static assets
├── __tests__/          # Test files
└── next.config.js      # Next.js configuration
```

## Environment Variables

Create a `.env.local` file in the package root:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Authentication
NEXTAUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your-ga-id
```

## Key Features

### Authentication

- User registration and login
- JWT token management
- Protected routes
- Session handling

### Code Generation

- Interactive code generation interface
- Real-time streaming responses
- Multiple AI model selection
- Custom personas and configurations

### Code Analysis

- Upload and analyze code files
- Security, quality, and performance analysis
- Interactive analysis reports
- Export analysis results

### Dashboard

- Project management
- Generation history
- Usage statistics
- User settings

## Components

### UI Components

The project uses a custom component library based on shadcn/ui:

- `Button` - Primary button component
- `Input` - Form input component
- `Card` - Container component
- `Dialog` - Modal dialog component
- And many more...

### Feature Components

- `CodeEditor` - Monaco-based code editor
- `StreamingResponse` - Real-time response display
- `FileUploader` - File upload with drag-and-drop
- `AnalysisViewer` - Code analysis visualization

## API Integration

The web app integrates with the backend API through a typed client:

```typescript
import { apiClient } from '@/lib/api/client';

// Generate code
const result = await apiClient.generate({
  prompt: 'Create a React component',
  language: 'typescript',
  model: 'claude-sonnet-4-5'
});

// Stream responses
apiClient.streamGenerate({
  prompt: 'Build a REST API',
  onProgress: (data) => console.log(data),
  onComplete: (result) => console.log('Done!', result)
});
```

## Deployment

### Railway

The web app is configured for Railway deployment:

1. Build command: `yarn build`
2. Start command: `yarn start`
3. Health check: `/api/health`

See the [Railway Deployment Guide](../../docs/deployment/RAILWAY_DEPLOYMENT.md) for details.

### Vercel

Can also be deployed to Vercel with zero configuration:

```bash
vercel deploy
```

### Docker

Build and run with Docker:

```bash
docker build -t monkey-coder-web .
docker run -p 3000:3000 monkey-coder-web
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new features
4. Run linting and tests
5. Submit a pull request

### Code Style

- Follow existing code conventions
- Use TypeScript for type safety
- Write tests for components and utilities
- Follow the Next.js App Router patterns

### Testing Guidelines

- Write unit tests for utilities and helpers
- Write component tests with React Testing Library
- Maintain test coverage above 70%

## Performance

- Optimized bundle size with tree shaking
- Image optimization with Next.js Image
- Font optimization with next/font
- Automatic code splitting
- Static generation where possible

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader friendly
- Semantic HTML
- ARIA labels where needed

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Support

- 📚 Documentation: [https://docs.monkey-coder.dev](https://docs.monkey-coder.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/GaryOcean428/monkey-coder/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/GaryOcean428/monkey-coder/discussions)
