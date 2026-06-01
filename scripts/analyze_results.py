import argparse
import json
from pathlib import Path

import pandas as pd

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


if __name__ == "__main__":
    main()
