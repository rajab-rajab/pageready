# PageReady Vision

PageReady Vision is an agentic document-quality gate. It inspects an uploaded page, uses OpenCV evidence to choose a corrective or escalation tool, verifies any correction, and emits an auditable trace.

## Runtime flow

`QualityGateAgent → OpenCV analysis → action tool → OpenCV verification`

`QualityGateAgent` is the runtime agent in this application. It uses OpenCV
for vision analysis and correction; it is not OpenCV itself. Its action tools
are `auto_correct`, `verify_corrected_page`, `request_rescan`, and
`send_to_human_review`. Codex was used to help develop the project, not as the
runtime agent that processes documents.

## Golden path

1. Analyze a document's visual evidence.
2. If the page has a confident, recoverable small skew, call `auto_correct`.
3. Re-analyze the corrected output with `verify_corrected_page`.
4. Approve only when verification succeeds; otherwise route it to human review.

The first milestone deliberately limits automatic correction to small skew. Blur, content near a frame edge, low contrast, conflicting evidence, and failed correction are fail-safe routes to human review or rescan.

## Local development

Use a working Python 3.11+ installation, then install the package and tests:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

Run an image through the local golden path:

```powershell
.\.venv\Scripts\python.exe -m pageready.cli analyze .\example.png --output-dir .\runs
```

Create an award-evidence smoke evaluation (the JSON includes the exact OpenCV
runtime, expected and observed decisions, tool sequences, and safety counts):

```powershell
.\.venv\Scripts\python.exe scripts\evaluate.py --output runs\evaluation.json
```

See `docs/agentic-vision-award-evidence.md` for the workflow diagram and the
submission capture checklist.

Run the local full-stack console in two terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn pageready.api:app --host 127.0.0.1 --port 8000
```

```powershell
Set-Location frontend
npm install
npm run dev
```

The Vite development server proxies `/api` to FastAPI. The local session resets on browser refresh by design.

## Docker and benchmark evidence

Build and run the full-stack container locally:

```powershell
docker build -t pageready-vision:local .
docker run --rm -p 8000:8000 pageready-vision:local
```

Build an ARM64-compatible image when preparing an AWS Graviton run:

```powershell
docker buildx build --platform linux/arm64 -t pageready-vision:arm64 --load .
```

Capture a local benchmark artifact:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark.py --runs 20 --output runs\benchmark.json
```

The resulting JSON documents operating-system, architecture, Python/OpenCV versions, fixture outcomes, median/p95 timing, and a comparison placeholder. It is **not** AWS Graviton or COOL evidence unless the same command runs on documented AWS ARM64/Graviton hardware with the intended runtime.

## Public AWS deployment

PageReady Vision is fully deployed as a public Docker web application on AWS
EC2 `t4g.small` (Graviton/ARM64) in `ap-southeast-2`.

- **Live application:** [http://52.64.48.227](http://52.64.48.227)
- **Persistent Elastic IP:** `52.64.48.227`
- **Runtime:** OpenCV 5.0.0, FastAPI, and the built React console in Docker

The Elastic IP remains available through EC2 stop/start cycles while it stays
allocated to this AWS account. The public service has been verified with the
four-page quality-gate demo. This is runtime-deployment evidence, not a COOL
claim: no COOL runtime or Graviton performance benchmark has been measured.
Do not label a local development wheel, an ARM64-compatible container, or a
local benchmark as COOL.
