/**
 * 主题配置常量
 * 功能：集中管理所有游戏风格主题配置，支持PrimeUIX多主题生态系统
 * 作者：System
 * 创建日期：2026-04-28
 * 更新：2026-04-29 - 添加PrimeUIX预设配置
 */

export type ThemePresetType = 'aura' | 'lara' | 'material' | 'nora';

export interface ThemeColorConfig {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  secondaryLight: string;
  secondaryDark: string;
  bg: string;
  bgSecondary: string;
  card: string;
  cardHover: string;
  cardActive: string;
  border: string;
  borderLight: string;
  text: string;
  textSecondary: string;
  textDisabled: string;
  textInverse: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  ai: string;
  accent: string;
  highlight: string;
  glow: string;
  shadow: string;
}

export interface ThemeTypographyConfig {
  fontFamily: string;
  fontSize: {
    base: string;
    header: string;
  };
}

export interface ThemeEffectsConfig {
  glow: string;
  shadow: string;
}

export interface ThemeConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  previewGradient: string;
  preset: ThemePresetType;
  colors: ThemeColorConfig;
  typography?: ThemeTypographyConfig;
  effects?: ThemeEffectsConfig;
}

export const GameThemes: ThemeConfig[] = [
  {
    id: 'guildwars',
    name: '激战2经典',
    description: '原始游戏风格，深色魔幻主题',
    icon: 'pi-swords',
    previewGradient: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
    preset: 'aura',
    colors: {
      primary: '#4A6FA5',
      primaryLight: '#6B8EBF',
      primaryDark: '#2D4A6F',
      secondary: '#FFD700',
      secondaryLight: '#FFE047',
      secondaryDark: '#D4A800',
      bg: '#0D0D0F',
      bgSecondary: '#141417',
      card: '#1A1A1F',
      cardHover: '#222228',
      cardActive: '#2A2A32',
      border: '#2D2D35',
      borderLight: '#3D3D48',
      text: '#F0F0F5',
      textSecondary: '#A0A0B0',
      textDisabled: '#606070',
      textInverse: '#0D0D0F',
      success: '#00D68F',
      warning: '#FFAA00',
      error: '#FF4D6A',
      info: '#00B4FF',
      ai: '#00E5C0',
      accent: '#FFD700',
      highlight: '#4A6FA5',
      glow: 'rgba(74, 111, 165, 0.4)',
      shadow: 'rgba(0, 0, 0, 0.5)'
    }
  },
  {
    id: 'flame-legion',
    name: '烈焰军团',
    description: '火元素主题，热情奔放的战斗风格',
    icon: 'pi-fire',
    previewGradient: 'linear-gradient(135deg, #1a0a0a 0%, #2d1313 50%, #4a1919 100%)',
    preset: 'aura',
    colors: {
      primary: '#E85D04',
      primaryLight: '#FF7D33',
      primaryDark: '#B84402',
      secondary: '#FF6B35',
      secondaryLight: '#FF8C5A',
      secondaryDark: '#CC4A00',
      bg: '#0D0505',
      bgSecondary: '#140A0A',
      card: '#1A1010',
      cardHover: '#251515',
      cardActive: '#302020',
      border: '#3D1F1F',
      borderLight: '#5D2F2F',
      text: '#F5E6E0',
      textSecondary: '#C0A090',
      textDisabled: '#705040',
      textInverse: '#0D0505',
      success: '#00D68F',
      warning: '#FFAA00',
      error: '#FF4D6A',
      info: '#00B4FF',
      ai: '#FF6B35',
      accent: '#FFAA00',
      highlight: '#E85D04',
      glow: 'rgba(232, 93, 4, 0.4)',
      shadow: 'rgba(232, 93, 4, 0.3)'
    }
  },
  {
    id: 'frost-dragon',
    name: '冰霜巨龙',
    description: '冰元素主题，冷峻高贵的冰霜风格',
    icon: 'pi-snowflake',
    previewGradient: 'linear-gradient(135deg, #0a1420 0%, #0d1f30 50%, #0a2a40 100%)',
    preset: 'aura',
    colors: {
      primary: '#00B4FF',
      primaryLight: '#4DD0FF',
      primaryDark: '#0088CC',
      secondary: '#E0FFFF',
      secondaryLight: '#FFFFFF',
      secondaryDark: '#B3E5EC',
      bg: '#050A10',
      bgSecondary: '#0A1420',
      card: '#101A28',
      cardHover: '#182838',
      cardActive: '#203850',
      border: '#204060',
      borderLight: '#306080',
      text: '#E0F4FF',
      textSecondary: '#80B0D0',
      textDisabled: '#507090',
      textInverse: '#050A10',
      success: '#00E5C0',
      warning: '#FFD700',
      error: '#FF6B6B',
      info: '#87CEEB',
      ai: '#00E5FF',
      accent: '#00E5FF',
      highlight: '#00B4FF',
      glow: 'rgba(0, 180, 255, 0.4)',
      shadow: 'rgba(0, 180, 255, 0.2)'
    }
  },
  {
    id: 'dark-void',
    name: '暗黑虚空',
    description: '虚空主题，深紫与宇宙级的深邃神秘风格',
    icon: 'pi-moon',
    previewGradient: 'linear-gradient(135deg, #050510 0%, #0a0a20 50%, #150a25 100%)',
    preset: 'aura',
    colors: {
      primary: '#9B59B6',
      primaryLight: '#B47ED4',
      primaryDark: '#6E3A7E',
      secondary: '#E040FB',
      secondaryLight: '#E870FF',
      secondaryDark: '#A800C0',
      bg: '#050508',
      bgSecondary: '#080810',
      card: '#0F0F18',
      cardHover: '#181828',
      cardActive: '#252538',
      border: '#252540',
      borderLight: '#3A3A60',
      text: '#E8E0F0',
      textSecondary: '#A090C0',
      textDisabled: '#605080',
      textInverse: '#050508',
      success: '#00FF9F',
      warning: '#FFD700',
      error: '#FF4D6A',
      info: '#8B5CF6',
      ai: '#C040FF',
      accent: '#E040FB',
      highlight: '#9B59B6',
      glow: 'rgba(155, 89, 182, 0.4)',
      shadow: 'rgba(155, 89, 182, 0.3)'
    }
  },
  {
    id: 'light-ascalon',
    name: '阿斯卡隆光明',
    description: '浅色主题，明亮清爽的视觉体验',
    icon: 'pi-sun',
    previewGradient: 'linear-gradient(135deg, #ffffff 0%, #f5f7fa 50%, #e4e8ec 100%)',
    preset: 'lara',
    colors: {
      primary: '#2563EB',
      primaryLight: '#3B82F6',
      primaryDark: '#1D4ED8',
      secondary: '#DC2626',
      secondaryLight: '#EF4444',
      secondaryDark: '#B91C1C',
      bg: '#FFFFFF',
      bgSecondary: '#F5F7FA',
      card: '#FFFFFF',
      cardHover: '#F8FAFC',
      cardActive: '#F1F5F9',
      border: '#E2E8F0',
      borderLight: '#F1F5F9',
      text: '#1E293B',
      textSecondary: '#64748B',
      textDisabled: '#94A3B8',
      textInverse: '#FFFFFF',
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#3B82F6',
      ai: '#06B6D4',
      accent: '#2563EB',
      highlight: '#3B82F6',
      glow: 'rgba(37, 99, 235, 0.3)',
      shadow: 'rgba(0, 0, 0, 0.1)'
    }
  }
];

export const DEFAULT_THEME_ID = 'guildwars';

export function getThemeById(themeId: string): ThemeConfig | undefined {
  return GameThemes.find(t => t.id === themeId);
}

export function getDefaultTheme(): ThemeConfig {
  return GameThemes.find(t => t.id === DEFAULT_THEME_ID) || GameThemes[0];
}
