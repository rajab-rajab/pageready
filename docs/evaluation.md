# Evaluation Protocol

## Dataset split

Use 150 non-sensitive, synthetic pages with a checked-in manifest:

* 50 calibration pages: threshold tuning only.
* 100 holdout pages: do not inspect when changing thresholds or policy.

Each manifest entry records its source template, corruption seed, intended defect labels, expected policy action, and SHA-256 checksum.

## Metrics

Report results per defect type and severity, not only as a single aggregate:

* precision and recall for blur, frame-edge-content, and low-contrast escalation;
* skew absolute error over the validated small-rotation range;
* correction verification success rate;
* unsafe approval count (must be zero in the holdout set);
* latency, throughput, and measured AWS cost.

## Benchmarking rule

Measure vanilla OpenCV and COOL on the same AWS Graviton deployment configuration and the same fixed inputs. Report the runtime version, instance type, image dimensions, iterations, warm-up procedure, and raw measurements. Never infer COOL performance from an x86-versus-Arm comparison.

PS C:\\Users\\RAJAB BAIG\\Documents\\GitHub\\BAIG\\PageReady-Vision> .\\.venv\\Scripts\\python.exe scripts\\evaluate.py --output runs\\evaluation.json

{

&nbsp; "schema\_version": "1.0",

&nbsp; "generated\_at\_utc": "2026-10-04T16:22:14.911725+00:00",

&nbsp; "scope": "Deterministic four-fixture smoke evaluation; not a holdout or production-accuracy result.",

&nbsp; "environment": {

&nbsp;   "platform": "Windows-11-10.0.22631-SP0",

&nbsp;   "machine": "AMD64",

&nbsp;   "python": "3.12.10",

&nbsp;   "opencv": "5.0.0"

&nbsp; },

&nbsp; "summary": {

&nbsp;   "fixtures": 4,

&nbsp;   "task\_successes": 4,

&nbsp;   "task\_failures": 0,

&nbsp;   "failure\_fixture\_names": \[],

&nbsp;   "unsafe\_approvals": 0,

&nbsp;   "unsafe\_approval\_fixture\_names": \[],

&nbsp;   "outcomes": {

&nbsp;     "approve": 2,

&nbsp;     "request\_rescan": 1,

&nbsp;     "send\_to\_human\_review": 1

&nbsp;   }

&nbsp; },

&nbsp; "fixtures": \[

&nbsp;   {

&nbsp;     "fixture": "permit-register-clean.png",

&nbsp;     "expected\_status": "Approved",

&nbsp;     "expected\_action": "approve",

&nbsp;     "observed\_action": "approve",

&nbsp;     "matched\_expected\_action": true,

&nbsp;     "tool\_sequence": \[],

&nbsp;     "trace\_event\_types": \[

&nbsp;       "input\_received",

&nbsp;       "runtime\_provenance",

&nbsp;       "image\_analyzed",

&nbsp;       "action\_selected",

&nbsp;       "outcome\_resolved"

&nbsp;     ]

&nbsp;   },

&nbsp;   {

&nbsp;     "fixture": "council-minutes-skewed.png",

&nbsp;     "expected\_status": "Approved",

&nbsp;     "expected\_action": "approve",

&nbsp;     "observed\_action": "approve",

&nbsp;     "matched\_expected\_action": true,

&nbsp;     "tool\_sequence": \[

&nbsp;       "auto\_correct",

&nbsp;       "verify\_corrected\_page"

&nbsp;     ],

&nbsp;     "trace\_event\_types": \[

&nbsp;       "input\_received",

&nbsp;       "runtime\_provenance",

&nbsp;       "image\_analyzed",

&nbsp;       "action\_selected",

&nbsp;       "tool\_invoked",

&nbsp;       "correction\_verified",

&nbsp;       "outcome\_resolved"

&nbsp;     ]

&nbsp;   },

&nbsp;   {

&nbsp;     "fixture": "property-card-blurred.png",

&nbsp;     "expected\_status": "Rescan requested",

&nbsp;     "expected\_action": "request\_rescan",

&nbsp;     "observed\_action": "request\_rescan",

&nbsp;     "matched\_expected\_action": true,

&nbsp;     "tool\_sequence": \[

&nbsp;       "request\_rescan"

&nbsp;     ],

&nbsp;     "trace\_event\_types": \[

&nbsp;       "input\_received",

&nbsp;       "runtime\_provenance",

&nbsp;       "image\_analyzed",

&nbsp;       "action\_selected",

&nbsp;       "rescan\_requested",

&nbsp;       "outcome\_resolved"

&nbsp;     ]

&nbsp;   },

&nbsp;   {

&nbsp;     "fixture": "zoning-notice-low-contrast.png",

&nbsp;     "expected\_status": "Needs review",

&nbsp;     "expected\_action": "send\_to\_human\_review",

&nbsp;     "observed\_action": "send\_to\_human\_review",

&nbsp;     "matched\_expected\_action": true,

&nbsp;     "tool\_sequence": \[

&nbsp;       "send\_to\_human\_review"

&nbsp;     ],

&nbsp;     "trace\_event\_types": \[

&nbsp;       "input\_received",

&nbsp;       "runtime\_provenance",

&nbsp;       "image\_analyzed",

&nbsp;       "action\_selected",

&nbsp;       "human\_review\_requested",

&nbsp;       "outcome\_resolved"

&nbsp;     ]

&nbsp;   }

&nbsp; ]

}

