"""Small local CLI for the golden path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from .agent import QualityGateAgent


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PageReady Vision on one image.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = parser.parse_args()

    image = cv2.imread(str(args.image), cv2.IMREAD_COLOR)
    if image is None:
        parser.error(f"Cannot read image: {args.image}")

    output, trace = QualityGateAgent().process(image, document_id=args.image.stem)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.output_dir / f"{args.image.stem}-processed.png"), output)
    (args.output_dir / f"{args.image.stem}-trace.json").write_text(
        json.dumps(trace, indent=2), encoding="utf-8"
    )
    print(json.dumps({"action": trace["selected_action"], "trace_id": trace["trace_id"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
