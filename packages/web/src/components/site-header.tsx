'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { ThemeToggle } from './theme-toggle';
import { Button } from './ui/button';
import { Menu, X } from 'lucide-react';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { unifiedNavigation } from '@/config/navigation';

export function SiteHeader() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileMenuOpen(false);
    };
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
      document.addEventListener('keydown', onKeyDown);
    } else {
      document.body.style.overflow = originalOverflow || '';
    }
    return () => {
      document.body.style.overflow = originalOverflow || '';
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [mobileMenuOpen]);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav
        className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8"
        aria-label="Global"
      >
        <div className="flex lg:flex-1">
          <Link
            href="/"
            className="-m-1.5 p-1.5 flex items-center gap-2"
          >
            <span className="relative h-12 w-[160px]">
              <Image
                src="/logo-light.png"
                alt="Monkey Coder"
                width={160}
                height={48}
                className="h-12 w-auto object-contain block dark:hidden"
                priority
              />
              <Image
                src="/logo-dark.png"
                alt="Monkey Coder"
                width={160}
                height={48}
                className="h-12 w-auto object-contain hidden dark:block neon-logo"
                priority
              />
            </span>
            <span className="font-bold text-xl">Monkey Coder</span>
          </Link>
        </div>
        
        {/* Mobile menu button */}
        <div className="flex lg:hidden">
          <button
            type="button"
            aria-controls="mobile-menu"
            aria-expanded={mobileMenuOpen}
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700 dark:text-gray-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        
        {/* Desktop navigation */}
        <div className="hidden lg:flex lg:gap-x-12">
          {unifiedNavigation.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className={cn(
                  'text-sm font-semibold leading-6 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500',
                  active
                    ? 'text-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {item.name}
              </Link>
            );
          })}
        </div>
        
        {/* Desktop actions */}
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-4">
          <ThemeToggle />
          <Link href="/login">
            <Button variant="outline" className="border-primary/20 text-primary hover:bg-primary/10 hover:border-primary/40">
              Log in
            </Button>
          </Link>
          <Link href="/signup">
            <Button className="neon-button-cyan">Get started</Button>
          </Link>
        </div>
      </nav>

      {/* Mobile menu */}
      <div className={cn('lg:hidden', mobileMenuOpen ? 'block' : 'hidden')}>
        <div className="fixed inset-0 z-50" />
        <div 
          id="mobile-menu" 
          role="dialog" 
          aria-modal="true" 
          className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-background px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10" 
          tabIndex={-1}
        >
          <div className="flex items-center justify-between">
            <Link
              href="/"
              className="-m-1.5 p-1.5 flex items-center gap-2"
            >
              <span className="relative h-12 w-[160px]">
                <Image
                  src="/logo-light.png"
                  alt="Monkey Coder"
                  width={160}
                  height={48}
                  className="h-12 w-auto object-contain block dark:hidden"
                  priority
                />
                <Image
                  src="/logo-dark.png"
                  alt="Monkey Coder"
                  width={160}
                  height={48}
                  className="h-12 w-auto object-contain hidden dark:block neon-logo"
                  priority
                />
              </span>
              <span className="font-bold text-xl">Monkey Coder</span>
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-700 dark:text-gray-300"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <X className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-gray-500/10">
              <div className="space-y-2 py-6">
                {unifiedNavigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-foreground hover:bg-gray-50 dark:hover:bg-gray-800"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
              <div className="py-6 space-y-2">
                <div className="flex justify-center mb-4">
                  <ThemeToggle />
                </div>
                <Link href="/login" className="block">
                  <Button variant="outline" className="w-full border-primary/20 text-primary hover:bg-primary/10 hover:border-primary/40">
                    Log in
                  </Button>
                </Link>
                <Link href="/signup" className="block">
                  <Button className="w-full neon-button-cyan">Get started</Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
