import { ChangeEvent, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import type { Batch, Page, PageStatus } from './types'

const statusClass: Record<PageStatus, string> = {
  Queued: 'queued', Analyzing: 'analyzing', Corrected: 'corrected', 'Rescan requested': 'warning',
  'Needs review': 'warning', Approved: 'approved', 'Approved with warning': 'override',
}

const sleep = (milliseconds: number) => new Promise(resolve => window.setTimeout(resolve, milliseconds))

function formatMetric(value: number | undefined, digits = 1) {
  return value === undefined ? '—' : value.toFixed(digits)
}

export default function App() {
  const [batch, setBatch] = useState<Batch | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [sessionReady, setSessionReady] = useState(false)
  const [note, setNote] = useState('')
  const [error, setError] = useState<string | null>(null)

  const selected = useMemo(() => batch?.pages.find(page => page.id === selectedId) ?? batch?.pages[0] ?? null, [batch, selectedId])

  useEffect(() => {
    api.reset().catch(reason => setError(reason instanceof Error ? reason.message : 'Unable to reset local session'))
      .finally(() => setSessionReady(true))
  }, [])

  const updatePage = (id: string, patch: Partial<Page>) => setBatch(current => current && ({ ...current, pages: current.pages.map(page => page.id === id ? { ...page, ...patch } : page) }))

  async function loadDemo() {
    try {
      setBusy(true); setError(null)
      const created = await api.createDemo()
      setBatch(created); setSelectedId(created.pages[0]?.id ?? null)
      const completed = await api.process(created.id)
      for (const finalPage of completed.pages) {
        setSelectedId(finalPage.id)
        updatePage(finalPage.id, { ...finalPage, status: 'Analyzing' })
        await sleep(420)
        if (finalPage.processed_image_url) {
          updatePage(finalPage.id, { ...finalPage, status: 'Corrected' })
          await sleep(460)
        }
        updatePage(finalPage.id, finalPage)
        await sleep(220)
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to load demo')
    } finally { setBusy(false) }
  }

  async function uploadFile(event: ChangeEvent<HTMLInputElement>, replacingId?: string) {
    const file = event.target.files?.[0]
    if (!file) return
    try {
      setError(null)
      const uploaded = await api.upload(file)
      if (replacingId) await api.remove(replacingId)
      const refreshed = replacingId
        ? { ...uploaded, pages: uploaded.pages.filter(page => page.id !== replacingId).map((page, index) => ({ ...page, queue_index: index })) }
        : uploaded
      setBatch(refreshed)
      setSelectedId(refreshed.pages.at(-1)?.id ?? null)

      // Run newly uploaded pages through the same audited policy path as the demo.
      // Without this request, successful uploads stayed in the queued state.
      const completed = await api.process(refreshed.id)
      setBatch(completed)
      setSelectedId(completed.pages.at(-1)?.id ?? null)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Upload failed') }
    finally { event.target.value = '' }
  }

  async function approveWarning() {
    if (!selected || !note.trim()) return
    try {
      const page = await api.override(selected.id, note)
      updatePage(page.id, {
        ...page,
        original_image_url: selected.original_image_url,
        processed_image_url: selected.processed_image_url,
      })
      setNote('')
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Override failed') }
  }

  async function exportAudit() {
    if (!batch) return
    try {
      const blob = await api.audit(batch.id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url; link.download = 'pageready-audit.json'; link.click(); URL.revokeObjectURL(url)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Audit export failed') }
  }

  async function clearQueue() {
    if (!batch) return
    try { await api.clear(batch.id); setBatch(null); setSelectedId(null); setNote(''); setError(null) }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to clear batch') }
  }

  async function removePage(pageId: string) {
    try {
      await api.remove(pageId)
      setBatch(current => current && ({ ...current, pages: current.pages.filter(page => page.id !== pageId).map((page, index) => ({ ...page, queue_index: index })) }))
      if (selectedId === pageId) setSelectedId(null)
    } catch (reason) { setError(reason instanceof Error ? reason.message : 'Unable to remove file') }
  }

  const resolved = batch?.pages.filter(page => page.status !== 'Queued' && page.status !== 'Analyzing').length ?? 0
  const summary = batch && resolved === batch.pages.length
    ? `${batch.pages.filter(page => page.status === 'Approved').length} Approved (${batch.pages.filter(page => page.processed_image_url).length} Auto-Corrected) · ${batch.pages.filter(page => page.status === 'Rescan requested').length} Rescan Requested · ${batch.pages.filter(page => page.status === 'Needs review').length} Needs Review`
    : null

  return <main className="app-shell">
    <header className="topbar">
      <div><p className="eyebrow">MUNICIPAL ARCHIVE · INTAKE GATE</p><h1>PageReady <span>Vision</span></h1></div>
      <div className="system-pill"><i /> Deterministic policy online</div>
    </header>

    {!batch ? <section className="landing panel">
      <div className="landing-copy"><p className="eyebrow">OCR PIPELINE PROTECTION</p><h2>Validate the page before it becomes data.</h2><p>OpenCV evidence detects recoverable skew, severe blur, and uncertainty—then records every action before downstream systems run.</p>
        <button className="primary" onClick={loadDemo} disabled={busy || !sessionReady}>{busy ? 'Preparing demo…' : sessionReady ? 'Load 4-Page Municipal Demo Batch' : 'Preparing local session…'} <b>→</b></button></div>
      <label className="dropzone"><input type="file" accept="image/*" onChange={uploadFile} /><strong>Drop a scan or choose a file</strong><span>PNG, JPG, or another browser-supported image</span><em>Local session only · no image data in export</em></label>
    </section> : <section className="console-grid">
      <aside className="queue panel"><div className="panel-heading"><div><p className="eyebrow">BATCH QUEUE</p><h2>{batch.pages.length} pages</h2></div><span>{resolved}/{batch.pages.length} resolved</span></div>
        <div className="queue-list">{batch.pages.map((page, index) => <div key={page.id} className={`queue-wrap ${selected?.id === page.id ? 'selected' : ''}`}><button className="queue-card" onClick={() => setSelectedId(page.id)}>
          <span className="page-index">{String(index + 1).padStart(2, '0')}</span><span className="queue-name"><strong>{page.filename.replace('.png', '')}</strong><small>{page.error?.message ?? page.source}</small></span><span className={`status ${page.error ? 'warning' : statusClass[page.status]}`}>{page.error ? 'Input error' : page.status}</span>
        </button>{page.error && <div className="file-actions"><button onClick={() => removePage(page.id)}>Remove</button><label>Replace<input type="file" accept="image/*" onChange={event => uploadFile(event, page.id)} /></label></div>}</div>)}</div>
        <button className="text-button" onClick={clearQueue}>Clear current queue</button>
      </aside>
      <section className="detail panel">
        {selected && <><div className="panel-heading"><div><p className="eyebrow">PAGE EVIDENCE · {String(selected.queue_index + 1).padStart(2, '0')}</p><h2>{selected.filename}</h2></div><span className={`status ${statusClass[selected.status]}`}>{selected.status}</span></div>
          {selected.warning_reason && <div className="warning-banner">⚠ <span>{selected.warning_reason}</span></div>}
          <div className="evidence-grid"><ImageCard label="ORIGINAL" url={selected.original_image_url} /><ImageCard label="PROCESSED / VERIFIED" url={selected.processed_image_url} empty="No transform was required" /></div>
          <div className="bottom-grid"><MetricCard page={selected} /><TraceCard page={selected} /></div>
          {selected.status === 'Needs review' && <div className="override-card"><div><p className="eyebrow">HUMAN CONTROL</p><strong>Approve Overriding Warning</strong><span>The warning and original evidence stay in the audit trail.</span></div><div className="override-actions"><input value={note} onChange={event => setNote(event.target.value)} placeholder="Required clerk rationale" /><button className="warning-button" onClick={approveWarning} disabled={!note.trim()}>Approve</button></div></div>}
        </>}
      </section>
    </section>}

    {summary && <footer className="summary panel"><div><p className="eyebrow">BATCH COMPLETE</p><strong>{summary}</strong></div><button className="primary" onClick={exportAudit}>Export Audit <b>↓</b></button></footer>}
    {error && <div className="toast" role="alert">{error}<button onClick={() => setError(null)}>×</button></div>}
  </main>
}

function ImageCard({ label, url, empty }: { label: string; url?: string | null; empty?: string }) {
  return <div className="image-card"><p className="eyebrow">{label}</p>{url ? <img src={url} alt={label} /> : <div className="image-empty">{empty ?? 'Waiting for image evidence'}</div>}</div>
}

function MetricCard({ page }: { page: Page }) {
  const metrics = page.metrics
  return <section className="metric-card"><p className="eyebrow">OPENCV SCORECARD</p><div className="metrics"><Metric label="SKEW" value={`${formatMetric(metrics?.skew_angle_deg, 2)}°`} /><Metric label="CONFIDENCE" value={formatMetric(metrics?.skew_confidence, 2)} /><Metric label="BLUR VAR." value={formatMetric(metrics?.blur_laplacian_var)} /><Metric label="CONTRAST" value={formatMetric(metrics?.contrast_std_dev)} /></div><small>{metrics?.content_touches_frame ? 'Frame-edge content detected · review required' : 'Frame-edge content not detected'}</small></section>
}

function Metric({ label, value }: { label: string; value: string }) { return <div><span>{label}</span><strong>{value}</strong></div> }

function TraceCard({ page }: { page: Page }) {
  const runtimeEvent = page.trace.find((event) => event.event_type === 'runtime_provenance')
  const openCvVersion = runtimeEvent?.detail.opencv_version

  return <section className="trace-card"><p className="eyebrow">EXECUTION TRACE</p>{openCvVersion ? <div className="runtime-provenance"><span>OPENCV RUNTIME</span><strong>{String(openCvVersion)}</strong></div> : null}<div className="trace-list">{page.trace.length ? page.trace.map((event, index) => <div className="trace-event" key={event.event_id}><span>{String(index + 1).padStart(2, '0')}</span><div><strong>{event.summary}</strong><small>{event.event_type.replaceAll('_', ' ')} · {event.actor}</small></div></div>) : <div className="trace-empty">Trace will appear after analysis begins.</div>}</div></section>
}
