import { describe, it, expect } from 'vitest';
import { THEME_COLORS, validateHexColor, hexToRgb, getColor } from '../constants/colors';

describe('Color Consistency Validation', () => {
  describe('Brand Colors', () => {
    it('should have accurate color names and descriptions', () => {
      // Test the corrected violet color (previously mislabeled as "lime")
      const violet = THEME_COLORS.brand.violet;
      expect(violet.name).toBe('Electric Purple');
      expect(violet.hex).toBe('#6c5ce7');
      expect(violet.description).toContain('CORRECTED from mislabeled "lime"');
      
      // Test that RGB values match hex values
      expect(violet.rgb).toEqual([108, 92, 231]);
      expect(hexToRgb(violet.hex)).toEqual([108, 92, 231]);
    });

    it('should not have misleading color names', () => {
      // Ensure no color names contradict their actual appearance
      const coral = THEME_COLORS.brand.coral;
      expect(coral.name).toContain('Red');
      expect(coral.hex).toBe('#ff4757');

      const cyan = THEME_COLORS.brand.cyan;
      expect(cyan.name).toBe('Turquoise');
      expect(cyan.hex).toBe('#00cec9');

      const yellow = THEME_COLORS.brand.yellow;
      expect(yellow.name).toContain('Gold');
      expect(yellow.hex).toBe('#fdcb6e');
    });

    it('should have all required brand colors', () => {
      const requiredColors = ['coral', 'orange', 'yellow', 'violet', 'cyan', 'purple', 'magenta'];
      requiredColors.forEach(color => {
        expect(THEME_COLORS.brand).toHaveProperty(color);
        expect(THEME_COLORS.brand[color as keyof typeof THEME_COLORS.brand]).toBeDefined();
      });
    });
  });

  describe('Color Validation', () => {
    it('should validate all hex colors in theme', () => {
      function validateColorObject(obj: any, path = ''): void {
        for (const [key, value] of Object.entries(obj)) {
          const currentPath = path ? `${path}.${key}` : key;
          
          if (value && typeof value === 'object') {
            if ('hex' in value) {
              expect(validateHexColor(value.hex)).toBe(true);
              expect(value.hex).toMatch(/^#[0-9a-f]{6}$/i);
            } else {
              validateColorObject(value, currentPath);
            }
          }
        }
      }

      validateColorObject(THEME_COLORS);
    });

    it('should have consistent RGB values', () => {
      function checkRgbConsistency(obj: any): void {
        for (const value of Object.values(obj)) {
          if (value && typeof value === 'object') {
            if ('hex' in value && 'rgb' in value) {
              const calculatedRgb = hexToRgb(value.hex);
              expect(calculatedRgb).toEqual(value.rgb);
            } else {
              checkRgbConsistency(value);
            }
          }
        }
      }

      checkRgbConsistency(THEME_COLORS);
    });
  });

  describe('Color Utilities', () => {
    it('should get colors by path correctly', () => {
      expect(getColor('brand.violet')).toEqual(THEME_COLORS.brand.violet);
      expect(getColor('dark.bg.primary')).toEqual(THEME_COLORS.dark.bg.primary);
      expect(getColor('nonexistent.path')).toBeNull();
    });

    it('should validate hex colors correctly', () => {
      expect(validateHexColor('#ff4757')).toBe(true);
      expect(validateHexColor('#FFF')).toBe(true);
      expect(validateHexColor('ff4757')).toBe(false);
      expect(validateHexColor('#gggggg')).toBe(false);
      expect(validateHexColor('#12345')).toBe(false);
    });

    it('should convert hex to RGB correctly', () => {
      expect(hexToRgb('#ff4757')).toEqual([255, 71, 87]);
      expect(hexToRgb('#6c5ce7')).toEqual([108, 92, 231]);
      expect(hexToRgb('#invalid')).toBeNull();
    });
  });

  describe('Color Naming Accuracy', () => {
    const colorDescriptionTests = [
      { hex: '#ff4757', expectedTerms: ['red', 'coral', 'vivid'] },
      { hex: '#6c5ce7', expectedTerms: ['purple', 'violet', 'electric'] },
      { hex: '#00cec9', expectedTerms: ['cyan', 'turquoise', 'teal'] },
      { hex: '#fdcb6e', expectedTerms: ['gold', 'yellow', 'warm'] },
    ];

    it.each(colorDescriptionTests)('should have accurate description for $hex', ({ hex, expectedTerms }) => {
      // Find the color in our theme
      function findColorByHex(obj: any): any {
        for (const value of Object.values(obj)) {
          if (value && typeof value === 'object') {
            if ('hex' in value && value.hex === hex) {
              return value;
            }
            const found = findColorByHex(value);
            if (found) return found;
          }
        }
        return null;
      }

      const color = findColorByHex(THEME_COLORS);
      expect(color).toBeTruthy();
      
      if (color) {
        const description = `${color.name} ${color.description || ''}`.toLowerCase();
        const hasExpectedTerm = expectedTerms.some(term => description.includes(term.toLowerCase()));
        expect(hasExpectedTerm).toBe(true);
      }
    });
  });

  describe('Theme Completeness', () => {
    it('should have complete light theme colors', () => {
      expect(THEME_COLORS.light.bg).toBeDefined();
      expect(THEME_COLORS.light.text).toBeDefined();
      expect(THEME_COLORS.light.border).toBeDefined();
      
      ['primary', 'secondary', 'tertiary', 'chat'].forEach(key => {
        expect(THEME_COLORS.light.bg).toHaveProperty(key);
      });
      
      ['primary', 'secondary', 'tertiary'].forEach(key => {
        expect(THEME_COLORS.light.text).toHaveProperty(key);
      });
    });

    it('should have complete dark theme colors', () => {
      expect(THEME_COLORS.dark.bg).toBeDefined();
      expect(THEME_COLORS.dark.text).toBeDefined();
      expect(THEME_COLORS.dark.border).toBeDefined();
      expect(THEME_COLORS.dark.accent).toBeDefined();
      
      ['primary', 'secondary', 'tertiary', 'chat'].forEach(key => {
        expect(THEME_COLORS.dark.bg).toHaveProperty(key);
      });
      
      ['primary', 'secondary', 'tertiary'].forEach(key => {
        expect(THEME_COLORS.dark.text).toHaveProperty(key);
      });
      
      ['primary', 'secondary', 'success', 'warning', 'danger'].forEach(key => {
        expect(THEME_COLORS.dark.accent).toHaveProperty(key);
      });
    });

    it('should have complete chat colors', () => {
      ['user', 'agent', 'system'].forEach(role => {
        expect(THEME_COLORS.chat[role as keyof typeof THEME_COLORS.chat]).toBeDefined();
        expect(THEME_COLORS.chat[role as keyof typeof THEME_COLORS.chat]).toHaveProperty('light');
        expect(THEME_COLORS.chat[role as keyof typeof THEME_COLORS.chat]).toHaveProperty('dark');
      });
    });
  });
});