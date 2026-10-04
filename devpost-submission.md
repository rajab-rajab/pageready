# PageReady Vision

## One-line Summary

An OpenCV 5 agentic quality gate that prevents poor municipal-document scans from reaching OCR or downstream AI by safely deskewing, requesting rescans, or escalating to a clerk with an auditable trace.

## Problem

Municipal archive teams often receive skewed, blurry, low-contrast, or potentially clipped scans. When those images reach OCR or AI extraction unchallenged, they cause bad data, manual cleanup, and unexplained decisions.

## Solution

PageReady Vision is a browser-based operations console that analyzes each page with OpenCV 5 and applies a fail-safe policy. It auto-corrects only confident, small skew; it requests a rescan for severe blur; and it routes low-confidence, low-contrast, frame-edge, or failed-verification cases to a human. Every action and its evidence are recorded in an image-free audit trail.

## Why This Matters

The project makes automation safer at the point where failures are cheapest to catch: before OCR and downstream AI use an unreliable source image. Clerks get an explainable, controllable decision rather than a black-box acceptance.

## How We Used AI

The runtime agent is deliberately deterministic rather than an LLM. It uses OpenCV 5 perception as tool input in a multi-step loop: analyze, choose, act, re-analyze, then approve or escalate. For the skewed page, the measured angle becomes the deskew-tool parameter; post-correction OpenCV evidence then changes the final decision. This satisfies the Agentic Vision path without representing an AI coding assistant as the product's agent.

## How We Used Codex

Codex helped co-design and implement the typed FastAPI service, React console, deterministic fixtures, evaluation scripts, trace contracts, Docker packaging, and test coverage. Build decisions were evidence-led: a rotated border that triggered the clipping safeguard was retained as a production rule while the recoverable-skew fixture was changed to omit the synthetic border; a faded fixture was tuned only after its original policy route was inspected.

## Key Features

- OpenCV 5 skew, confidence, blur, contrast, and frame-edge evidence.
- Measured-angle deskew followed by independent verification.
- Fail-safe rescan and human-review routing.
- Evidence-first clerk override with a required rationale.
- Split-panel before/after images, metrics, and chronological trace.
- Image-free JSON audit export.
- Deterministic synthetic fixtures, evaluation artifact, and automated tests.

## Architecture

React/Vite console -> FastAPI/Pydantic batch service -> OpenCV 5 `QualityGateAgent` -> policy action/tool -> verification -> trace and audit export. See `docs/technical-report.md` and `docs/agentic-vision-award-evidence.md` for the full architecture and workflow diagrams.

## Testing Instructions

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\evaluate.py --output runs\evaluation.json
```

Expected results: 16 passing tests; `evaluation.json` reports four expected actions, zero task failures, and zero unsafe approvals on the fixed demo set. Run the local console with `uvicorn pageready.api:app --host 127.0.0.1 --port 8000`, then run `npm install` and `npm run dev` in `frontend/`. Load the four-page municipal demo and inspect the skewed-page trace.

## Public Demo Link

http://52.64.48.227

This public Docker service runs on AWS EC2 `t4g.small` (Graviton/ARM64) in
`ap-southeast-2`, with OpenCV 5.0.0 recorded in each page trace. The four-page
demo was verified at this endpoint on October 4, 2026. It is a live demo, not a
production archive deployment.

## Public Repository Link

https://github.com/rajab-rajab/pageready

## Demo Video

Judge-accessible demo video: https://youtu.be/GXOiXvwbG0U

The narrated demonstration is under five minutes and shows the OpenCV 5 runtime proof, agentic workflow diagram, architecture and safety policy, deployed AWS application, and execution trace. The required story is outlined in `docs/demo-rehearsal.md`.

## Screenshot Shot List

Use the existing local localhost captures as candidate assets, then select 3-5 that clearly show: first-run intake, deskew before/after plus trace, rescan and review outcomes, clerk override with note, and image-free audit export. The detailed list is in `docs/demo-rehearsal.md`.

## Submission Readiness Notes

- Selected special award: **Agentic Vision Award**.
- Code archive candidate: `pageready-vision-ae8c20d.zip` (clean source snapshot of the published build).
- Technical report: `docs/technical-report.md`.
- Reproducible evaluation: `runs/evaluation.json` (OpenCV 5.0.0, 4/4 expected actions, zero failures, zero unsafe approvals).
- The live service is verified on AWS Graviton; the local benchmark remains Windows/AMD64 only and does not claim COOL results.

## Known Limitations

This is a four-fixture demonstration, not a production archive service. It has a
live AWS EC2 demo endpoint but no persistent store, user accounts, OCR/LLM
extraction, or COOL-on-Graviton measurement. Frame-edge evidence is an
escalation signal, not proof of physical-document truncation. The planned
150-page holdout evaluation has not yet been executed.

## TODO Official Form Fields

- Special Award Consideration: Agentic Vision Award.
- Repository URL: populated above.
- Testing instructions: populate from the section above.
- Working web endpoint: populate with the public demo link above.
- Video URL: https://youtu.be/GXOiXvwbG0U
