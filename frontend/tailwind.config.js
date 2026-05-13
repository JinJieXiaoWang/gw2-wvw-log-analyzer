/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 主色调 - 使用CSS变量支持主题切换
        primary: {
          DEFAULT: 'var(--color-primary)',
          light: 'var(--color-primary-light)',
          dark: 'var(--color-primary-dark)',
          'alpha-10': 'var(--color-primary-alpha-10)',
          'alpha-20': 'var(--color-primary-alpha-20)',
          'alpha-30': 'var(--color-primary-alpha-30)',
        },
        // 辅助色
        secondary: {
          DEFAULT: 'var(--color-secondary)',
          light: 'var(--color-secondary-light)',
          dark: 'var(--color-secondary-dark)',
          'alpha-10': 'var(--color-secondary-alpha-10)',
          'alpha-20': 'var(--color-secondary-alpha-20)',
        },
        // 中性色
        neutral: {
          bg: 'var(--color-bg)',
          'bg-secondary': 'var(--color-bg-secondary)',
          card: 'var(--color-card)',
          'card-hover': 'var(--color-card-hover)',
          'card-active': 'var(--color-card-active)',
          border: 'var(--color-border)',
          'border-light': 'var(--color-border-light)',
          text: 'var(--color-text)',
          'text-secondary': 'var(--color-text-secondary)',
          'text-disabled': 'var(--color-text-disabled)',
          'text-inverse': 'var(--color-text-inverse)',
        },
        // 状态色
        status: {
          success: 'var(--color-success)',
          'success-alpha-10': 'var(--color-success-alpha-10)',
          warning: 'var(--color-warning)',
          'warning-alpha-10': 'var(--color-warning-alpha-10)',
          error: 'var(--color-error)',
          'error-alpha-10': 'var(--color-error-alpha-10)',
          info: 'var(--color-info)',
          'info-alpha-10': 'var(--color-info-alpha-10)',
        },
        // AI功能专用色
        ai: {
          DEFAULT: 'var(--color-ai)',
          light: 'var(--color-ai-light)',
          dark: 'var(--color-ai-dark)',
          'alpha-10': 'var(--color-ai-alpha-10)',
          'alpha-20': 'var(--color-ai-alpha-20)',
          'alpha-30': 'var(--color-ai-alpha-30)',
        },
        
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', 'system-ui', '-apple-system', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'sm': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.25rem',
      },
      transitionDuration: {
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '350': '350ms',
      },
      boxShadow: {
        // 游戏风格发光阴影
        'glow-primary': '0 0 30px var(--color-primary-alpha-30)',
        'glow-secondary': '0 0 30px var(--color-secondary-alpha-30)',
        'glow-ai': '0 0 30px var(--color-ai-alpha-30)',
        'glow-success': '0 0 30px var(--color-success-alpha-10)',
        'glow-error': '0 0 30px var(--color-error-alpha-10)',
        // 阴影透明度变体
        'glow-primary-alpha-50': '0 0 30px var(--color-primary-alpha-50)',
        'glow-primary-alpha-30': '0 0 30px var(--color-primary-alpha-30)',
      },
      // PrimeVue组件对齐配置
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px var(--color-primary-alpha-30)' },
          '50%': { boxShadow: '0 0 40px var(--color-primary-alpha-50)' },
        },
      },
    },
  },
  plugins: [],
  // 优化性能配置
  darkMode: 'class',
  // 兼容PrimeVue的主题系统
  corePlugins: {
    preflight: true,
  },
};
