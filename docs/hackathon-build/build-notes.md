# Build Notes

## Onboarding

- Project direction confirmed: municipal-archive document quality gate, not a generic chatbot or thin vision wrapper.
- Golden workflow: inspect -> auto-correct when safe -> verify -> approve; otherwise request rescan or human review and emit a trace.
- Build preference: concise, implementation-oriented planning.
- Visual direction: technical operations console with a split-panel evidence and trace view.
- Agent strategy: deterministic policy first; model-backed fallback after the core safety path is proven.

## Scope

- Time budget: 35-40 focused hours before the October 25 internal deadline.
- Core demo: a four-page municipal scan batch with approved, deskewed, rescan, and human-review outcomes.
- Priority: protect downstream OCR pipelines; OCR/LLM extraction itself is deliberately excluded.
- Primary human control: **Approve Overriding Warning** with a trace entry.
- Explicit cuts: user accounts, archive search, long-term archive management, real production rescan integration, and unverified COOL claims.
- Deepening rounds: 0; participant chose to lock the scope after the mandatory scope interview.

## PRD

- First-run experience: empty dropzone plus **Load 4-Page Municipal Demo Batch**.
- Queue states locked: `Queued`, `Analyzing`, `Corrected`, `Rescan requested`, `Needs review`, `Approved`, `Approved with warning`.
- Review UI requires side-by-side evidence, warning reason, metric scorecard, and prior trace events before the clerk can override.
- Completion summary: `2 Approved (1 Auto-Corrected) · 1 Rescan Requested · 1 Needs Review`; audit export contains metrics, traces, and override notes but no image binary payload.
- Edge behavior: failed files stay in the queue with Remove/Replace; clearing is required before a new batch; browser refresh resets to clean demo state.
- Deepening rounds: 0; participant chose to write the PRD after the mandatory interview.

## Technical Specification

- Stack locked: React/Vite/TypeScript dashboard, FastAPI/Pydantic local API, existing Python 3.12/OpenCV 5 quality-gate core, and in-memory batch state.
- Delivery locked: local full-stack demo and recorded video; Docker is ARM64-compatible for later AWS Graviton benchmarking, not a present cloud-deployment claim.
- Demo inputs: four fixed-seed, locally generated synthetic municipal-looking documents; no sensitive archive data.
- Quality states, error treatment, trace/audit contracts, API boundary, test plan, and risk/non-claim language are defined in `spec.md`.
- Deepening rounds: 0; participant chose to proceed directly after architecture review.

## Build Checklist

- Participant co-designed the checklist and selected autonomous implementation between four inspection milestones: Data Engine, API Routes, UI Split-Panel, and Docker Benchmarks.
- Sequencing decision: synthetic-data/OpenCV engine first, then service/API, then React dashboard, then Docker/benchmark and submission rehearsal.
- Git cadence: commit after each tested milestone.
- Submission wow moment: the split-screen deskew snap paired with real-time corrective-tool and verification trace logging.
- Deepening rounds: 0; participant locked the initial checklist after confirming risk ordering, state contracts, and the October 25/35–40 hour fit.

## Build Execution

- Data Engine work began autonomously: added versioned Pydantic policy/domain contracts, deterministic synthetic municipal fixtures, and trace-event contract coverage.
- Initial skewed fixture correctly triggered frame-edge review because its rotated outer border reached the frame margin. Participant approved the fixture-only correction: omit that border for the recoverable-skew fixture while retaining the production safeguard.
- Verification after the correction: `8 passed` with `python -m pytest -q -p no:cacheprovider`.
- Awaiting participant inspection of the Data Engine evidence sheet before marking items 1–3 complete and committing the milestone.

## API Routes Milestone

- Implemented the ephemeral batch service and typed FastAPI contract for seeded batches, uploads, processing, batch state, clerk overrides, image serving, audit export, and clear operations.
- The first faded fixture made both blur and contrast fail, so policy correctly chose rescan. Participant approved a fixture-only contrast adjustment from 0.18 to 0.35, retaining rescan priority while restoring the intended low-contrast review case.
- Verification after the correction: `14 passed` with `python -m pytest -q -p no:cacheprovider`.
- Awaiting participant API inspection before marking items 4–5 complete and committing the milestone.

## UI Split-Panel Milestone

- Added a manually scaffolded React/Vite/TypeScript operations console after the interactive Vite initializer produced no files.
- Implemented first-run dropzone/demo loader, sequential visual state pacing, queue, side-by-side evidence, scorecard, trace timeline, required-note override, image-free export, clear control, and failed-upload Remove/Replace controls.
- Browser verification exposed and fixed two V1 boundary issues: override responses must retain preloaded evidence URLs, and browser refresh must reset the backend's ephemeral session as well as React state.
- Verification: full Python suite `15 passed`; production frontend build completed; browser flow confirmed the exact seeded summary, review evidence, override gating, and clean refresh/replay behavior.
- Awaiting participant UI inspection before marking items 6–8 complete and committing the milestone.

- UI milestone approved. Accuracy note for submission materials: V1 displays original/processed evidence and chronological trace events, but does not draw defect bounding boxes or expose per-tool latency in the UI; only total backend execution runtime is currently recorded.

## Docker Benchmarks Milestone

- Built the full-stack multi-stage Docker image and added a static-file console route for the packaged frontend.
- Added `scripts/benchmark.py`, which records operating-system, architecture, Python/OpenCV/NumPy versions, fixture outcomes, timing summaries, and an unrecorded comparison placeholder.
- README now documents local development, Docker use, ARM64-compatible build preparation, reproducible benchmarks, and the strict non-claim boundary for AWS Graviton/COOL.
- Participant verified the existing `pageready-vision:local` image running as `pageready-vision-check`, mapped from host port 8010 to container port 8000. The inspected benchmark artifact identified the local environment as Windows/AMD64 and explicitly disclaimed AWS Graviton and COOL results.

## End-to-End Rehearsal and Handoff

- Added `docs/demo-rehearsal.md` with clean-run commands, the complete deterministic four-outcome rehearsal, an image-free audit check, five screenshot targets, a 3:45 video shot list, and a Devpost evidence inventory.
- Actual screenshots and recording remain participant-captured verification artifacts; no captures are represented as complete until inspected by the participant.
