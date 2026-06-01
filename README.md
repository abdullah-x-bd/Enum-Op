# Enumerative Overproduction in ChatGPT Writing

This repository contains the experimental code, prompt bank, annotation materials, and analysis scripts for a small empirical paper on enumerative overproduction in ChatGPT writing.

The paper studies a simple but stubborn writing problem. ChatGPT often turns prose into inventory. Even when a user asks for normal paragraphs and explicitly bans lists, the model may still produce list-like sentences inside the paragraph. The visible list disappears, but the checklist structure remains.

## Research aim

The study asks whether anti-list prompting reduces enumerative writing, or whether it mainly changes the surface form of enumeration.

The main comparison is between three prompt conditions.

1. Control prompts that ask for long-form writing without special style restrictions.
2. Anti-list prompts that ban bullet points, numbered lists, and list-like writing.
3. Strong anti-list prompts that also ban long comma chains, stacked examples, repeated category clusters, and paragraph-level inventory writing.

## Core hypothesis

The expected finding is not that ChatGPT ignores the instruction completely. It may obey the surface instruction by removing bullets and numbered lists.

The stronger claim is that hidden enumeration may remain. The model may replace obvious lists with comma chains, example chains, question chains, contrast pairs, or abstract noun clusters inside paragraph prose.

## Main metrics

The repository tracks both visible and hidden enumeration.

Visible enumeration includes bullet points, numbered lists, line-broken lists, and semicolon-separated list structures.

Hidden enumeration includes paragraph-internal list structures. These are sentences that pack multiple categories, examples, qualities, effects, or questions into one sequence.

The initial metrics are:

- surface_list_rate_per_1000_words
- enumerative_sentence_rate
- enumerative_paragraph_rate
- mean_list_span
- trigger_phrase_rate_per_1000_words
- substitution_score

The substitution score is the most important early metric. It measures cases where surface list markers fall but hidden enumeration remains high.

## Repository structure

```text
.
├── configs/
│   └── experiment.example.yaml
├── data/
│   ├── processed/
│   └── raw/
├── docs/
│   └── annotation_codebook.md
├── prompts/
│   └── prompt_bank.jsonl
├── results/
├── scripts/
│   ├── analyze_results.py
│   └── run_openai_experiment.py
├── src/
│   └── enumop/
│       ├── __init__.py
│       └── metrics.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Quick start

Install the Python dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy the example config.

```bash
cp configs/experiment.example.yaml configs/experiment.local.yaml
```

Add an OpenAI API key as an environment variable.

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Run a small pilot.

```bash
python scripts/run_openai_experiment.py --config configs/experiment.local.yaml --limit 3
```

Analyze the generated output.

```bash
python scripts/analyze_results.py --input data/raw/openai_outputs.jsonl --output results/metrics_summary.csv
```

## Experimental notes

The main experiment should keep the model, temperature, top_p, maximum output length, system prompt, and prompt bank fixed inside each run.

The first paper version should use temperature 0 for the main results. A smaller robustness run can use a higher temperature to see whether enumeration becomes more pronounced under normal creative generation settings.

Every output should store the model name, prompt ID, condition, timestamp, input prompt, output text, and available API metadata.

## Current status

This is the initial scaffold. The next work is to expand the prompt bank, run a pilot experiment, refine the regex metrics, and add a manual annotation sample.

## License

A license should be added before public release or paper submission.