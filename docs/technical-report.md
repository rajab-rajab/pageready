# PageReady Vision: Responsible Document-Quality Automation

## Problem and users

Municipal archive and back-office teams receive document scans that may be skewed, blurred, low-contrast, or clipped at an image edge. Passing those pages directly into OCR or downstream AI systems can create extraction errors, manual rework, and unexplained acceptance decisions. PageReady Vision is a quality gate for archive clerks: it detects observable page-quality risk before downstream processing and either corrects, requests a rescan, or asks for human review.

## OpenCV 5 implementation and agentic workflow

The application runs Python 3.12 with `opencv-python-headless 5.0.0.93`. OpenCV computes a Hough-line skew estimate and confidence, Laplacian-variance blur evidence, grayscale contrast spread, and conservative frame-edge-content evidence. A versioned deterministic policy consumes those measurements.

```text
OpenCV 5 perception -> QualityGateAgent decision -> action tool -> OpenCV 5 verification
       skew, blur,             approve /          deskew,          final approval
       contrast, edge          correct /          rescan, or        or escalation
       evidence                escalate           human review
```

The skewed fixture demonstrates a multi-step perception-decision-action loop: OpenCV 5 detects a confident recoverable skew; the agent passes the measured angle to `auto_correct`; OpenCV 5 re-analyzes the corrected image with `verify_corrected_page`; and post-correction skew evidence determines whether the page is approved or escalated to a clerk.

This is not a chatbot describing a fixed result: the visual measurement changes both the correction tool call and the later outcome. Each trace records the OpenCV version, measurement evidence, selected action, tool calls, verification, and final resolution.

## Architecture

The React/Vite operations console calls a FastAPI service that owns an ephemeral batch. The service invokes the OpenCV 5 `QualityGateAgent`, then returns page metrics, image evidence, and chronological trace events to the console. The export path produces image-free JSON containing metrics, actions, and override notes, but no document bytes or URLs.

The current demo is deployed at `http://52.64.48.227` as a Docker service on an
AWS EC2 `t4g.small` (Graviton/ARM64) instance in `ap-southeast-2`. The deployed
container runs OpenCV 5.0.0 for the core image-analysis workload; the public
four-page demo was checked end to end, including runtime-provenance trace
events. The intended production AWS architecture is raw and processed images in
distinct S3 prefixes, an ARM64 worker on AWS Graviton, trace metadata in
DynamoDB, CloudWatch metrics, and Step Functions routing for rescan and
human-review events. Those production components remain a target, and this
submission makes no COOL execution or benchmark claim.

## Evaluation and results

The reproducible smoke evaluation (`scripts/evaluate.py`) ran on Windows 11 AMD64 using Python 3.12.10 and OpenCV 5.0.0. It evaluated four deterministic, fixed-seed synthetic document fixtures. Results: 4/4 expected actions matched, 0 task failures, and 0 unsafe approvals.

| Fixture | Expected outcome | Observed agent behavior |
| --- | --- | --- |
| Clean permit register | Approve | Approved without a tool call |
| Skewed council minutes | Approve | Measured skew -> deskew -> verification -> approved |
| Blurred property card | Request rescan | Rescan requested; no speculative correction |
| Low-contrast zoning notice | Human review | Sent to review with evidence retained |

The full automated suite also passed: 16 tests, covering fixture determinism, correction and verification, rescan/review routes, corrupt uploads, audit exclusions, session reset, and required override notes. The smoke evaluation is not a production-accuracy claim or a held-out benchmark. The planned 150-page evaluation protocol, including defect-specific precision/recall and unsafe-approval measurement, is in `docs/evaluation.md`.

## User experience and human control

The console presents a live queue and a split evidence panel with original and corrected images, metrics, action reason, and trace. It does not silently correct low-confidence cases. Blur requests a rescan; low contrast, weak skew evidence, frame-edge content, and failed verification route to review. A clerk can approve a reviewed page only after entering a non-empty rationale, and the warning and override remain in the audit trail.

## Reproducibility, security, and responsible operation

All demo documents are deterministic synthetic pages with no real archive data. The project ships source, Docker instructions, a pinned dependency lockfile, automated tests, a benchmark harness, and an evaluation script. Audit exports exclude image payloads. Uploaded invalid images remain visible as safe error items, and local session data is intentionally cleared on refresh.

The source makes no claim that `content_touches_frame` proves physical-document
truncation. It is treated only as an escalation signal. The current V1 has no
user accounts, durable audit store, production rescan integration, or
COOL-on-Graviton measurement; those are explicitly excluded from performance
claims. The AWS EC2 service is a verified demonstration endpoint, not a
production archive deployment.

## Limitations and next steps

The current application is a four-fixture demonstration rather than a
production archive system. It does not run OCR or LLM extraction, and its
deterministic deskew policy is limited to validated small rotations. Next steps
are a held-out synthetic evaluation, role-based clerk identity, persistent
audits, and a verified COOL baseline comparison on the deployed AWS Graviton
runtime.
