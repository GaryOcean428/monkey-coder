'use client';

import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  // Avoid hydration mismatch
  const activeTheme = (theme === 'system' ? resolvedTheme : theme) || 'dark';

  const toggle = () => {
    setTheme(activeTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={`Switch to ${activeTheme === 'dark' ? 'light' : 'dark'} theme`}
      className="relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-border/60 bg-background/60 text-foreground shadow-sm transition-colors hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/60"
    >
      {/* Sun icon (visible in dark mode to indicate switch to light) */}
      <Sun
        className={[
          'absolute h-[1.15rem] w-[1.15rem] transition-all',
          activeTheme === 'dark'
            ? 'rotate-0 scale-100 text-yellow-400'
            : '-rotate-90 scale-0 text-foreground'
        ].join(' ')}
      />
      {/* Moon icon (visible in light mode to indicate switch to dark) */}
      <Moon
        className={[
          'absolute h-[1.1rem] w-[1.1rem] transition-all',
          activeTheme === 'dark'
            ? 'rotate-90 scale-0 text-foreground'
            : 'rotate-0 scale-100 text-slate-900'
        ].join(' ')}
      />
      {/* Fallback label for screen readers when icons may not render */}
      <span className="sr-only">
        {mounted ? (activeTheme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme') : 'Toggle theme'}
      </span>
    </button>
  );
}
