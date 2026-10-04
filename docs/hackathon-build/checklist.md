# PageReady Vision — Build Checklist

## Build Preferences

- **Build mode:** Autonomous between named inspection milestones.
- **Comprehension checks:** N/A; the participant requested milestone inspection rather than task-by-task instruction.
- **Git:** Commit after each completed milestone with tests passing.
- **Verification:** Yes — pause for participant inspection after Data Engine, API Routes, UI Split-Panel, and Docker Benchmarks.
- **Check-in cadence:** Balanced — report completed evidence and the next milestone at each pause.
- **Time budget:** 35–40 focused hours, targeting an October 25 internal deadline.
- **Submission wow moment:** Split-screen deskew snapping straight while the real-time trace logs the corrective tool call and verification.

## Checklist

- [x] **1. Define domain contracts and deterministic policy**
  Spec ref: `spec.md > 4. Domain Model and State Rules`
  What to build: Add Pydantic/domain models for pages, metrics, trace events, audit export, intake errors, and override requests; centralize the versioned quality thresholds and legal state transitions.
  Acceptance: The seven required workflow statuses are preserved exactly; failed intake remains an error sub-state; an override requires a non-empty note and preserves warning evidence.
  Verify: Run focused Python tests for state transitions and serialization, including illegal override and illegal transition cases.

- [x] **2. Generate deterministic municipal demo fixtures**
  Spec ref: `spec.md > 7. Synthetic Demo Fixture Design`
  What to build: Create fixed-seed, harmless municipal-looking document generator output for clean, recoverably skewed, severely blurred, and low-contrast pages.
  Acceptance: Loading the seeded demo can always create exactly four labeled pages with no sensitive source material; outputs are stable between runs.
  Verify: Run fixture tests that compare stable metadata/checksums and save a local visual sample set for inspection.

- [x] **3. Prove the vision-policy engine end to end**
  Spec ref: `spec.md > 3. Architecture and Data Flow` and `spec.md > 4.3 Deterministic decision policy`
  What to build: Integrate fixtures with the existing OpenCV analyzer and agent; preserve analysis, action selection, deskew, verification, and trace evidence for every outcome.
  Acceptance: Clean is approved; skewed is corrected then verified/approved; severe blur requests rescan; low contrast requires review; failed verification never approves.
  Verify: Run the full golden-path and synthetic-fixture test suite.

### Inspection milestone — Data Engine

Approved: four generated pages, metric outcomes, transition traces, and deskew evidence inspected; `8 passed`. Commit the tested engine milestone before beginning the API milestone.

- [x] **4. Build the ephemeral batch service**
  Spec ref: `spec.md > 4.1 Page model` and `spec.md > 5. API Contract`
  What to build: Implement in-memory batch ownership, ordered sequential processing, image lifetime, selection-ready page data, clear-before-new-batch behavior, and audit assembly.
  Acceptance: A page progresses visibly through the required states; an active batch blocks a new batch; browser/session reset is intentionally ephemeral.
  Verify: Run service tests for queue ordering, duplicate processing prevention, clear behavior, and audit content exclusion.

- [x] **5. Expose the FastAPI contract**
  Spec ref: `spec.md > 5. API Contract`
  What to build: Add typed demo, upload, process, batch-state, override, audit, clear, and image-serving routes with safe validation and client-safe errors.
  Acceptance: The frontend can obtain every item of queue, image, metric, trace, and override data; corrupt/unsupported input stays visible with a readable error; audit JSON contains no image bytes, URLs, or base64 data.
  Verify: Run FastAPI API tests covering happy paths, invalid ids/files, concurrent processing rejection, override validation, and export payload assertions.

### Inspection milestone — API Routes

Approved: scripted API responses verified the four-page demo, review override, intake error state, and image-free audit export; `14 passed`. Commit the tested API milestone before beginning the React console.

- [x] **6. Scaffold the React/Vite technical-ops console**
  Spec ref: `spec.md > 2. Technology Decisions` and `spec.md > 6. Frontend Design and Interaction`
  What to build: Create the TypeScript app, typed API client, shared models, dark slate theme tokens, empty dropzone, demo loader, and active-batch guard.
  Acceptance: First load shows both the empty dropzone and **Load 4-Page Municipal Demo Batch**; a second intake is blocked until clear.
  Verify: Run frontend typecheck/build and manually load the first-run state in a browser.

- [x] **7. Implement the live queue and split-panel evidence view**
  Spec ref: `spec.md > 3. Architecture and Data Flow` and `spec.md > 6. Queue and detail console`
  What to build: Render ordered queue cards, exact statuses, selected-page original/processed images, scorecard, warning reason, and chronological trace with live polling.
  Acceptance: The skewed page visibly progresses through `Analyzing`, `Corrected`, and `Approved`, with its trace showing deskew and verification; rescan and review evidence are equally inspectable.
  Verify: Run the local stack, load the demo, and capture the deskew/trace sequence using browser inspection or an automated UI test.

- [x] **8. Complete review, override, summary, and export controls**
  Spec ref: `spec.md > 4.3 Deterministic decision policy` and `spec.md > 6. Completion and export`
  What to build: Add evidence-led review, required override note, `Approved with warning` transition, truthful live summary, audit download, failed-file Remove/Replace, and clear/reset controls.
  Acceptance: Review shows prior trace and metrics before override; the override retains the warning and appends the clerk note; the seeded unresolved summary reads `2 Approved (1 Auto-Corrected) · 1 Rescan Requested · 1 Needs Review`.
  Verify: Run UI interaction checks for override-note validation, audit download structure, summary behavior before/after override, and reset-to-clean state.

### Inspection milestone — UI Split-Panel

Approved: complete four-page browser flow inspected, including deskew trace, evidence-led review, required-note override, summary, export control, and clean refresh/replay; `15 passed` and production frontend build passed. Commit the tested UI milestone before beginning Docker work.

- [x] **9. Package Docker runtime and benchmark harness**
  Spec ref: `spec.md > 2. Technology Decisions` and `spec.md > 9. Verification Plan`
  What to build: Update the Docker build for the full stack and `linux/arm64` compatibility; add a benchmark script that records environment, fixture set, timings, and baseline comparison fields.
  Acceptance: The documented image builds/runs locally; benchmark output makes no AWS/Graviton result claim unless executed on verified ARM64 Graviton hardware.
  Verify: Build/run the container locally, run the benchmark harness, and inspect its reproducibility metadata and non-claim wording.

### Inspection milestone — Docker Benchmarks

Approved: Docker image `pageready-vision:local` started successfully as `pageready-vision-check` and serves the full-stack console at `http://localhost:8010`; benchmark output records reproducibility metadata and explicit AMD64-local/non-claim wording. Commit the tested packaging milestone before beginning the rehearsal.

- [ ] **10. Rehearse the end-to-end demo and prepare handoff artifacts**
  Spec ref: `spec.md > 10. Implementation Sequence` and `prd.md > Submission Proof Points`
  What to build: Document clean-run commands, execute the complete flow from a fresh local state, capture screenshots and a ≤5-minute video shot list, and prepare repository/testing evidence for Devpost.
  Acceptance: A judge can reproduce the local demo, see all four outcomes, inspect the audit trail, and understand the evidence-gated AWS path without unsupported claims.
  Verify: Follow README instructions from a clean environment; run full backend/frontend tests; complete one recorded dry run using the shot list.

### Devpost handoff

After the build is verified, use `$prepare-submission` to turn the tested project, screenshots, video, benchmark evidence, and reproducibility instructions into the Devpost submission draft.
