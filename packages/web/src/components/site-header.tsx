'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from './theme-toggle';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/docs', label: 'Docs' },
  { href: '/contact', label: 'Contact' },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/70 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="-m-1.5 p-1.5 flex items-center gap-2">
            <span className="relative h-8 w-[120px]">
              <Image
                src="/logo-light.png"
                alt="Monkey Coder"
                width={120}
                height={32}
                className="h-8 w-auto object-contain block dark:hidden"
                priority
              />
              <Image
                src="/logo-dark.png"
                alt="Monkey Coder"
                width={120}
                height={32}
                className="h-8 w-auto object-contain hidden dark:block"
                priority
              />
            </span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            {navItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? 'page' : undefined}
                  className={cn(
                    'px-2 py-1 rounded-md transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500',
                    active
                      ? 'text-foreground bg-muted'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/60'
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
