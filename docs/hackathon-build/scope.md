# Project Scope

## Project Name Candidates

- PageReady Vision (selected)

## One-Line Summary

PageReady Vision is a technical operations console that protects municipal archive OCR pipelines by using OpenCV 5 evidence to correct, rescan, or escalate poor-quality document scans before downstream processing.

## Target User

Municipal archive and back-office clerks who receive batches of scanned records and need to stop low-quality pages before they create OCR or LLM failures.

## Problem

Archive intake workflows often pass rotated, blurry, low-contrast, or potentially clipped scans into downstream OCR. The result is incorrect extraction, expensive manual cleanup, and no clear audit trail explaining why a page was accepted.

## Core Workflow

1. A clerk drops a batch of four municipal scans into the console.
2. The console displays a live per-page queue while OpenCV 5 collects skew, blur, contrast, and frame-edge evidence.
3. A deterministic tool-calling agent chooses one safe outcome per page:
   - auto-correct and verify recoverable rotation/skew;
   - request a rescan for severe blur or likely clipping;
   - send low-confidence or low-contrast pages to human review.
4. The split-panel dashboard shows the original and processed image, metrics, selected action, and append-only trace.
5. In the review state, the clerk can select **Approve Overriding Warning**; that decision is recorded with the evidence and rationale.

## What We Are Building

- A local technical operations console with obsidian/dark-slate styling and indigo, emerald, and amber status accents.
- A four-page batch queue with live per-page status transitions.
- OpenCV 5 visual evidence collection and safe rotation/skew correction with post-correction verification.
- Deterministic agent policy and trace contract; model-backed fallback is designed as a later integration, not a critical V1 dependency.
- A transparent split-panel view inspired by Vercel/Supabase: image evidence beside metrics, tool calls, and human controls.
- Local audit records structured for later DynamoDB persistence.
- Synthetic municipal-archive fixtures and automated tests for the golden perception -> decision -> action -> verification path.

## What We Are Not Building

- OCR, LLM extraction, or downstream content interpretation. PageReady protects those systems; it does not replace them.
- User accounts, permissions, or multi-user tenancy.
- Archive search, long-term document management, or records-retention workflows.
- Real production rescan integrations; V1 will demonstrate a queued rescan event.
- A production-grade document-boundary detector or automatic treatment of uncertain frame-edge content as proven truncation.
- COOL performance claims until COOL runs and is benchmarked on AWS Graviton.

## Inspiration And References

- Archive intake and intelligent-document-processing workflows, focused on preventing poor inputs rather than extracting text.
- Vercel/Supabase split-panel observability dashboards for the evidence and trace presentation.
- OpenCV 5 and the hackathon's Agentic Vision path: vision evidence must change a later tool call or human-control request.

## Demo Path

1. Start a seeded batch of four synthetic municipal scans.
2. Show the clean page approved, the skewed page corrected and re-verified, the severely blurred page routed to a rescan event, and the low-contrast page opened for review.
3. Use **Approve Overriding Warning** on the review page and show the append-only trace update.
4. Open the trace panel to prove that OpenCV 5 evidence changed the agent's later action for every page.

## Submission Story

PageReady Vision makes document automation safer by placing a transparent, controllable quality gate before OCR or LLM processing. Its judge demo focuses on an observable perception-decision-action loop, responsible human override, reproducible tests, and a clear path to AWS Graviton/Cool validation without overstating unbuilt infrastructure.
