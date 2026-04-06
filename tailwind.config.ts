import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#ffffff',
        bg2: '#f7f7f7',
        bg3: '#ededee',
        bg4: '#e2e2e2',
        ink: '#000000',
        ink2: '#1a1a1a',
        ink3: '#3c3c43',
        ink4: '#999999',
        ink5: '#b2b2b2',
        border: '#e5e5e5',
        bd2: '#d8d8d8',
        blue: { DEFAULT: '#0059b5', hover: '#004a99' },
        red: { DEFAULT: '#d0021b', light: '#ff1744' },
        navy: '#1a3060',
        green2: '#0a5c36',
        amber2: '#b45309',
      },
      fontFamily: {
        condensed: ['var(--font-oswald)', 'Impact', 'sans-serif'],
        body: ['var(--font-inter)', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'monospace'],
      },
      maxWidth: {
        site: '1200px',
      },
      fontSize: {
        '2xs': ['10px', { lineHeight: '1.2' }],
        xs: ['11px', { lineHeight: '1.3' }],
        sm: ['13px', { lineHeight: '1.4' }],
        base: ['14px', { lineHeight: '1.5' }],
        md: ['15px', { lineHeight: '1.35' }],
        lg: ['16px', { lineHeight: '1.3' }],
        xl: ['18px', { lineHeight: '1.15' }],
        '2xl': ['22px', { lineHeight: '1.15' }],
        '3xl': ['28px', { lineHeight: '1.12' }],
        '4xl': ['32px', { lineHeight: '1.1' }],
      },
      borderRadius: {
        pill: '20px',
        round: '100px',
      },
      transitionDuration: {
        fast: '150ms',
        med: '300ms',
      },
      keyframes: {
        'ticker-scroll': {
          from: { transform: 'translateX(100vw)' },
          to: { transform: 'translateX(-100%)' },
        },
        pulsate: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
      animation: {
        ticker: 'ticker-scroll 35s linear infinite',
        pulsate: 'pulsate 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
export default config
