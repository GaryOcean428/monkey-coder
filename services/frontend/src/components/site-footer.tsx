'use client';

import Link from 'next/link';
import { navigationConfig } from '@/config/navigation';

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="container mx-auto px-4 py-8 grid gap-6 md:grid-cols-3">
        <div className="space-y-2">
          <h3 className="text-sm font-semibold tracking-tight text-foreground">Monkey Coder</h3>
          <p className="text-sm text-muted-foreground">
            AI-powered code generation for modern teams.
          </p>
        </div>

        <nav className="grid grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <h4 className="font-medium text-foreground/90">Product</h4>
            <ul className="space-y-1">
              <li><Link href="/pricing" className="text-muted-foreground hover:text-foreground transition-colors">Pricing</Link></li>
              <li><Link href="/docs" className="text-muted-foreground hover:text-foreground transition-colors">Docs</Link></li>
              <li><Link href="/projects" className="text-muted-foreground hover:text-foreground transition-colors">Projects</Link></li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium text-foreground/90">Legal</h4>
            <ul className="space-y-1">
              {navigationConfig.legal.map((item) => (
                <li key={item.name}>
                  <Link href={item.href} className="text-muted-foreground hover:text-foreground transition-colors">
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        <div className="text-sm text-muted-foreground md:text-right">
          <p>&copy; {new Date().getFullYear()} Monkey Coder. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
