# Product Requirements Document

## Product Summary

PageReady Vision is a browser-based technical operations console for municipal archive intake. It gives a clerk a visible, controlled quality gate before documents reach OCR or LLM systems. The demo uses a four-page municipal batch and makes every page outcome—approval, auto-correction, rescan, or review—easy to inspect and audit.

## Target User

Municipal archive and back-office clerks who need to make fast, accountable decisions about incoming document scans without interpreting the documents' content.

## Core User Journey

1. On first open, the clerk sees an empty dropzone and a **Load 4-Page Municipal Demo Batch** button.
2. The clerk loads the demo or adds a supported document batch. Each page appears in the batch queue as `Queued`.
3. Each queue card moves visibly through `Analyzing` and then into one of the resolved states: `Corrected`, `Rescan requested`, `Needs review`, `Approved`, or `Approved with warning`.
4. Selecting a queue item opens the split-panel console: original/processed image evidence beside the scorecard and chronological trace.
5. For a skewed page, the clerk sees the document deskew in real time while the trace records the corrective tool call and verification outcome.
6. For a review page, the clerk sees side-by-side images, warning reason, metric scorecard, and prior trace events before choosing **Approve Overriding Warning**.
7. When the batch completes, the console reports `2 Approved (1 Auto-Corrected) · 1 Rescan Requested · 1 Needs Review` and offers **Export Audit**.
8. The clerk may clear the current queue before loading a new batch. A browser refresh returns the app to its clean demo state.

## Epics And User Stories

### Epic 1: Start and manage a document batch

- As an archive clerk, I want to start with either an empty dropzone or a prepared municipal demo batch so that I can immediately understand how the console works.
- As an archive clerk, I want each file represented in a live queue so that I can see what is happening to every page.
- As an archive clerk, I want a failed upload to remain visible with a useful message and **Remove**/**Replace** controls so that I can correct the intake problem without losing context.

Acceptance criteria:

- First open shows both an empty dropzone and **Load 4-Page Municipal Demo Batch**.
- Loading the demo adds exactly four clearly labeled items to the queue.
- The queue uses exactly these statuses: `Queued`, `Analyzing`, `Corrected`, `Rescan requested`, `Needs review`, `Approved`, `Approved with warning`.
- Unsupported or corrupt input becomes a failed queue item with a readable error and **Remove** and **Replace** controls.
- The clerk must clear the current queue before starting a new batch.

### Epic 2: Observe automated quality decisions

- As an archive clerk, I want to see page evidence and the selected quality outcome so that I can trust that poor scans will not silently enter OCR.
- As an archive clerk, I want to see an auto-corrected skewed page become straight beside its original so that I can verify the automation at a glance.

Acceptance criteria:

- Selecting a page shows a side-by-side image view, metric scorecard, current status, and chronological trace.
- A skewed demo page visibly moves through `Analyzing` -> `Corrected` -> `Approved` after verification.
- The trace identifies the evidence, selected action, action result, and verification result.
- A severe blur outcome visibly becomes `Rescan requested` and records why no automatic correction was attempted.
- A low-contrast or uncertain page visibly becomes `Needs review`; the application must not silently approve it.

### Epic 3: Make a responsible human override

- As an archive clerk, I want to approve a reviewed page despite a warning when I have inspected the evidence, so that exceptional but usable records can continue.

Acceptance criteria:

- The review panel displays the original image, any processed image, warning reason, metric scorecard, and prior trace events before the override control is available.
- Selecting **Approve Overriding Warning** changes the item to `Approved with warning`.
- The trace adds the clerk override action and an override note.
- The interface never presents the override as an automatic correction or removes the original warning evidence.

### Epic 4: Finish and export an audit trail

- As an archive clerk, I want a concise end-of-batch summary and evidence-only audit export so that I can communicate what happened without exposing document payloads.

Acceptance criteria:

- Once all pages resolve, the console shows `2 Approved (1 Auto-Corrected) · 1 Rescan Requested · 1 Needs Review` for the seeded demo batch.
- **Export Audit** downloads JSON containing batch/page outcomes, metrics, trace events, and clerk override notes.
- The export contains no raw document-image binary payload.
- Refreshing the browser resets the demonstration to its clean start state and does not claim long-term persistence.

## Edge Cases

- An unsupported or corrupt file stays visible as a failed queue item until the clerk removes or replaces it.
- A low-confidence correction verification routes the page to `Needs review`, never `Approved`.
- Trying to add files to an active demo batch prompts the clerk to clear the current queue first.
- Audit export remains available after the batch completes, including reviewed and overridden outcomes.
- A browser refresh intentionally clears the queue and audit state; this is a V1 demo boundary, not data loss in a production archive product.

## What We Are Building

- Local desktop/browser demo console with an obsidian dark-slate visual system and indigo, emerald, and amber state accents.
- Four-page seeded municipal batch plus supported upload/drop interaction.
- Live queue, split-panel evidence view, metrics, agent trace, safe review override, completion summary, and audit JSON export.
- Observable OpenCV 5 perception-decision-action loop with deterministic policy and visible verification.

## What We Would Add With More Time

- OCR and LLM handoff after quality approval.
- User accounts, clerk identity, role permissions, and persistent audit storage.
- Archive search, long-term records management, and production rescan-notification integrations.
- Real AWS DynamoDB persistence, real AWS Graviton deployment, and a verified COOL benchmark.
- Model-backed agent fallback after its safety and observability contract is separately tested.

## Submission Proof Points

- A real-time before/after deskew moment paired with a tool-call trace.
- All four quality outcomes in one short, controlled municipal-archive scenario.
- The human override is evidence-led and auditable, demonstrating appropriate autonomy rather than blind automation.
- Automated golden-path tests and synthetic fixtures substantiate the technical claims.
- Audit export makes the system's decision trail judge-accessible without requiring raw document data.
