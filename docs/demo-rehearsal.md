# PageReady Vision — Demo Rehearsal and Submission Evidence

This rehearsal uses only deterministic synthetic municipal-style documents. It
demonstrates a quality gate before OCR or downstream LLM processing. The live
demo runs at `http://52.64.48.227` on AWS Graviton/ARM64 with OpenCV 5.0.0, but
it does not claim production archival accuracy, COOL execution, performance
benchmarks, or persistent audit storage.

## Clean-run commands

From the repository root in WSL or Ubuntu:

```bash
docker build -t pageready-vision:local .
docker run --rm --name pageready-vision -p 8010:8000 pageready-vision:local
```

Open `http://localhost:8010`. Stop the container with `Ctrl+C` after the rehearsal.

For development and test evidence on Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm run build
```

For a local benchmark artifact (not an AWS result):

```powershell
.\.venv\Scripts\python.exe scripts\benchmark.py --runs 20 --output runs\benchmark.json
```

The benchmark JSON must identify its host architecture and retain its `claim_guardrail`. A Windows/AMD64 artifact is local evidence only.

## Four-outcome rehearsal

1. Begin in a fresh browser session and select **Load 4-Page Municipal Demo Batch**.
2. Let the queue complete. Confirm the exact unresolved summary: `2 Approved (1 Auto-Corrected) · 1 Rescan Requested · 1 Needs Review`.
3. Select the skewed council-minutes page. Show its original and straightened evidence side-by-side, then its trace entries for analysis, deskew, and verification.
4. Select the severely blurred property-card page. Show that it requests a rescan rather than silently approving or correcting it.
5. Select the low-contrast zoning notice. Show the metric evidence and the required non-empty clerk note. Attempting an empty note must not approve the page.
6. Add a concise override note and approve with warning. Confirm that the warning remains visible and the trace has an override event.
7. Download the audit export. Confirm it contains page states, metrics, trace, and note metadata, but no image bytes, URLs, or base64 payload.
8. Use **Clear** and refresh the browser. Confirm the console returns to its clean first-run state; reload the deterministic demo once if a reset proof is needed.

## Screenshot checklist

Capture PNG screenshots at these moments; use these filenames in a `docs/screenshots/` folder when available:

1. `01-first-run.png` — clean drop zone and **Load 4-Page Municipal Demo Batch** button.
2. `02-deskew-evidence.png` — skewed page selected with before/after evidence, scorecard, and corrective/verification trace.
3. `03-rescan-review.png` — rescan and needs-review queue states visible together.
4. `04-override-audit.png` — evidence-led override note and resulting **Approved with warning** trace/summary.
5. `05-audit-export.png` — downloaded audit JSON opened just far enough to show metadata and no image payload.

Do not upload images to Devpost during this rehearsal. They are inputs to `$prepare-submission`, after the project feels ready.

## Video shot list (target: 3 minutes 45 seconds)

| Time | Shot | Narration proof point |
| --- | --- | --- |
| 0:00–0:20 | First-run state | PageReady Vision gates document quality before OCR/LLM work. |
| 0:20–0:30 | Deployment and architecture | Show the AWS public endpoint and explain: OpenCV 5 perception → QualityGateAgent decision → action tool → OpenCV 5 verification. |
| 0:30–0:50 | Load deterministic batch | Four controlled pages produce distinct, explainable outcomes. |
| 0:50–1:35 | Skewed council minutes | A small recoverable skew is corrected, then independently verified before approval. |
| 1:35–2:05 | Blurred property card | Severe blur fails safely to **Rescan requested**; no speculative correction. |
| 2:05–2:50 | Low-contrast zoning notice | Evidence and trace appear before a clerk can approve with warning. |
| 2:50–3:20 | Override and audit export | A required note creates an auditable, image-free decision trail. |
| 3:20–3:45 | Reproducibility/non-claim close | The live AWS Graviton service runs OpenCV 5; no COOL runtime or benchmark is claimed. |

## Devpost handoff inventory

- Repository: source, Dockerfile, README, deterministic fixtures, test suite, benchmark harness.
- Screenshots: five captures from the checklist above.
- Video: a public ≤5-minute recording following the shot list.
- Benchmark: `runs/benchmark.json`, labeled with its actual environment and non-claim guardrail.
- Submission facts: verified local behavior and a live AWS Graviton OpenCV 5 demo; no production-accuracy, COOL, or performance claims.
