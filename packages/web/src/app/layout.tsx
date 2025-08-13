import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { AuthProvider } from '@/lib/auth-context'
import { Toaster } from 'react-hot-toast'
import { SiteHeader } from '@/components/site-header'
import { SiteFooter } from '@/components/site-footer'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Monkey Coder - AI-Powered Code Generation Platform',
  description: 'Transform your ideas into production-ready code with AI. Powered by advanced language models.',
  keywords: 'AI, code generation, programming, development, automation',
  authors: [{ name: 'Monkey Coder Team' }],
  icons: {
    icon: '/icon.png',
    apple: '/android-chrome-192x192.png',
  },
  manifest: '/site.webmanifest',
  openGraph: {
    title: 'Monkey Coder - AI-Powered Code Generation',
    description: 'Transform your ideas into production-ready code with AI',
    url: 'https://monkey-coder.com',
    siteName: 'Monkey Coder',
    images: [
      {
        url: 'https://monkey-coder.com/og-image.png',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Monkey Coder - AI-Powered Code Generation',
    description: 'Transform your ideas into production-ready code with AI',
    images: ['https://monkey-coder.com/twitter-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <AuthProvider>
            <div className="min-h-screen flex flex-col">
              <SiteHeader />
              <main className="flex-1">{children}</main>
              <SiteFooter />
            </div>
            <Toaster
              position="bottom-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--background)',
                  color: 'var(--foreground)',
                  border: '1px solid var(--border)',
                },
              }}
            />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
