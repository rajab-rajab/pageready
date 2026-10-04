export type PageStatus = 'Queued' | 'Analyzing' | 'Corrected' | 'Rescan requested' | 'Needs review' | 'Approved' | 'Approved with warning'

export interface Metrics {
  width: number
  height: number
  skew_angle_deg: number
  skew_confidence: number
  blur_laplacian_var: number
  contrast_std_dev: number
  content_touches_frame: boolean
  analysis_notes: string[]
}

export interface TraceEvent {
  event_id: string
  timestamp_utc: string
  event_type: string
  actor: 'system' | 'clerk'
  summary: string
  pipeline_version: string
  policy_version: string
  detail: Record<string, unknown>
}

export interface Page {
  id: string
  filename: string
  source: 'demo' | 'upload'
  queue_index: number
  status: PageStatus
  error?: { code: string; message: string } | null
  original_image_url?: string | null
  processed_image_url?: string | null
  metrics?: Metrics | null
  warning_reason?: string | null
  trace: TraceEvent[]
  override_note?: string | null
}

export interface Batch {
  id: string
  processing: boolean
  pages: Page[]
}
