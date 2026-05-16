import { formatBytes } from '@/utils/core/helpers'

export const formatFileSize = formatBytes

export function getRarityClass(status: string): string {
  const map: Record<string, string> = {
    completed: 'bg-gradient-to-br from-rarity-legendary to-primary',
    parsing: 'bg-gradient-to-br from-rarity-exotic to-secondary',
    failed: 'bg-gradient-to-br from-status-error to-status-error/70',
    pending: 'bg-gradient-to-br from-neutral-border to-neutral-bg',
  }
  return map[status] || 'bg-gradient-to-br from-neutral-border to-neutral-bg'
}

export function getStatusDotClass(status: string): string {
  const map: Record<string, string> = {
    completed: 'status-dot-success',
    parsing: 'status-dot-warning',
    failed: 'status-dot-error',
    pending: 'status-dot-pending',
  }
  return map[status] || 'status-dot-pending'
}

export function getStatusBadgeClass(status: string): string {
  const map: Record<string, string> = {
    completed: 'game-badge',
    parsing: 'game-badge',
    failed: 'game-badge',
    pending: 'game-badge',
  }
  return map[status] || 'game-badge'
}
