/**
 * 设计令牌常量
 * 功能：集中管理设计系统的所有设计令牌，确保样式一致性
 * 作者：System
 * 创建日期：2024-01-15
 */

/* ============================================
   颜色令牌 (Color Tokens)
   ============================================ */
export const Colors = {
  primary: {
    DEFAULT: '#165DFF',
    light: '#4080FF',
    dark: '#0E42D2',
    alpha10: 'rgba(22, 93, 255, 0.1)',
    alpha20: 'rgba(22, 93, 255, 0.2)'
  },
  secondary: {
    DEFAULT: '#FF7D00',
    light: '#FF9A2E',
    dark: '#D25F00',
    alpha10: 'rgba(255, 125, 0, 0.1)'
  },
  neutral: {
    bg: '#141414',
    card: '#2A2A2A',
    cardHover: '#333333',
    border: '#3D3D3D',
    borderLight: '#4D4D4D',
    text: '#E5E5E5',
    textSecondary: '#909399',
    textDisabled: '#666666'
  },
  status: {
    success: '#00B42A',
    successAlpha10: 'rgba(0, 180, 42, 0.1)',
    warning: '#FF7D00',
    warningAlpha10: 'rgba(255, 125, 0, 0.1)',
    error: '#F53F3F',
    errorAlpha10: 'rgba(245, 63, 63, 0.1)',
    info: '#0FCEF5',
    infoAlpha10: 'rgba(15, 206, 245, 0.1)'
  },
  ai: {
    DEFAULT: '#00C896',
    alpha10: 'rgba(0, 200, 150, 0.1)',
    alpha20: 'rgba(0, 200, 150, 0.2)'
  }
} as const

/* ============================================
   字体令牌 (Typography Tokens)
   ============================================ */
export const Typography = {
  fontFamily: {
    DEFAULT: "'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', Consolas, monospace"
  },
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem'
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75
  }
} as const

/* ============================================
   间距令牌 (Spacing Tokens)
   ============================================ */
export const Spacing = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
  24: '6rem'
} as const

/* ============================================
   圆角令牌 (Border Radius Tokens)
   ============================================ */
export const BorderRadius = {
  none: '0',
  sm: '0.25rem',
  DEFAULT: '0.375rem',
  md: '0.5rem',
  lg: '0.75rem',
  xl: '1rem',
  '2xl': '1.5rem',
  full: '9999px'
} as const

/* ============================================
   阴影令牌 (Shadow Tokens)
   ============================================ */
export const Shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
  DEFAULT: '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.6)',
  glow: {
    primary: '0 0 20px rgba(22, 93, 255, 0.3)',
    secondary: '0 0 20px rgba(255, 125, 0, 0.3)',
    ai: '0 0 20px rgba(0, 200, 150, 0.3)'
  }
} as const

/* ============================================
   过渡动画令牌 (Transition Tokens)
   ============================================ */
export const Transitions = {
  fast: '150ms ease',
  DEFAULT: '200ms ease',
  slow: '300ms ease',
  spring: '300ms cubic-bezier(0.34, 1.56, 0.64, 1)'
} as const

/* ============================================
   Z-Index 令牌 (Z-Index Tokens)
   ============================================ */
export const ZIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070
} as const

/* ============================================
   断点令牌 (Breakpoint Tokens)
   ============================================ */
export const Breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
} as const

/* ============================================
   动画令牌 (Animation Tokens)
   ============================================ */
export const Animations = {
  spin: '1s linear infinite',
  pulse: '2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
  bounce: '1s infinite',
  glowPulse: '2s ease-in-out infinite',
  slideInUp: '0.4s ease-out forwards',
  zoomIn: '0.3s ease-out forwards'
} as const

/* ============================================
   组件尺寸令牌 (Component Size Tokens)
   ============================================ */
export const ComponentSizes = {
  button: {
    sm: { height: '2rem', padding: '0.5rem 1rem', fontSize: '0.875rem' },
    md: { height: '2.5rem', padding: '0.625rem 1.5rem', fontSize: '1rem' },
    lg: { height: '3rem', padding: '0.75rem 2rem', fontSize: '1.125rem' }
  },
  input: {
    sm: { height: '2rem', fontSize: '0.875rem' },
    md: { height: '2.5rem', fontSize: '1rem' },
    lg: { height: '3rem', fontSize: '1.125rem' }
  },
  sidebar: {
    collapsed: '4rem',
    expanded: '15rem'
  }
} as const

/* ============================================
   职业配置 (Profession Config)
   ============================================ */
export const ProfessionConfig = {
  colors: {
    '战士': '#E85000',
    '守护者': '#FFB400',
    '潜行者': '#6B2D5C',
    '工程师': '#FF9B1A',
    '元素使': '#19B1E5',
    '幻术师': '#7B5BA6',
    '唤灵师': '#0078E8',
    '游侠': '#A4C600',
    '魂武师': '#8A4BAF',
    '铸剑师': '#D4A574'
  },
  icons: {
    '战士': 'pi-sword',
    '守护者': 'pi-shield',
    '潜行者': 'pi-eye',
    '工程师': 'pi-cog',
    '元素使': 'pi-bolt',
    '幻术师': 'pi-star',
    '唤灵师': 'pi-heart',
    '游侠': 'pi-flag',
    '魂武师': 'pi-sun',
    '铸剑师': 'pi-box'
  }
} as const

/* ============================================
   地图配置 (Map Config)
   ============================================ */
export const MapConfig = {
  BL: { name: '蓝色边境', abbreviation: 'BL', color: '#165DFF' },
  EBG: { name: '永恒战场', abbreviation: 'EBG', color: '#FF7D00' },
  OG: { name: '荒漠绿洲', abbreviation: 'OG', color: '#00B42A' }
} as const

/* ============================================
   日期格式配置 (Date Format Config)
   ============================================ */
export const DateFormat = {
  default: 'YYYY-MM-DD HH:mm:ss',
  date: 'YYYY-MM-DD',
  time: 'HH:mm:ss',
  short: 'MM/DD HH:mm',
  full: 'YYYY年MM月DD日 HH:mm'
} as const

/* ============================================
   分页配置 (Pagination Config)
   ============================================ */
export const PaginationConfig = {
  pageSizes: [10, 20, 50, 100],
  defaultPageSize: 20
} as const

/* ============================================
   导出所有令牌
   ============================================ */
export const DesignTokens = {
  Colors,
  Typography,
  Spacing,
  BorderRadius,
  Shadows,
  Transitions,
  ZIndex,
  Breakpoints,
  Animations,
  ComponentSizes,
  ProfessionConfig,
  MapConfig,
  DateFormat,
  PaginationConfig
} as const

export default DesignTokens
