# PageReady Vision — 54-Second Demo Voiceover

PageReady Vision is a document-quality gate for municipal archives. Before OCR or an LLM processes a scan, it checks whether the page is reliable enough to continue.

Here, we load a deterministic four-page demo batch. A clean permit register is approved immediately. The council-minutes page has a small recoverable skew, so PageReady selects a deskew tool, verifies the corrected result, and only then approves it.

The blurred property card fails safely to a rescan request. The low-contrast zoning notice is sent to human review, where the clerk sees the metrics and complete decision trace before approving with a required note.

Every decision is exportable as an image-free audit trail. This Docker package is ARM64-compatible; AWS Graviton and COOL performance claims wait for measured AWS evidence.
