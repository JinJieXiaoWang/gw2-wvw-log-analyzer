/**
 * 主题预设配置
 * 功能：扩展 PrimeVue 的 Aura 主题以实现游戏风格 UI
 * 作者：System
 * 创建日期：2026-04-29
 */

import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';

export const GameThemePreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '{primary.50}',
      100: '{primary.100}',
      200: '{primary.200}',
      300: '{primary.300}',
      400: '{primary.400}',
      500: '{primary.500}',
      600: '{primary.600}',
      700: '{primary.700}',
      800: '{primary.800}',
      900: '{primary.900}',
      950: '{primary.950}'
    },
    colorScheme: {
      light: {
        surface: {
          0: '#ffffff',
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617'
        },
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b'
        }
      },
      dark: {
        surface: {
          0: '#0d0d0f',
          50: '#141417',
          100: '#1a1a1f',
          200: '#222228',
          300: '#2d2d35',
          400: '#3d3d48',
          500: '#606070',
          600: '#7a7a8a',
          700: '#9999a8',
          800: '#b6b6c2',
          900: '#d4d4dc',
          950: '#e8e8ec'
        },
        primary: {
          50: '#0a1420',
          100: '#0d1f30',
          200: '#0a2a40',
          300: '#003864',
          400: '#0057a8',
          500: '#165DFF',
          600: '#3d78ff',
          700: '#6d9bff',
          800: '#9ebbff',
          900: '#cddcff',
          950: '#e6ecff'
        }
      }
    }
  }
});
