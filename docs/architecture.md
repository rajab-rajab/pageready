# PageReady Vision Architecture

## Deployed system

PageReady Vision is deployed as one public Docker web application on AWS EC2.
The service runs on a `t4g.small` Graviton/ARM64 instance in
`ap-southeast-2` and is reachable through the persistent Elastic IP
[`http://52.64.48.227`](http://52.64.48.227).

```text
Browser
  |
  | HTTP :80
  v
AWS Elastic IP 52.64.48.227
  |
  v
EC2 t4g.small (Graviton / ARM64)
  |
  v
Docker: PageReady Vision
  |
  +-- React/Vite operations console
  |
  +-- FastAPI batch API
  |
  +-- QualityGateAgent
  |     |
  |     +-- OpenCV 5 perception and verification
  |
  +-- Ephemeral in-memory demo batch and image-free audit export
```

The deployed Docker image contains the built React console and the Python
FastAPI application. Docker maps public port `80` to application port `8000`.
There is no separate frontend host, database, queue, S3 bucket, or Lambda
component in the current competition demo.

## Agentic Vision runtime flow

`QualityGateAgent` is the runtime agent. Codex assisted with development, but
is not part of the running document-processing path.

```text
Input page
  -> OpenCV 5 analysis
       skew angle + confidence
       blur variance
       contrast spread
       frame-edge evidence
  -> QualityGateAgent decision/orchestration
  -> action tool
       auto_correct(angle)
       request_rescan()
       send_to_human_review()
  -> OpenCV 5 verification when corrected
  -> approved, rescan requested, or human review
  -> chronological audit trace
```

The skewed-page route is the key multi-step agentic loop: measured OpenCV
evidence supplies the deskew angle, `auto_correct` uses that value, and a
second OpenCV analysis determines whether the page can be approved. Visual
evidence therefore changes both the tool call and the final outcome.

## Decision and safety policy

| Observed evidence | Agent action | Final control |
| --- | --- | --- |
| Clean, sufficient-quality page | Approve | No correction is applied. |
| Confident, small recoverable skew | `auto_correct` then `verify_corrected_page` | Approve only after verification succeeds. |
| Severe blur | `request_rescan` | No speculative correction or approval. |
| Low contrast, weak evidence, frame-edge content, or failed verification | `send_to_human_review` | Clerk must provide a non-empty rationale to approve with warning. |

`content_touches_frame` is an escalation signal only; it is not treated as
proof that a physical document is truncated. Audit exports intentionally omit
image bytes, image URLs, and base64 payloads.

## Observability and evaluation

Every page records ordered trace events such as input receipt, OpenCV runtime
provenance, evidence collection, selected action, tool invocation, correction
verification, human-review request, and final resolution. The deterministic
four-fixture evaluation covers a clean approval, verified deskew approval,
rescan failure handling, and human-review escalation. Its current result is
four expected outcomes out of four with zero unsafe approvals.

## Scope and next steps

The current deployment is intentionally a stateless public demo: browser
refreshes clear its batch data and no durable customer-document storage exists.
If the project moves beyond the competition demo, the next architecture would
separate raw and processed documents in S3, persist audit metadata in DynamoDB,
add CloudWatch metrics and alarms, and use a durable workflow for rescan and
review tasks. Those components are future work, not part of the deployed
system or a COOL claim.
