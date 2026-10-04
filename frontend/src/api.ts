import type { Batch, Page } from './types'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(payload.detail ?? 'Request failed')
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  reset: () => request<void>('/api/session/reset', { method: 'POST' }),
  createDemo: () => request<Batch>('/api/batches/demo', { method: 'POST' }),
  process: (batchId: string) => request<Batch>(`/api/batches/${batchId}/process`, { method: 'POST' }),
  clear: (batchId: string) => request<void>(`/api/batches/${batchId}`, { method: 'DELETE' }),
  override: (pageId: string, note: string) => request<Page>(`/api/pages/${pageId}/approve-warning`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ note }),
  }),
  upload: (file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<Batch>('/api/batches/upload', { method: 'POST', body })
  },
  remove: (pageId: string) => request<void>(`/api/pages/${pageId}`, { method: 'DELETE' }),
  audit: async (batchId: string) => {
    const response = await fetch(`/api/batches/${batchId}/audit`)
    if (!response.ok) throw new Error('Unable to export audit')
    return response.blob()
  },
}
