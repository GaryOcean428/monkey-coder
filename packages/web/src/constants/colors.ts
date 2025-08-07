/**
 * Monkey Coder Theme Colors - Type-Safe Color Constants
 * 
 * ⚠️ CRITICAL FIX: "lime" color was mislabeled - #6c5ce7 is Electric Purple, not lime green!
 * This file provides accurate color descriptions and type safety.
 */

export const THEME_COLORS = {
  brand: {
    coral: { 
      hex: '#ff4757', 
      name: 'Vivid Red', 
      rgb: [255, 71, 87] as const,
      description: 'Energetic coral red from logo gradient top'
    },
    orange: { 
      hex: '#ff7675', 
      name: 'Soft Coral', 
      rgb: [255, 118, 117] as const,
      description: 'Warm orange transition color'
    },
    yellow: { 
      hex: '#fdcb6e', 
      name: 'Warm Gold', 
      rgb: [253, 203, 110] as const,
      description: 'Golden yellow accent color'
    },
    violet: { 
      hex: '#6c5ce7', 
      name: 'Electric Purple', 
      rgb: [108, 92, 231] as const,
      description: 'Electric purple/violet - CORRECTED from mislabeled "lime"'
    },
    cyan: { 
      hex: '#00cec9', 
      name: 'Turquoise', 
      rgb: [0, 206, 201] as const,
      description: 'Primary brand cyan/turquoise'
    },
    purple: { 
      hex: '#a29bfe', 
      name: 'Soft Lavender', 
      rgb: [162, 155, 254] as const,
      description: 'Soft lavender purple accent'
    },
    magenta: { 
      hex: '#fd79a8', 
      name: 'Bubblegum Pink', 
      rgb: [253, 121, 168] as const,
      description: 'Playful magenta/pink gradient end'
    },
  },
  light: {
    bg: {
      primary: { hex: '#fefefe', name: 'Soft White', rgb: [254, 254, 254] as const },
      secondary: { hex: '#f8f9fa', name: 'Cool Gray', rgb: [248, 249, 250] as const },
      tertiary: { hex: '#f1f3f4', name: 'Warm Gray', rgb: [241, 243, 244] as const },
      chat: { hex: '#ffffff', name: 'Pure White', rgb: [255, 255, 255] as const },
    },
    text: {
      primary: { hex: '#2d3436', name: 'Charcoal Gray', rgb: [45, 52, 54] as const },
      secondary: { hex: '#636e72', name: 'Slate Gray', rgb: [99, 110, 114] as const },
      tertiary: { hex: '#74b9ff', name: 'Sky Blue', rgb: [116, 185, 255] as const },
    },
    border: { hex: '#e9ecef', name: 'Pearl Gray', rgb: [233, 236, 239] as const },
  },
  dark: {
    bg: {
      primary: { hex: '#0a0e1a', name: 'Midnight Navy', rgb: [10, 14, 26] as const },
      secondary: { hex: '#1a1f2e', name: 'Deep Space', rgb: [26, 31, 46] as const },
      tertiary: { hex: '#2c3447', name: 'Storm Blue', rgb: [44, 52, 71] as const },
      chat: { hex: '#252b3d', name: 'Dark Slate', rgb: [37, 43, 61] as const },
    },
    text: {
      primary: { hex: '#f8f9fa', name: 'Soft White', rgb: [248, 249, 250] as const },
      secondary: { hex: '#adb5bd', name: 'Silver Gray', rgb: [173, 181, 189] as const },
      tertiary: { hex: '#6c757d', name: 'Cool Gray', rgb: [108, 117, 125] as const },
    },
    border: { hex: '#495057', name: 'Graphite', rgb: [73, 80, 87] as const },
    accent: {
      primary: { hex: '#00cec9', name: 'Cyan', rgb: [0, 206, 201] as const },
      secondary: { hex: '#a29bfe', name: 'Periwinkle', rgb: [162, 155, 254] as const },
      success: { hex: '#00b894', name: 'Mint Green', rgb: [0, 184, 148] as const },
      warning: { hex: '#fdcb6e', name: 'Amber', rgb: [253, 203, 110] as const },
      danger: { hex: '#e17055', name: 'Burnt Orange', rgb: [225, 112, 85] as const },
    }
  },
  chat: {
    user: {
      light: { hex: '#667eea', name: 'Royal Blue', rgb: [102, 126, 234] as const },
      dark: { hex: '#764ba2', name: 'Deep Violet', rgb: [118, 75, 162] as const },
    },
    agent: {
      light: { hex: '#f093fb', name: 'Orchid Pink', rgb: [240, 147, 251] as const },
      dark: { hex: '#4facfe', name: 'Ocean Blue', rgb: [79, 172, 254] as const },
    },
    system: {
      light: { hex: '#ffeaa7', name: 'Cream', rgb: [255, 234, 167] as const },
      dark: { hex: '#fdcb6e', name: 'Honey', rgb: [253, 203, 110] as const },
    }
  }
} as const;

// Type-safe brand color keys
export type BrandColor = keyof typeof THEME_COLORS.brand;
export type LightThemeColor = keyof typeof THEME_COLORS.light;
export type DarkThemeColor = keyof typeof THEME_COLORS.dark;
export type ChatColor = keyof typeof THEME_COLORS.chat;

// Color validation utilities
export function validateHexColor(hex: string): boolean {
  return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex);
}

export function hexToRgb(hex: string): [number, number, number] | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : null;
}

// Get color by path (e.g., 'brand.violet', 'dark.bg.primary')
export function getColor(path: string) {
  const keys = path.split('.');
  let current: any = THEME_COLORS;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return null;
    }
  }
  
  return current;
}

// Branded gradient definitions
export const GRADIENTS = {
  brand: 'linear-gradient(135deg, #ff4757 0%, #ff7675 25%, #fdcb6e 50%, #00cec9 75%, #a29bfe 100%)',
  chatUser: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  chatAgent: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  neural: 'radial-gradient(circle at center, rgba(0, 206, 201, 0.1) 0%, transparent 50%)',
} as const;

// Neon effect definitions
export const NEON_EFFECTS = {
  subtle: {
    cyan: 'shadow-neon-cyan',
    violet: 'shadow-neon-violet', 
    coral: 'shadow-neon-coral',
    purple: 'shadow-neon-purple',
    magenta: 'shadow-neon-magenta',
    yellow: 'shadow-neon-yellow',
  },
  intense: {
    cyan: 'shadow-neon-cyan-intense',
    violet: 'shadow-neon-violet-intense',
    coral: 'shadow-neon-coral-intense', 
    purple: 'shadow-neon-purple-intense',
    magenta: 'shadow-neon-magenta-intense',
    yellow: 'shadow-neon-yellow-intense',
  },
  hover: {
    cyan: 'hover:shadow-neon-hover-cyan',
    violet: 'hover:shadow-neon-hover-violet',
    coral: 'hover:shadow-neon-hover-coral',
  },
  multiColor: {
    rainbow: 'shadow-neon-rainbow',
    brand: 'shadow-neon-brand',
  },
  animations: {
    flicker: 'animate-neon-flicker',
    pulse: 'animate-neon-pulse',
    breathe: 'animate-neon-breathe',
    glowCyan: 'animate-glow-cyan',
    glowViolet: 'animate-glow-violet',
    glowCoral: 'animate-glow-coral',
    glowRainbow: 'animate-glow-rainbow',
    borderGlow: 'animate-border-glow',
  }
} as const;

// Neon utility functions
export function getNeonClass(color: keyof typeof NEON_EFFECTS.subtle, intensity: 'subtle' | 'intense' = 'subtle'): string {
  return NEON_EFFECTS[intensity][color] || '';
}

export function getNeonHover(color: keyof typeof NEON_EFFECTS.hover): string {
  return NEON_EFFECTS.hover[color] || '';
}

export function getNeonAnimation(animation: keyof typeof NEON_EFFECTS.animations): string {
  return NEON_EFFECTS.animations[animation] || '';
}

// Combined neon button classes
export const NEON_BUTTON_CLASSES = {
  cyan: 'bg-brand-cyan text-white shadow-neon-cyan hover:shadow-neon-hover-cyan transition-all duration-300 animate-glow-cyan',
  violet: 'bg-brand-violet text-white shadow-neon-violet hover:shadow-neon-hover-violet transition-all duration-300 animate-glow-violet',
  coral: 'bg-brand-coral text-white shadow-neon-coral hover:shadow-neon-hover-coral transition-all duration-300 animate-glow-coral',
  rainbow: 'bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-magenta text-white shadow-neon-rainbow animate-glow-rainbow',
} as const;