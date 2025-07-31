import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { FileX, Home } from 'lucide-react'

export default function NotFound() {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center bg-background text-foreground">
        <div className="mx-auto max-w-md text-center">
          <FileX className="mx-auto h-16 w-16 text-muted-foreground" />
          <h1 className="mt-6 text-4xl font-bold">404 - Page Not Found</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Link href="/">
              <Button className="gap-2">
                <Home className="h-4 w-4" />
                Go Home
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline">
                Go to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </body>
    </html>
  )
}
