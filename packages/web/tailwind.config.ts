import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Brand colors from your logo gradient
        brand: {
          coral: '#ff4757',     // Top of gradient
          orange: '#ff7675',    // Orange transition
          yellow: '#fdcb6e',    // Yellow section
          violet: '#6c5ce7',    // Electric Purple/Violet
          cyan: '#00cec9',      // Cyan/teal
          purple: '#a29bfe',    // Purple section
          magenta: '#fd79a8',   // Magenta/pink
        },
        // Light theme - warm, soft backgrounds
        light: {
          bg: {
            primary: '#fefefe',    // Very soft off-white
            secondary: '#f8f9fa',  // Light warm gray
            tertiary: '#f1f3f4',   // Slightly darker warm gray
            chat: '#ffffff',       // Chat bubbles
          },
          text: {
            primary: '#2d3436',    // Dark charcoal for main text
            secondary: '#636e72',  // Medium gray for secondary text
            tertiary: '#74b9ff',   // Muted for timestamps/meta
          },
          border: '#e9ecef',       // Subtle borders
        },
        // Dark theme - deep navy with vibrant accents
        dark: {
          bg: {
            primary: '#0a0e1a',    // Very dark navy (from your logo bg)
            secondary: '#1a1f2e',  // Slightly lighter navy for cards
            tertiary: '#2c3447',   // Medium navy for hover states
            chat: '#252b3d',       // Chat bubble background
          },
          text: {
            primary: '#f8f9fa',    // Pure white for readability
            secondary: '#adb5bd',  // Light gray for secondary text
            tertiary: '#6c757d',   // Muted gray for timestamps
          },
          border: '#495057',       // Subtle dark borders
          accent: {
            primary: '#00cec9',    // Cyan from logo
            secondary: '#a29bfe',  // Purple from logo
            success: '#00b894',    // Success green
            warning: '#fdcb6e',    // Warning yellow
            danger: '#e17055',     // Danger coral
          }
        },
        // Chat-specific colors
        chat: {
          user: {
            light: '#667eea',      // User message bubble (light)
            dark: '#764ba2',       // User message bubble (dark)
          },
          agent: {
            light: '#f093fb',      // Agent message bubble (light)
            dark: '#4facfe',       // Agent message bubble (dark)
          },
          system: {
            light: '#ffeaa7',      // System message (light)
            dark: '#fdcb6e',       // System message (dark)
          }
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      backgroundImage: {
        // Subtle grid patterns
        'grid-light': 'url("data:image/svg+xml,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\' width=\'32\' height=\'32\' fill=\'none\' stroke=\'rgb(0 0 0 / 0.02)\'%3e%3cpath d=\'M0 .5H31.5V32\'/%3e%3c/svg%3e")',
        'grid-dark': 'url("data:image/svg+xml,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\' width=\'32\' height=\'32\' fill=\'none\' stroke=\'rgb(255 255 255 / 0.03)\'%3e%3cpath d=\'M0 .5H31.5V32\'/%3e%3c/svg%3e")',
        // Gradient backgrounds inspired by your logo
        'gradient-brand': 'linear-gradient(135deg, #ff4757 0%, #ff7675 25%, #fdcb6e 50%, #00cec9 75%, #a29bfe 100%)',
        'gradient-chat-user': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-chat-agent': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'gradient-neural': 'radial-gradient(circle at center, rgba(0, 206, 201, 0.1) 0%, transparent 50%)',
      },
      boxShadow: {
        // Chat-specific shadows
        'chat-light': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'chat-dark': '0 4px 12px rgba(0, 0, 0, 0.4)',
        'message-hover': '0 4px 16px rgba(0, 206, 201, 0.2)',
        
        // Neon glow effects - subtle to intense
        'neon-cyan': '0 0 10px rgba(0, 206, 201, 0.5), 0 0 20px rgba(0, 206, 201, 0.3), 0 0 30px rgba(0, 206, 201, 0.1)',
        'neon-cyan-intense': '0 0 20px rgba(0, 206, 201, 0.8), 0 0 40px rgba(0, 206, 201, 0.6), 0 0 60px rgba(0, 206, 201, 0.4)',
        'neon-violet': '0 0 10px rgba(108, 92, 231, 0.5), 0 0 20px rgba(108, 92, 231, 0.3), 0 0 30px rgba(108, 92, 231, 0.1)',
        'neon-violet-intense': '0 0 20px rgba(108, 92, 231, 0.8), 0 0 40px rgba(108, 92, 231, 0.6), 0 0 60px rgba(108, 92, 231, 0.4)',
        'neon-coral': '0 0 10px rgba(255, 71, 87, 0.5), 0 0 20px rgba(255, 71, 87, 0.3), 0 0 30px rgba(255, 71, 87, 0.1)',
        'neon-coral-intense': '0 0 20px rgba(255, 71, 87, 0.8), 0 0 40px rgba(255, 71, 87, 0.6), 0 0 60px rgba(255, 71, 87, 0.4)',
        'neon-purple': '0 0 10px rgba(162, 155, 254, 0.5), 0 0 20px rgba(162, 155, 254, 0.3), 0 0 30px rgba(162, 155, 254, 0.1)',
        'neon-purple-intense': '0 0 20px rgba(162, 155, 254, 0.8), 0 0 40px rgba(162, 155, 254, 0.6), 0 0 60px rgba(162, 155, 254, 0.4)',
        'neon-magenta': '0 0 10px rgba(253, 121, 168, 0.5), 0 0 20px rgba(253, 121, 168, 0.3), 0 0 30px rgba(253, 121, 168, 0.1)',
        'neon-magenta-intense': '0 0 20px rgba(253, 121, 168, 0.8), 0 0 40px rgba(253, 121, 168, 0.6), 0 0 60px rgba(253, 121, 168, 0.4)',
        'neon-yellow': '0 0 10px rgba(253, 203, 110, 0.5), 0 0 20px rgba(253, 203, 110, 0.3), 0 0 30px rgba(253, 203, 110, 0.1)',
        'neon-yellow-intense': '0 0 20px rgba(253, 203, 110, 0.8), 0 0 40px rgba(253, 203, 110, 0.6), 0 0 60px rgba(253, 203, 110, 0.4)',
        
        // Multi-color neon effects
        'neon-rainbow': '0 0 10px rgba(0, 206, 201, 0.3), 0 0 20px rgba(108, 92, 231, 0.3), 0 0 30px rgba(253, 121, 168, 0.3)',
        'neon-brand': '0 0 15px rgba(0, 206, 201, 0.4), 0 0 25px rgba(108, 92, 231, 0.3)',
        
        // Hover states
        'neon-hover-cyan': '0 0 15px rgba(0, 206, 201, 0.6), 0 0 30px rgba(0, 206, 201, 0.4), 0 0 45px rgba(0, 206, 201, 0.2)',
        'neon-hover-violet': '0 0 15px rgba(108, 92, 231, 0.6), 0 0 30px rgba(108, 92, 231, 0.4), 0 0 45px rgba(108, 92, 231, 0.2)',
        'neon-hover-coral': '0 0 15px rgba(255, 71, 87, 0.6), 0 0 30px rgba(255, 71, 87, 0.4), 0 0 45px rgba(255, 71, 87, 0.2)',
      },
      animation: {
        'typing': 'typing 1.5s infinite',
        'pulse-soft': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'glow-cyan': 'glow-cyan 2s ease-in-out infinite alternate',
        'glow-violet': 'glow-violet 2s ease-in-out infinite alternate',
        'glow-coral': 'glow-coral 2s ease-in-out infinite alternate',
        'glow-rainbow': 'glow-rainbow 3s ease-in-out infinite',
        'neon-flicker': 'neon-flicker 1.5s infinite linear',
        'neon-pulse': 'neon-pulse 2s ease-in-out infinite',
        'neon-breathe': 'neon-breathe 3s ease-in-out infinite alternate',
        'border-glow': 'border-glow 2s linear infinite',
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
      keyframes: {
        typing: {
          '0%, 60%': { opacity: '1' },
          '30%': { opacity: '0.4' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 206, 201, 0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 206, 201, 0.6)' },
        },
        'glow-cyan': {
          '0%': { boxShadow: '0 0 5px rgba(0, 206, 201, 0.2), 0 0 10px rgba(0, 206, 201, 0.1)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 206, 201, 0.6), 0 0 35px rgba(0, 206, 201, 0.4), 0 0 50px rgba(0, 206, 201, 0.2)' },
        },
        'glow-violet': {
          '0%': { boxShadow: '0 0 5px rgba(108, 92, 231, 0.2), 0 0 10px rgba(108, 92, 231, 0.1)' },
          '100%': { boxShadow: '0 0 20px rgba(108, 92, 231, 0.6), 0 0 35px rgba(108, 92, 231, 0.4), 0 0 50px rgba(108, 92, 231, 0.2)' },
        },
        'glow-coral': {
          '0%': { boxShadow: '0 0 5px rgba(255, 71, 87, 0.2), 0 0 10px rgba(255, 71, 87, 0.1)' },
          '100%': { boxShadow: '0 0 20px rgba(255, 71, 87, 0.6), 0 0 35px rgba(255, 71, 87, 0.4), 0 0 50px rgba(255, 71, 87, 0.2)' },
        },
        'glow-rainbow': {
          '0%': { boxShadow: '0 0 10px rgba(0, 206, 201, 0.4)' },
          '25%': { boxShadow: '0 0 20px rgba(108, 92, 231, 0.4)' },
          '50%': { boxShadow: '0 0 20px rgba(255, 71, 87, 0.4)' },
          '75%': { boxShadow: '0 0 20px rgba(253, 121, 168, 0.4)' },
          '100%': { boxShadow: '0 0 10px rgba(0, 206, 201, 0.4)' },
        },
        'neon-flicker': {
          '0%, 19%, 21%, 23%, 25%, 54%, 56%, 100%': {
            opacity: '1',
            boxShadow: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor'
          },
          '20%, 24%, 55%': {
            opacity: '0.4',
            boxShadow: '0 0 5px currentColor'
          }
        },
        'neon-pulse': {
          '0%, 100%': {
            opacity: '1',
            boxShadow: '0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor'
          },
          '50%': {
            opacity: '0.8',
            boxShadow: '0 0 20px currentColor, 0 0 30px currentColor, 0 0 40px currentColor'
          }
        },
        'neon-breathe': {
          '0%': {
            boxShadow: '0 0 5px currentColor, 0 0 10px currentColor, 0 0 15px currentColor, 0 0 20px currentColor'
          },
          '100%': {
            boxShadow: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor, 0 0 40px currentColor, 0 0 50px currentColor'
          }
        },
        'border-glow': {
          '0%': {
            borderColor: 'rgba(0, 206, 201, 0.2)',
            boxShadow: '0 0 5px rgba(0, 206, 201, 0.2)'
          },
          '50%': {
            borderColor: 'rgba(108, 92, 231, 0.4)',
            boxShadow: '0 0 20px rgba(108, 92, 231, 0.4), 0 0 30px rgba(108, 92, 231, 0.2)'
          },
          '100%': {
            borderColor: 'rgba(0, 206, 201, 0.2)',
            boxShadow: '0 0 5px rgba(0, 206, 201, 0.2)'
          }
        },
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      fontFamily: {
        'display': ['Inter', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
