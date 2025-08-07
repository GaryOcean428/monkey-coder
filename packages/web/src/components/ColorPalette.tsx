import React from 'react';
import { THEME_COLORS } from '../constants/colors';

interface ColorSwatchProps {
  color: {
    hex: string;
    name: string;
    rgb: readonly [number, number, number];
    description?: string;
  };
  label: string;
  showRgb?: boolean;
}

const ColorSwatch: React.FC<ColorSwatchProps> = ({ color, label, showRgb = false }) => (
  <div className="flex items-center space-x-3 p-3 rounded-lg bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700">
    <div 
      className="w-16 h-16 rounded-lg shadow-md border border-gray-300 dark:border-gray-600 flex-shrink-0"
      style={{ backgroundColor: color.hex }}
      title={color.description || color.name}
    />
    <div className="flex-1 min-w-0">
      <p className="font-semibold text-gray-900 dark:text-gray-100 truncate">
        {label}
      </p>
      <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
        {color.name}
      </p>
      <p className="text-xs font-mono text-gray-500 dark:text-gray-500">
        {color.hex}
      </p>
      {showRgb && (
        <p className="text-xs font-mono text-gray-400 dark:text-gray-600">
          rgb({color.rgb.join(', ')})
        </p>
      )}
      {color.description && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 italic">
          {color.description}
        </p>
      )}
    </div>
  </div>
);

interface ColorSectionProps {
  title: string;
  colors: Record<string, any>;
  prefix?: string;
  showRgb?: boolean;
  className?: string;
}

const ColorSection: React.FC<ColorSectionProps> = ({ 
  title, 
  colors, 
  prefix = '', 
  showRgb = false,
  className = ''
}) => {
  const renderColorOrSection = (key: string, value: any): React.ReactNode => {
    if (value && typeof value === 'object') {
      if ('hex' in value) {
        // This is a color object
        return (
          <ColorSwatch 
            key={key}
            color={value}
            label={prefix ? `${prefix}.${key}` : key}
            showRgb={showRgb}
          />
        );
      } else {
        // This is a nested section
        return (
          <div key={key} className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700 pb-1">
              {prefix ? `${prefix}.${key}` : key}
            </h4>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {Object.entries(value).map(([nestedKey, nestedValue]) => 
                renderColorOrSection(nestedKey, nestedValue)
              )}
            </div>
          </div>
        );
      }
    }
    return null;
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 border-b-2 border-gray-300 dark:border-gray-600 pb-2">
        {title}
      </h3>
      <div className="space-y-6">
        {Object.entries(colors).map(([key, value]) => 
          renderColorOrSection(key, value)
        )}
      </div>
    </div>
  );
};

export const ColorPalette: React.FC<{ showRgb?: boolean }> = ({ showRgb = false }) => {
  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 rounded-xl space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Monkey Coder Theme Colors
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Complete color palette with accurate descriptions and usage guidelines
        </p>
        <div className="inline-flex items-center px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 text-sm rounded-full">
          ⚠️ Fixed: "lime" was mislabeled - #6c5ce7 is actually Electric Purple
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <ColorSection 
          title="🎨 Brand Colors" 
          colors={THEME_COLORS.brand}
          showRgb={showRgb}
        />
        
        <ColorSection 
          title="☀️ Light Theme" 
          colors={THEME_COLORS.light}
          showRgb={showRgb}
        />
        
        <ColorSection 
          title="🌙 Dark Theme" 
          colors={THEME_COLORS.dark}
          showRgb={showRgb}
          className="xl:col-span-1"
        />
        
        <ColorSection 
          title="💬 Chat Colors" 
          colors={THEME_COLORS.chat}
          showRgb={showRgb}
        />
      </div>

      <div className="mt-8 space-y-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          🎨 Gradient Previews
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-2">
            <div 
              className="h-16 rounded-lg shadow-sm"
              style={{ background: 'linear-gradient(135deg, #ff4757 0%, #ff7675 25%, #fdcb6e 50%, #00cec9 75%, #a29bfe 100%)' }}
            />
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Brand Gradient</p>
          </div>
          <div className="space-y-2">
            <div 
              className="h-16 rounded-lg shadow-sm"
              style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
            />
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Chat User</p>
          </div>
          <div className="space-y-2">
            <div 
              className="h-16 rounded-lg shadow-sm"
              style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}
            />
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Chat Agent</p>
          </div>
          <div className="space-y-2">
            <div 
              className="h-16 rounded-lg shadow-sm"
              style={{ background: 'radial-gradient(circle at center, rgba(0, 206, 201, 0.3) 0%, transparent 50%)' }}
            />
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Neural Effect</p>
          </div>
        </div>
      </div>

      <div className="mt-8 space-y-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          ⚡ Neon Effects Preview
        </h3>
        <div className="bg-gray-900 rounded-xl p-6 space-y-4">
          <p className="text-gray-300 text-sm mb-4">
            Neon effects work best in dark mode. These examples show the enhanced glow effects available.
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-brand-cyan rounded-lg shadow-neon-cyan animate-glow-cyan mx-auto"></div>
              <p className="text-xs text-cyan-300 font-mono">neon-cyan</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-brand-violet rounded-lg shadow-neon-violet animate-glow-violet mx-auto"></div>
              <p className="text-xs text-violet-300 font-mono">neon-violet</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-brand-coral rounded-lg shadow-neon-coral animate-glow-coral mx-auto"></div>
              <p className="text-xs text-red-300 font-mono">neon-coral</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-brand-purple rounded-lg shadow-neon-purple mx-auto"></div>
              <p className="text-xs text-purple-300 font-mono">neon-purple</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-brand-magenta rounded-lg shadow-neon-magenta mx-auto"></div>
              <p className="text-xs text-pink-300 font-mono">neon-magenta</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-brand-yellow rounded-lg shadow-neon-yellow mx-auto"></div>
              <p className="text-xs text-yellow-300 font-mono">neon-yellow</p>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <h4 className="text-white font-medium">Interactive Neon Buttons:</h4>
            <div className="flex flex-wrap gap-3">
              <button className="bg-brand-cyan text-white px-4 py-2 rounded-lg shadow-neon-cyan hover:shadow-neon-hover-cyan transition-all duration-300 animate-glow-cyan text-sm">
                Cyan Glow
              </button>
              <button className="bg-brand-violet text-white px-4 py-2 rounded-lg shadow-neon-violet hover:shadow-neon-hover-violet transition-all duration-300 animate-glow-violet text-sm">
                Violet Glow
              </button>
              <button className="bg-brand-coral text-white px-4 py-2 rounded-lg shadow-neon-coral hover:shadow-neon-hover-coral transition-all duration-300 animate-glow-coral text-sm">
                Coral Glow
              </button>
              <button className="bg-gradient-to-r from-brand-cyan via-brand-violet to-brand-magenta text-white px-4 py-2 rounded-lg shadow-neon-rainbow animate-glow-rainbow text-sm">
                Rainbow Effect
              </button>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <h4 className="text-white font-medium">Animation Effects:</h4>
            <div className="flex flex-wrap gap-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-brand-cyan rounded-lg animate-neon-flicker text-brand-cyan flex items-center justify-center font-bold text-xs text-white">
                  FLICKER
                </div>
                <p className="text-xs text-gray-400 mt-1">Flicker</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-brand-violet rounded-lg animate-neon-pulse text-brand-violet flex items-center justify-center font-bold text-xs text-white">
                  PULSE
                </div>
                <p className="text-xs text-gray-400 mt-1">Pulse</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-brand-coral rounded-lg animate-neon-breathe text-brand-coral flex items-center justify-center font-bold text-xs text-white">
                  BREATHE
                </div>
                <p className="text-xs text-gray-400 mt-1">Breathe</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-800 border-2 rounded-lg animate-border-glow flex items-center justify-center font-bold text-xs text-white">
                  BORDER
                </div>
                <p className="text-xs text-gray-400 mt-1">Border Glow</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h4 className="font-medium text-blue-900 dark:text-blue-200 mb-2">Usage Guidelines:</h4>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
          <li>• Use <code className="bg-blue-100 dark:bg-blue-800 px-1 rounded">text-brand-violet</code> for the corrected purple color</li>
          <li>• Brand colors work best as accents and highlights</li>
          <li>• Light/dark theme colors provide semantic context</li>
          <li>• Chat colors distinguish message types and roles</li>
          <li>• Always test color combinations for accessibility</li>
        </ul>
      </div>
    </div>
  );
};

export default ColorPalette;