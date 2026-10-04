# PageReady Vision — Technical Specification

## 1. Purpose and V1 Boundary

PageReady Vision is a local, full-stack document-quality gate for municipal archive intake. It prevents low-quality scans from entering downstream OCR or LLM pipelines by using OpenCV evidence to either correct a safely recoverable skew, request a rescan, or route the page to a clerk for review.

V1 is a deterministic, four-page demonstration. It does not perform OCR, content extraction, accounts, archive search, durable records management, production rescan notifications, real DynamoDB persistence, or model-backed decision-making. Browser refresh intentionally clears all batch data.

## 2. Technology Decisions

| Area | Choice | Reason |
| --- | --- | --- |
| Vision runtime | Python 3.12, OpenCV 5, NumPy | Existing tested evidence and deskew implementation. |
| API | FastAPI + Pydantic | Typed local JSON API and simple testability. |
| Frontend | React, Vite, TypeScript | Responsive split-panel console and explicit UI state. |
| Styling | CSS variables + component CSS | Delivers the dark technical-ops visual system without a large design dependency. |
| State | In-memory FastAPI batch store | Matches the explicit reset-on-refresh V1 boundary. |
| Demo documents | Locally generated synthetic municipal-looking pages | Safe, deterministic, repeatable, and free of sensitive records. |
| Packaging | Docker multi-stage build, compatible with `linux/arm64` | Creates a reproducible path for later AWS Graviton benchmarking. |

The local app is the submission runtime. Docker/ARM64 is a reproducibility and benchmark path, not evidence that the product has run on AWS Graviton until a real benchmark is recorded.

## 3. Architecture and Data Flow

```text
React/Vite console
  ├─ load demo / upload files / select page / submit override
  └─ polls batch state while sequential processing is active
                    │ JSON over localhost
                    ▼
FastAPI service
  ├─ validates image inputs and owns ephemeral batch state
  ├─ generates deterministic demo pages
  ├─ invokes QualityGateAgent per page
  └─ serializes metrics, trace, and audit export
                    │
                    ▼
OpenCV QualityGateAgent
  analyze → deterministic plan → correction or escalation
          → verification after correction → trace event append
```

Processing is sequential so the console can make the deskew moment legible: `Queued` → `Analyzing` → `Corrected` → `Approved`. A small frontend delay may pace presentation only; it must not alter OpenCV results or policy decisions.

## 4. Domain Model and State Rules

### 4.1 Page model

Each `PageJob` has:

- `id`, `filename`, `source` (`demo` or `upload`), and monotonically increasing `queue_index`.
- `status`: exactly one of `Queued`, `Analyzing`, `Corrected`, `Rescan requested`, `Needs review`, `Approved`, or `Approved with warning`.
- `error`: nullable object containing `code` and human-readable `message` for a failed/corrupt upload. Error is an intake sub-state, not an eighth quality status.
- `original_image_url` and nullable `processed_image_url`; images are served only within the active local session and never embedded in audit JSON.
- `metrics`, `warning_reason`, `trace`, nullable `override_note`, and timestamps.

### 4.2 Metrics and evidence

`QualityMetrics` records width, height, estimated skew angle, skew confidence, Laplacian blur score, contrast standard deviation, and `content_touches_frame`.

`content_touches_frame` is only evidence that detected content reaches an image border. It must not be represented as proof that a physical original document was truncated.

### 4.3 Deterministic decision policy

Policy thresholds are centralized in a versioned `QualityPolicy` object. They are not hidden in frontend code.

1. Severe blur routes to `Rescan requested`; no automatic correction is attempted.
2. Evidence of content touching the frame, weak correction confidence, or low contrast routes to `Needs review`.
3. A sufficiently confident recoverable skew triggers deskew. The system records `Corrected`, re-analyzes the output, then marks `Approved` only if verification passes.
4. A clean page moves directly to `Approved`.
5. A failed verification routes to `Needs review`, preserving both before/after evidence.
6. A clerk may select **Approve Overriding Warning** only from `Needs review`, with a non-empty note. The final state is `Approved with warning`; the warning and prior evidence remain visible.

### 4.4 Trace and audit contract

Every `TraceEvent` contains a stable event id, UTC timestamp, event type, actor (`system` or `clerk`), policy/pipeline version, a human-readable summary, and structured evidence/action detail. Required events include:

- input received;
- image analyzed;
- deterministic action selected;
- deskew tool invoked and completed, where applicable;
- post-correction verification;
- rescan/review decision; and
- clerk override and note, where applicable.

`AuditExport` includes batch metadata, policy/pipeline versions, page outcomes, metrics, warning reasons, trace events, and override notes. It explicitly excludes raw image bytes, base64 content, and image URLs.

## 5. API Contract

| Endpoint | Intent |
| --- | --- |
| `POST /api/batches/demo` | Create exactly four generated municipal demo pages; reject if an active queue exists. |
| `POST /api/batches/upload` | Validate supported image files and add queue items or visible intake errors. |
| `POST /api/batches/{batch_id}/process` | Begin sequential processing; reject duplicate concurrent processing. |
| `GET /api/batches/{batch_id}` | Return queue, selected-page-ready evidence, summary, and completion state. |
| `POST /api/pages/{page_id}/approve-warning` | Validate review state and non-empty note; append clerk trace event. |
| `GET /api/batches/{batch_id}/audit` | Return/download the image-free audit JSON. |
| `DELETE /api/batches/{batch_id}` | Clear the current queue before another batch can start. |
| `GET /api/images/{image_id}` | Serve active-session original or processed PNG for the evidence panel. |

The service validates all externally supplied ids, files, and override notes. API failures use a typed error response with a message suitable for the console; raw exceptions and filesystem paths are never returned to the browser.

## 6. Frontend Design and Interaction

The React dashboard uses an obsidian/dark-slate surface, indigo for active analysis, emerald for approved/corrected outcomes, and amber for warnings, rescans, and review.

### First run

- Show an empty dropzone and **Load 4-Page Municipal Demo Batch** together.
- Disable additional intake while a queue exists and guide the clerk to clear it first.

### Queue and detail console

- Left panel: ordered queue cards, exact status labels, progress, failed-intake error cards, and Remove/Replace controls.
- Right panel: selected-page header, side-by-side original and processed images, warning reason, metric scorecard, and chronological trace.
- During deskew, the right panel visibly updates from original evidence to corrected result while the trace adds the deskew tool and verification events.
- Review displays all prior evidence before enabling **Approve Overriding Warning** and requires an explanation field.

### Completion and export

For the seeded demo, display exactly: `2 Approved (1 Auto-Corrected) · 1 Rescan Requested · 1 Needs Review` with **Export Audit**. If the clerk overrides the review page, update the live count/status honestly rather than retaining the pre-override text as a current result.

## 7. Synthetic Demo Fixture Design

The generator draws a municipal-style header, seal-like geometric mark, form fields, lines, stamps, and harmless fake identifiers. It uses a fixed seed and fixed dimensions. Four named pages are generated:

1. `permit-register-clean.png`: clean and directly approved.
2. `council-minutes-skewed.png`: recoverable rotation; corrected, verified, then approved.
3. `property-card-blurred.png`: deliberately severe blur; rescan requested.
4. `zoning-notice-low-contrast.png`: contrast reduced to force review; no automatic approval.

Fixtures must remain content-free and deterministic. Tests assert their intended policy outcome rather than relying on visual inspection alone.

## 8. Repository Structure

```text
frontend/
  src/api/                 typed API client
  src/components/          queue, evidence panel, scorecard, trace, controls
  src/types/               API-aligned TypeScript types
  src/styles/              theme tokens and component styles
src/pageready/
  analysis.py              existing OpenCV evidence collection
  agent.py                 existing deterministic perception-decision-action loop
  api.py                   FastAPI application and routes
  schemas.py               Pydantic request/response/domain types
  service.py               batch orchestration and ephemeral store
  demo.py                  deterministic synthetic document generator
  policy.py                versioned thresholds and decision policy
tests/
  test_golden_path.py      existing computer-vision checks
  test_demo.py             fixture determinism and intended outcomes
  test_service.py          transitions, trace integrity, audit exclusions
  test_api.py              endpoint validation and export behavior
scripts/
  benchmark.py             repeatable architecture/timing benchmark capture
Dockerfile                 local full-stack and linux/arm64-compatible runtime
```

## 9. Verification Plan

- Retain and run existing golden-path OpenCV tests for rotation, blur, and escalation.
- Add unit tests for every legal and illegal state transition, including blocked override without a note and failed correction verification.
- Add API tests for corrupt inputs, active-batch rejection, clear-before-new-batch behavior, and absence of image payloads/URLs from export JSON.
- Add frontend interaction checks for seeded batch loading, live selected-page update, evidence-led review, override, and audit download.
- Run the full stack locally from a clean environment and record the exact commands in the README.
- Build and run the Docker image locally. For an actual Graviton claim, run the same pinned image on AWS ARM64/Graviton, record machine architecture, CPU/OS, image digest, OpenCV version, fixture set, run count, median/p95 timing, and baseline comparison. Until then, describe this only as ARM64-compatible packaging and a planned benchmark.

## 10. Implementation Sequence

1. Introduce Pydantic schemas, policy configuration, synthetic generator, and service tests while preserving current CV tests.
2. Add FastAPI batch, processing, override, audit, and image-serving routes with API tests.
3. Scaffold React/Vite dashboard and connect typed client to seeded demo flow.
4. Build queue, evidence, scorecard, trace, review override, clear, and export interactions.
5. Add Docker full-stack runtime and benchmark capture script.
6. Run end-to-end verification, gather screenshots/video, and prepare submission evidence.

## 11. Risks and Non-Claims

- Synthetic documents validate the demo path; they are not a claim of production accuracy on all archive media.
- Hough-line deskew can fail on sparse or unusual layouts; uncertainty must route to review, not approval.
- The UI must distinguish quality evidence from physical-document conclusions and avoid claiming certain truncation detection.
- No persistent database or authenticated identity exists in V1; audit export is a demonstration artifact, not a durable municipal record.
- No COOL eligibility, AWS deployment, or Graviton performance claim is made before measured evidence exists.
