import React from 'react';
import { NEON_BUTTON_CLASSES } from '../constants/colors';

interface NeonDemoProps {
  title: string;
  description: string;
  className: string;
  children: React.ReactNode;
}

const NeonDemo: React.FC<NeonDemoProps> = ({ title, description, className, children }) => (
  <div className="bg-gray-900 rounded-xl p-6 border border-gray-700">
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <div className={`flex items-center justify-center p-8 rounded-lg bg-black/50 ${className}`}>
        {children}
      </div>
      <div className="text-xs text-gray-500 font-mono bg-gray-800 p-2 rounded">
        className="{className}"
      </div>
    </div>
  </div>
);

export const NeonShowcase: React.FC = () => {
  return (
    <div className="space-y-8 p-6 bg-gray-950 rounded-2xl">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-white">
          ⚡ Neon Effects Showcase
        </h2>
        <p className="text-gray-400">
          Comprehensive neon glow effects with animations for modern UI design
        </p>
      </div>

      {/* Subtle Neon Effects */}
      <section className="space-y-4">
        <h3 className="text-xl font-bold text-cyan-300 mb-4">🌟 Subtle Neon Glows</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <NeonDemo
            title="Cyan Glow"
            description="Primary brand color with subtle glow"
            className=""
          >
            <div className="w-24 h-24 bg-brand-cyan rounded-xl shadow-neon-cyan flex items-center justify-center text-white font-bold">
              CYAN
            </div>
          </NeonDemo>

          <NeonDemo
            title="Violet Glow"
            description="Electric purple with soft illumination"
            className=""
          >
            <div className="w-24 h-24 bg-brand-violet rounded-xl shadow-neon-violet flex items-center justify-center text-white font-bold">
              VIOLET
            </div>
          </NeonDemo>

          <NeonDemo
            title="Coral Glow"
            description="Warm coral with vibrant edge"
            className=""
          >
            <div className="w-24 h-24 bg-brand-coral rounded-xl shadow-neon-coral flex items-center justify-center text-white font-bold">
              CORAL
            </div>
          </NeonDemo>
        </div>
      </section>

      {/* Intense Neon Effects */}
      <section className="space-y-4">
        <h3 className="text-xl font-bold text-violet-300 mb-4">⚡ Intense Neon Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <NeonDemo
            title="Intense Cyan"
            description="Maximum intensity glow effect"
            className=""
          >
            <div className="w-24 h-24 bg-brand-cyan rounded-xl shadow-neon-cyan-intense flex items-center justify-center text-white font-bold">
              INTENSE
            </div>
          </NeonDemo>

          <NeonDemo
            title="Intense Violet"
            description="High-intensity purple glow"
            className=""
          >
            <div className="w-24 h-24 bg-brand-violet rounded-xl shadow-neon-violet-intense flex items-center justify-center text-white font-bold">
              INTENSE
            </div>
          </NeonDemo>

          <NeonDemo
            title="Rainbow Neon"
            description="Multi-color glow combination"
            className=""
          >
            <div className="w-24 h-24 bg-gradient-to-br from-brand-cyan via-brand-violet to-brand-magenta rounded-xl shadow-neon-rainbow flex items-center justify-center text-white font-bold">
              RAINBOW
            </div>
          </NeonDemo>
        </div>
      </section>

      {/* Animated Neon Effects */}
      <section className="space-y-4">
        <h3 className="text-xl font-bold text-magenta-300 mb-4">🎬 Animated Neon Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <NeonDemo
            title="Flicker Effect"
            description="Realistic neon tube flickering"
            className=""
          >
            <div className="w-20 h-20 bg-brand-cyan rounded-lg flex items-center justify-center text-white font-bold text-sm animate-neon-flicker text-brand-cyan">
              FLICKER
            </div>
          </NeonDemo>

          <NeonDemo
            title="Pulse Effect"
            description="Steady pulsing glow"
            className=""
          >
            <div className="w-20 h-20 bg-brand-violet rounded-lg flex items-center justify-center text-white font-bold text-sm animate-neon-pulse text-brand-violet">
              PULSE
            </div>
          </NeonDemo>

          <NeonDemo
            title="Breathe Effect"
            description="Gentle breathing animation"
            className=""
          >
            <div className="w-20 h-20 bg-brand-coral rounded-lg flex items-center justify-center text-white font-bold text-sm animate-neon-breathe text-brand-coral">
              BREATHE
            </div>
          </NeonDemo>

          <NeonDemo
            title="Rainbow Cycle"
            description="Color-cycling animation"
            className=""
          >
            <div className="w-20 h-20 bg-gray-800 rounded-lg flex items-center justify-center text-white font-bold text-sm animate-glow-rainbow">
              CYCLE
            </div>
          </NeonDemo>
        </div>
      </section>

      {/* Interactive Neon Buttons */}
      <section className="space-y-4">
        <h3 className="text-xl font-bold text-yellow-300 mb-4">🎯 Interactive Neon Buttons</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <NeonDemo
            title="Cyan Button"
            description="Hover for enhanced glow"
            className=""
          >
            <button className={`${NEON_BUTTON_CLASSES.cyan} px-6 py-3 rounded-lg font-semibold`}>
              Click Me
            </button>
          </NeonDemo>

          <NeonDemo
            title="Violet Button"
            description="Electric purple interaction"
            className=""
          >
            <button className={`${NEON_BUTTON_CLASSES.violet} px-6 py-3 rounded-lg font-semibold`}>
              Interact
            </button>
          </NeonDemo>

          <NeonDemo
            title="Coral Button"
            description="Warm coral with glow"
            className=""
          >
            <button className={`${NEON_BUTTON_CLASSES.coral} px-6 py-3 rounded-lg font-semibold`}>
              Engage
            </button>
          </NeonDemo>

          <NeonDemo
            title="Rainbow Button"
            description="Multi-color gradient effect"
            className=""
          >
            <button className={`${NEON_BUTTON_CLASSES.rainbow} px-6 py-3 rounded-lg font-semibold`}>
              Amazing
            </button>
          </NeonDemo>
        </div>
      </section>

      {/* Border Glow Effects */}
      <section className="space-y-4">
        <h3 className="text-xl font-bold text-purple-300 mb-4">🔲 Border Glow Effects</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <NeonDemo
            title="Animated Border"
            description="Color-cycling border glow"
            className=""
          >
            <div className="w-32 h-20 border-2 rounded-lg animate-border-glow flex items-center justify-center text-white font-semibold">
              Border Glow
            </div>
          </NeonDemo>

          <NeonDemo
            title="Card with Neon"
            description="Complete card design with neon accents"
            className=""
          >
            <div className="bg-gray-800 border border-brand-cyan shadow-neon-cyan rounded-lg p-4 max-w-xs">
              <h4 className="text-brand-cyan font-bold mb-2 animate-glow-cyan">Neon Card</h4>
              <p className="text-gray-300 text-sm">This card uses neon effects for a futuristic appearance.</p>
              <button className="mt-3 px-3 py-1 bg-brand-violet text-white rounded shadow-neon-violet hover:shadow-neon-hover-violet transition-all text-sm">
                Action
              </button>
            </div>
          </NeonDemo>
        </div>
      </section>

      {/* Usage Guide */}
      <section className="space-y-4">
        <h3 className="text-xl font-bold text-green-300 mb-4">📖 Usage Guide</h3>
        <div className="bg-gray-800 rounded-xl p-6 space-y-4">
          <h4 className="text-white font-semibold mb-3">Available Neon Classes:</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h5 className="text-cyan-300 font-medium">Subtle Glow Effects:</h5>
              <ul className="text-sm text-gray-400 space-y-1 font-mono">
                <li>shadow-neon-cyan</li>
                <li>shadow-neon-violet</li>
                <li>shadow-neon-coral</li>
                <li>shadow-neon-purple</li>
                <li>shadow-neon-magenta</li>
                <li>shadow-neon-yellow</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h5 className="text-violet-300 font-medium">Intense Effects:</h5>
              <ul className="text-sm text-gray-400 space-y-1 font-mono">
                <li>shadow-neon-cyan-intense</li>
                <li>shadow-neon-violet-intense</li>
                <li>shadow-neon-coral-intense</li>
                <li>shadow-neon-rainbow</li>
                <li>shadow-neon-brand</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h5 className="text-coral-300 font-medium">Hover Effects:</h5>
              <ul className="text-sm text-gray-400 space-y-1 font-mono">
                <li>hover:shadow-neon-hover-cyan</li>
                <li>hover:shadow-neon-hover-violet</li>
                <li>hover:shadow-neon-hover-coral</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h5 className="text-magenta-300 font-medium">Animations:</h5>
              <ul className="text-sm text-gray-400 space-y-1 font-mono">
                <li>animate-neon-flicker</li>
                <li>animate-neon-pulse</li>
                <li>animate-neon-breathe</li>
                <li>animate-glow-rainbow</li>
                <li>animate-border-glow</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 p-4 bg-black/30 rounded-lg">
            <h5 className="text-yellow-300 font-medium mb-2">Example Usage:</h5>
            <code className="text-green-400 text-sm">
              {`<button className="bg-brand-cyan text-white shadow-neon-cyan hover:shadow-neon-hover-cyan animate-glow-cyan transition-all duration-300 px-6 py-3 rounded-lg">
  Neon Button
</button>`}
            </code>
          </div>
        </div>
      </section>
    </div>
  );
};

export default NeonShowcase;