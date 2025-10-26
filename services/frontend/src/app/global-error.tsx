'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { AlertTriangle, Home } from 'lucide-react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center bg-background text-foreground">
        <div className="mx-auto max-w-md text-center">
          <AlertTriangle className="mx-auto h-16 w-16 text-destructive" />
          <h1 className="mt-6 text-4xl font-bold">Something went wrong</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            A critical error occurred. We've been notified and are working to fix it.
          </p>
          {error.digest && (
            <p className="mt-2 text-sm text-muted-foreground">
              Error ID: {error.digest}
            </p>
          )}
          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button
              onClick={
                // Attempt to recover by trying to re-render the segment
                () => reset()
              }
              className="gap-2"
            >
              Try Again
            </Button>
            <Link href="/">
              <Button variant="outline" className="gap-2">
                <Home className="h-4 w-4" />
                Go Home
              </Button>
            </Link>
          </div>
        </div>
      </body>
    </html>
  )
}
