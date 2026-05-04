export interface AIReport {
  id: number
  report_type: 'fight' | 'member' | 'build'
  target_type: string
  target_id: number
  title: string
  content: string
  insights: AIInsight[]
  recommendations: AIRecommendation[]
  created_at: string
  updated_at: string
}

export interface AIInsight {
  category: string
  description: string
  severity: 'info' | 'warning' | 'critical'
  metrics?: Record<string, number>
}

export interface AIRecommendation {
  priority: 'high' | 'medium' | 'low'
  action: string
  expected_impact: string
}

export interface TrendAnalysis {
  period: string
  metrics: TrendMetric[]
}

export interface TrendMetric {
  name: string
  values: number[]
  labels: string[]
  trend: 'increasing' | 'decreasing' | 'stable'
  change_percentage: number
}

export interface Suggestion {
  id: number
  category: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  created_at: string
}

export interface ReportsListParams {
  page?: number
  page_size?: number
  report_type?: string | null
  target_type?: string | null
}