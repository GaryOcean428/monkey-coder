'use client'

import Link from 'next/link'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Menu, X } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { ThemeToggle } from '@/components/ui/theme-toggle'

const navigation = [
  { name: 'Features', href: '#features' },
  { name: 'Pricing', href: '#pricing' },
]

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-800 bg-[#1a1f2e] backdrop-blur
                      supports-[backdrop-filter]:bg-[#1a1f2e]/90 neon-header">
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-4
                      xs:p-5
                      sm:p-6
                      lg:px-8"
           aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/"
                className="-m-1.5 p-1.5 flex items-center rounded-lg
                          hover:bg-white/5
                          focus:outline-none focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]"
                aria-label="Monkey Coder home">
            <Image
              src="/splash.png"
              alt="Monkey Coder Logo"
              width={300}
              height={80}
              className="h-16 w-auto
                        xs:h-18
                        sm:h-20 neon-logo"
              priority
            />
          </Link>
        </div>
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-white
                      hover:bg-white/10 hover:text-gray-100
                      focus:outline-none focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]
                      transition-colors duration-200"
            onClick={() => setMobileMenuOpen(true)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-menu"
          >
            <span className="sr-only">Open main menu</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        <div className="hidden lg:flex lg:gap-x-8
                        xl:gap-x-12">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="text-sm font-semibold leading-6 text-white/80 rounded-md px-3 py-2
                        hover:text-white hover:bg-white/5
                        focus:outline-none focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]
                        transition-colors duration-200"
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="hidden lg:flex lg:flex-1 lg:justify-end lg:gap-x-3
                        xl:gap-x-4">
          <ThemeToggle />
          <Link href="/login">
            <Button variant="ghost"
                    className="text-white border-transparent
                              hover:text-white hover:bg-white/10 hover:border-white/20
                              focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]">
              Log in
            </Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-[#00cec9] text-white border-[#00cec9]
                              hover:bg-[#00b8b3] hover:border-[#00b8b3]
                              focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]">
              Get started
            </Button>
          </Link>
        </div>
      </nav>

      {/* Mobile menu */}
      <div className={cn('lg:hidden', mobileMenuOpen ? 'block' : 'hidden')}
           id="mobile-menu"
           role="dialog"
           aria-modal="true"
           aria-labelledby="mobile-menu-button">
        <div className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
             onClick={() => setMobileMenuOpen(false)}
             aria-hidden="true" />
        <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-[#1a1f2e] px-4 py-6 shadow-xl
                        xs:px-5
                        sm:max-w-sm sm:px-6 sm:ring-1 sm:ring-white/10">
          <div className="flex items-center justify-between">
            <Link href="/"
                  className="-m-1.5 p-1.5 flex items-center rounded-lg
                            hover:bg-white/5
                            focus:outline-none focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]"
                  onClick={() => setMobileMenuOpen(false)}
                  aria-label="Monkey Coder home">
              <Image
                src="/splash.png"
                alt="Monkey Coder Logo"
                width={240}
                height={64}
                className="h-14 w-auto
                          xs:h-16 neon-logo"
              />
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-white
                        hover:bg-white/10 hover:text-gray-100
                        focus:outline-none focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]
                        transition-colors duration-200"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Close menu"
            >
              <span className="sr-only">Close menu</span>
              <X className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-white/10">
              <div className="space-y-2 py-6">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-white/90
                              hover:bg-white/5 hover:text-white
                              focus:outline-none focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]
                              transition-colors duration-200"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
              <div className="py-6 space-y-3
                              xs:space-y-4">
                <div className="flex items-center justify-center">
                  <ThemeToggle />
                </div>
                <Link href="/login"
                      className="block"
                      onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="outline"
                          className="w-full text-white border-white/20 bg-transparent
                                    hover:bg-white/10 hover:border-white/30
                                    focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]">
                    Log in
                  </Button>
                </Link>
                <Link href="/signup"
                      className="block"
                      onClick={() => setMobileMenuOpen(false)}>
                  <Button className="w-full bg-[#00cec9] text-white border-[#00cec9]
                                    hover:bg-[#00b8b3] hover:border-[#00b8b3]
                                    focus:ring-2 focus:ring-[#00cec9] focus:ring-offset-2 focus:ring-offset-[#1a1f2e]">
                    Get started
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
