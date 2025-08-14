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
  metadataBase: new URL('https://coder.fastmonkey.au'),
  title: 'Monkey Coder - AI-Powered Code Generation Platform',
  description: 'Transform your ideas into production-ready code with AI. Powered by advanced language models.',
  keywords: 'AI, code generation, programming, development, automation',
  authors: [{ name: 'Monkey Coder Team' }],
  icons: {
    icon: ['/favicon.ico', '/favicon-32x32.ico', '/favicon-16x16.ico'],
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
  alternates: {
    canonical: '/',
  },
  themeColor: '#0b1324',
  openGraph: {
    title: 'Monkey Coder - AI-Powered Code Generation',
    description: 'Transform your ideas into production-ready code with AI',
    url: '/',
    siteName: 'Monkey Coder',
    images: [
      {
        url: '/splash.png',
        width: 1068,
        height: 874,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Monkey Coder - AI-Powered Code Generation',
    description: 'Transform your ideas into production-ready code with AI',
    images: ['/splash.png'],
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
              <main className="flex-1">
                {children}
                {/* Logo placement and styling */}
                <div className="flex justify-center items-center my-8">
                  <img
                    src="/splash.png"
                    alt="Monkey Coder Logo"
                    className="max-w-xs w-full h-auto object-contain animate-pulse [text-shadow:0_0_5px_#00fff7,_0_0_10px_#00fff7,_0_0_15px_#00fff7,_0_0_20px_#00fff7]"
                    style={{ maxWidth: '200px' }} // Example size, adjust as needed
                  />
                </div>
              </main>
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
