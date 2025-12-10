/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
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
        // Background colors
        background: {
          primary: '#0A0E1A',
          secondary: '#131825',
          tertiary: '#1C2333',
        },
        // Glass effect
        glass: {
          bg: 'rgba(28, 35, 51, 0.7)',
          border: 'rgba(255, 255, 255, 0.1)',
        },
        // Accent colors
        accent: {
          primary: '#00D9FF',
          secondary: '#8B5CF6',
          glow: 'rgba(0, 217, 255, 0.25)',
        },
        // Severity colors
        severity: {
          critical: '#EF4444',
          high: '#F59E0B',
          medium: '#8B5CF6',
          low: '#10B981',
        },
        // Text colors
        text: {
          primary: '#F8FAFC',
          secondary: '#94A3B8',
          tertiary: '#64748B',
        },
        // Status colors
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Clash Display', 'Inter', 'sans-serif'],
      },
      fontSize: {
        'display': ['56px', { lineHeight: '1.1', fontWeight: '700' }],
        'h1': ['36px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['28px', { lineHeight: '1.3', fontWeight: '600' }],
        'h3': ['20px', { lineHeight: '1.4', fontWeight: '600' }],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      borderRadius: {
        'lg': '16px',
        'xl': '24px',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glow-primary': '0 0 20px rgba(0, 217, 255, 0.25)',
        'glow-critical': '0 0 20px rgba(239, 68, 68, 0.25)',
        'glow-success': '0 0 20px rgba(16, 185, 129, 0.25)',
      },
      backdropBlur: {
        'glass': '10px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}

