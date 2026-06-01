import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.enumop.metrics import compute_metrics


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary-output", default=None)
    args = parser.parse_args()

    rows = []
    for record in read_jsonl(Path(args.input)):
        text = record.get("output_text", "")
        metrics = compute_metrics(text)
        row = {
            "prompt_id": record.get("prompt_id"),
            "genre": record.get("genre"),
            "condition": record.get("condition"),
            "model": record.get("model"),
            **metrics,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    if not df.empty:
        summary = df.groupby("condition").mean(numeric_only=True).round(4)
        print(summary)
        if args.summary_output:
            summary_output_path = Path(args.summary_output)
            summary_output_path.parent.mkdir(parents=True, exist_ok=True)
            summary.to_csv(summary_output_path)


if __name__ == "__main__":
    main()
