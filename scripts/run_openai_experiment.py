import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml
from openai import OpenAI
from tqdm import tqdm


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def build_user_prompt(base_prompt: str, condition_instruction: str) -> str:
    if not condition_instruction.strip():
        return base_prompt
    return f"{base_prompt}\n\nStyle instruction:\n{condition_instruction.strip()}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt_file = Path(config["prompt_file"])
    output_file = Path(config["output_file"])
    output_file.parent.mkdir(parents=True, exist_ok=True)

    prompts = list(read_jsonl(prompt_file))
    if args.limit is not None:
        prompts = prompts[: args.limit]

    conditions = config["conditions"]
    model = config["model"]

    with output_file.open("a", encoding="utf-8") as out:
        for prompt_record in tqdm(prompts):
            for condition_name, condition in conditions.items():
                user_prompt = build_user_prompt(
                    prompt_record["base_prompt"],
                    condition.get("instruction", ""),
                )

                response = client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": config.get("system_prompt", "")},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=config.get("temperature", 0),
                    top_p=config.get("top_p", 1),
                    max_output_tokens=config.get("max_output_tokens", 1800),
                )

                record = {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "experiment_name": config.get("experiment_name"),
                    "provider": config.get("provider", "openai"),
                    "model": model,
                    "temperature": config.get("temperature", 0),
                    "top_p": config.get("top_p", 1),
                    "prompt_id": prompt_record["prompt_id"],
                    "genre": prompt_record.get("genre"),
                    "condition": condition_name,
                    "base_prompt": prompt_record["base_prompt"],
                    "condition_instruction": condition.get("instruction", ""),
                    "full_prompt": user_prompt,
                    "output_text": response.output_text,
                    "response_id": response.id,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()


if __name__ == "__main__":
    main()
